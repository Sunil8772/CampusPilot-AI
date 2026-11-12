import json
from datetime import time
from database.db import get_cursor
from services.permissions import require_role
from services.audit import log_action
from services.common import result

DAY_MAP = {"monday":0,"tuesday":1,"wednesday":2,"thursday":3,
           "friday":4,"saturday":5,"sunday":6}

def _value(row,*keys,default=None):
    for key in keys:
        if key in row and row[key] not in (None,""):
            return row[key]
    return default

def import_timetable_records(records,program,semester,academic_year,uploaded_by,
                             source_filename=None):
    require_role(uploaded_by,["admin"])
    if not records:
        return result(False,"No timetable records supplied.")
    clean,errors = [],[]
    for index,row in enumerate(records,start=1):
        try:
            day = str(_value(row,"Day","day","day_of_week",default="")).strip().lower()
            if day not in DAY_MAP:
                raise ValueError("invalid Day")
            start = time.fromisoformat(str(_value(row,"Start Time","start_time")))
            end = time.fromisoformat(str(_value(row,"End Time","end_time")))
            room = _value(row,"Room","room_name","room")
            if not room:
                raise ValueError("Room is required")
            if end <= start:
                raise ValueError("End Time must be after Start Time")
            clean.append({
                "program":str(_value(row,"Program","program",default=program)),
                "semester":int(_value(row,"Semester","semester",default=semester)),
                "section":_value(row,"Section","section"),
                "day_of_week":DAY_MAP[day],"start_time":start,"end_time":end,
                "subject":_value(row,"Subject","subject"),
                "faculty":_value(row,"Faculty","faculty"),
                "room_name":str(room).strip(),
                "course_code":_value(row,"Course Code","course_code"),
                "class_type":_value(row,"Class Type","class_type"),
                "batch":_value(row,"Batch","batch"),
                "source_data":row,
            })
        except Exception as exc:
            errors.append({"row":index,"error":str(exc)})
    if errors:
        return result(False,"Timetable validation failed; no rows were imported.",
                      errors=errors,imported_count=0)
    with get_cursor() as cur:
        cur.execute(
            """INSERT INTO timetable_imports(uploaded_by,program,semester,academic_year,
                                             source_filename,status)
               VALUES (%s,%s,%s,%s,%s,'draft') RETURNING id""",
            (uploaded_by,program,int(semester),academic_year,source_filename))
        import_id = cur.fetchone()["id"]
        cur.execute(
            "INSERT INTO timetable_versions(import_id,version_number) VALUES (%s,1) RETURNING id",
            (import_id,))
        version_id = cur.fetchone()["id"]
        for row in clean:
            cur.execute(
                """INSERT INTO timetable_entries(version_id,program,semester,section,day_of_week,
                   start_time,end_time,subject,faculty,room_name,course_code,class_type,batch,source_data)
                   VALUES (%(version_id)s,%(program)s,%(semester)s,%(section)s,%(day_of_week)s,
                   %(start_time)s,%(end_time)s,%(subject)s,%(faculty)s,%(room_name)s,
                   %(course_code)s,%(class_type)s,%(batch)s,%(source_data)s::jsonb)""",
                {**row,"version_id":version_id,
                 "source_data":json.dumps(row["source_data"],default=str)})
        log_action(uploaded_by,"timetable_imported","timetable_import",import_id,
                   {"rows":len(clean),"program":program,"semester":semester},cur)
    return result(True,"Timetable saved as a draft.",import_id=import_id,
                  version_id=version_id,imported_count=len(clean))

def publish_timetable(import_id,admin_id):
    require_role(admin_id,["admin"])
    with get_cursor() as cur:
        cur.execute("SELECT * FROM timetable_imports WHERE id=%s FOR UPDATE",(import_id,))
        imported = cur.fetchone()
        if not imported:
            return result(False,"Timetable import not found.")
        cur.execute(
            """UPDATE timetable_imports SET status='archived'
               WHERE program=%s AND semester=%s AND academic_year=%s
                 AND status='published' AND id<>%s""",
            (imported["program"],imported["semester"],imported["academic_year"],import_id))
        cur.execute(
            """UPDATE timetable_versions SET is_published=FALSE
               WHERE import_id IN (SELECT id FROM timetable_imports
                 WHERE program=%s AND semester=%s AND academic_year=%s)""",
            (imported["program"],imported["semester"],imported["academic_year"]))
        cur.execute("UPDATE timetable_versions SET is_published=TRUE WHERE import_id=%s RETURNING id",
                    (import_id,))
        version = cur.fetchone()
        if not version:
            return result(False,"No timetable version exists for this import.")
        cur.execute("UPDATE timetable_imports SET status='published',published_at=NOW() WHERE id=%s",
                    (import_id,))
        log_action(admin_id,"timetable_published","timetable_import",import_id,
                   {"version_id":version["id"]},cur)
    return result(True,"Timetable published.",import_id=import_id,version_id=version["id"])

def get_published_timetable(program,semester,academic_year):
    with get_cursor() as cur:
        cur.execute(
            """SELECT te.* FROM timetable_entries te
               JOIN timetable_versions tv ON tv.id=te.version_id
               JOIN timetable_imports ti ON ti.id=tv.import_id
               WHERE ti.program=%s AND ti.semester=%s AND ti.academic_year=%s
                 AND tv.is_published=TRUE
               ORDER BY te.day_of_week,te.start_time,te.room_name""",
            (program,semester,academic_year))
        return cur.fetchall()
