import json

def log_action(actor_id, action, entity_type, entity_id=None, details=None, cur=None):
    payload = json.dumps(details or {}, default=str)
    if cur is not None:
        cur.execute(
            """INSERT INTO audit_logs(actor_id,action,entity_type,entity_id,details)
               VALUES (%s,%s,%s,%s,%s::jsonb)""",
            (actor_id, action, entity_type, entity_id, payload),
        )
        return
    from database.db import get_cursor
    with get_cursor() as db:
        db.execute(
            """INSERT INTO audit_logs(actor_id,action,entity_type,entity_id,details)
               VALUES (%s,%s,%s,%s,%s::jsonb)""",
            (actor_id, action, entity_type, entity_id, payload),
        )
