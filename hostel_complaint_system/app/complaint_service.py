import uuid
import os
from datetime import datetime
from database.models import get_connection
from app.auth import get_current_user, is_active_student

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf"}
DUPLICATE_THRESHOLD = 3  # same category complaints before notice


def _generate_complaint_id() -> str:
    return "CMP-" + str(uuid.uuid4())[:8].upper()


def _validate_photo(photo_path: str) -> dict:
    if not photo_path:
        return {"valid": True}  # photo is optional
    ext = os.path.splitext(photo_path)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return {"valid": False, "message": f"Invalid file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}
    return {"valid": True}


def register_complaint(category: str, description: str, photo_path: str = "",
                        agreed: bool = False) -> dict:
    """
    UC-02 Register Complaint use-case logic.

    Preconditions (checked here):
      - User must be logged in with valid credentials
      - User must be an active student (not past student)

    Returns {'success': True, 'complaint_id': str} or {'success': False, 'message': str}
    """
    # --- Precondition 1: logged-in check ---
    if not is_active_student():
        user = get_current_user()
        if user is None:
            return {"success": False, "message": "Access denied: you must be logged in."}
        if user["role"] != "student":
            return {"success": False, "message": "Access denied: only students can register complaints."}
        # inactive student
        return {"success": False, "message": "Access denied: you are not an active student."}

    # --- Field validations ---
    if not category or category.strip() == "":
        return {"success": False, "message": "Please select a complaint category."}

    if not description or description.strip() == "":
        return {"success": False, "message": "Description is required."}

    # --- Agreement checkbox ---
    if not agreed:
        return {"success": False, "message": "You must accept the agreement before submitting."}

    # --- Photo validation ---
    photo_check = _validate_photo(photo_path)
    if not photo_check["valid"]:
        return {"success": False, "message": photo_check["message"]}

    user = get_current_user()

    # --- Duplicate / mass-complaint check ---
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM complaints WHERE user_id = ? AND category = ?",
        (user["user_id"], category)
    ).fetchone()[0]

    if count >= DUPLICATE_THRESHOLD:
        conn.close()
        return {
            "success": False,
            "message": (
                f"Too many same complaints in category '{category}'. "
                "A notice will be sent to the college instead of registering another complaint."
            )
        }

    complaint_id = _generate_complaint_id()
    conn.execute(
        "INSERT INTO complaints (complaint_id, user_id, category, description, photo_path, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (complaint_id, user["user_id"], category.strip(), description.strip(),
         photo_path.strip() if photo_path else "", datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

    return {"success": True, "complaint_id": complaint_id}


def check_complaint_status(complaint_id: str) -> dict:
    """Returns complaint details or error."""
    if not complaint_id or complaint_id.strip() == "":
        return {"success": False, "message": "Complaint ID is required."}

    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM complaints WHERE complaint_id = ?", (complaint_id.strip(),)
    ).fetchone()
    conn.close()

    if row is None:
        return {"success": False, "message": f"No complaint found with ID '{complaint_id}'."}

    return {"success": True, "complaint": dict(row)}


def get_all_complaints() -> list:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM complaints ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]