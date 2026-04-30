from database.models import get_connection

_current_user = None


def login(user_id: str, password: str) -> dict:
    """
    Returns {'success': True, 'user': Row} or {'success': False, 'message': str}
    """
    if not user_id or not password:
        return {"success": False, "message": "User ID and password are required."}

    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE user_id = ? AND password = ?", (user_id, password)
    ).fetchone()
    conn.close()

    if row is None:
        return {"success": False, "message": "Invalid credentials. Please try again."}

    global _current_user
    _current_user = dict(row)
    return {"success": True, "user": _current_user}


def logout():
    global _current_user
    _current_user = None


def get_current_user():
    return _current_user


def is_logged_in() -> bool:
    return _current_user is not None


def is_active_student() -> bool:
    u = _current_user
    return u is not None and u["role"] == "student" and u["is_active"] == 1