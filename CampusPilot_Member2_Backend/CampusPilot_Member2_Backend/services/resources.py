from database.db import get_cursor
from services.permissions import require_role
from services.audit import log_action
from services.common import result, parse_datetime

def add_resource(resource_code, name, resource_type, capacity=1, location=None,
                 equipment=None, notes=None, actor_id=None):
    require_role(actor_id, ["admin"])
    allowed = ("classroom","lab","amphitheatre","guest_house","parking")
    if resource_type not in allowed:
        raise ValueError("Unsupported resource_type.")
    if int(capacity) < 1:
        raise ValueError("capacity must be at least 1")
    with get_cursor() as cur:
        cur.execute(
            """INSERT INTO resources(resource_code,name,resource_type,capacity,location,equipment,notes)
               VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING *""",
            (resource_code,name,resource_type,int(capacity),location,equipment or [],notes),
        )
        row = cur.fetchone()
        log_action(actor_id,"resource_created","resource",row["id"],
                   {"resource_code":resource_code},cur)
    return result(True,"Resource created.",resource=row)

def get_resources(resource_type=None, include_inactive=False):
    sql = "SELECT * FROM resources WHERE (%s IS NULL OR resource_type=%s)"
    params = [resource_type,resource_type]
    if not include_inactive:
        sql += " AND is_active=TRUE"
    sql += " ORDER BY resource_type,name"
    with get_cursor() as cur:
        cur.execute(sql,params)
        return cur.fetchall()

def update_resource(resource_id, actor_id, **changes):
    require_role(actor_id,["admin"])
    allowed = {"name","resource_type","capacity","location","equipment","is_active","notes"}
    values = {k:v for k,v in changes.items() if k in allowed}
    if not values:
        return result(False,"No valid resource fields supplied.")
    if "resource_type" in values and values["resource_type"] not in (
        "classroom","lab","amphitheatre","guest_house","parking"
    ):
        raise ValueError("Unsupported resource_type.")
    if "capacity" in values and int(values["capacity"]) < 1:
        raise ValueError("capacity must be at least 1")
    assignments = ", ".join(f"{key}=%s" for key in values)
    with get_cursor() as cur:
        cur.execute(f"UPDATE resources SET {assignments} WHERE id=%s RETURNING *",
                    list(values.values())+[resource_id])
        row = cur.fetchone()
        if not row:
            return result(False,"Resource not found.")
        log_action(actor_id,"resource_updated","resource",resource_id,values,cur)
    return result(True,"Resource updated.",resource=row)

def add_resource_block(resource_id,start_datetime,end_datetime,reason,actor_id):
    require_role(actor_id,["admin"])
    start_dt,end_dt = parse_datetime(start_datetime),parse_datetime(end_datetime)
    if end_dt <= start_dt:
        raise ValueError("end_datetime must be after start_datetime")
    with get_cursor() as cur:
        cur.execute(
            """INSERT INTO room_blocks(resource_id,start_datetime,end_datetime,reason,created_by)
               VALUES (%s,%s,%s,%s,%s) RETURNING *""",
            (resource_id,start_dt,end_dt,reason,actor_id),
        )
        block = cur.fetchone()
        log_action(actor_id,"resource_blocked","room_block",block["id"],
                   {"resource_id":resource_id,"reason":reason},cur)
    return result(True,"Resource block added.",block=block)
