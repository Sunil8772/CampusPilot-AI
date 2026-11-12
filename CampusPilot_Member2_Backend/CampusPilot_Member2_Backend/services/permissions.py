from database.db import get_cursor

def get_user(user_id):
    with get_cursor() as cur:
        cur.execute(
            "SELECT id,external_id,full_name,email,role,is_active FROM users WHERE id=%s",
            (user_id,),
        )
        return cur.fetchone()

def require_role(user_id, allowed_roles):
    user = get_user(user_id)
    if not user or not user["is_active"]:
        raise PermissionError("User does not exist or is inactive.")
    if user["role"] not in allowed_roles:
        raise PermissionError("You do not have permission for this action.")
    return user

def upsert_user(external_id, full_name, email, role):
    if role not in ("student","faculty","admin"):
        raise ValueError("role must be student, faculty or admin")
    with get_cursor() as cur:
        cur.execute(
            """INSERT INTO users(external_id,full_name,email,role)
               VALUES (%s,%s,%s,%s)
               ON CONFLICT(email) DO UPDATE SET
                 external_id=EXCLUDED.external_id, full_name=EXCLUDED.full_name,
                 role=EXCLUDED.role, is_active=TRUE
               RETURNING id,external_id,full_name,email,role""",
            (external_id,full_name,email,role),
        )
        return cur.fetchone()
