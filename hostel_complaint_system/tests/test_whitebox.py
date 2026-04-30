#!/usr/bin/env python3
"""
White-Box Test Suite — UC-02 Register Complaint
Coverage: branch, path, and condition testing of complaint_service.py
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database.models import init_db, get_connection
from app import auth, complaint_service


def reset_db():
    conn = get_connection()
    conn.executescript("""
        DELETE FROM complaints;
        DELETE FROM users;
        INSERT INTO users VALUES ('S001', 'pass123', 'Alice Student', 'student', 1);
        INSERT INTO users VALUES ('S002', 'pass456', 'Bob Student',   'student', 0);
        INSERT INTO users VALUES ('M001', 'mgr789', 'Carol Manager', 'complaint_manager', 1);
    """)
    conn.commit()
    conn.close()
    auth.logout()


class TestWhiteBox(unittest.TestCase):

    def setUp(self):
        init_db()
        reset_db()

    # ── Branch: not logged in ────────────────────────────────────────────────
    def test_WB01_not_logged_in_branch(self):
        """is_active_student() → False (None user) → early return"""
        result = complaint_service.register_complaint("Maintenance", "x", agreed=True)
        self.assertFalse(result["success"])
        self.assertIn("logged in", result["message"])
        print("WB01 PASS – Branch: not logged in")

    # ── Branch: manager tries to complain ────────────────────────────────────
    def test_WB02_manager_role_branch(self):
        """role != 'student' branch"""
        auth.login("M001", "mgr789")
        result = complaint_service.register_complaint("Maintenance", "x", agreed=True)
        self.assertFalse(result["success"])
        self.assertIn("only students", result["message"])
        print("WB02 PASS – Branch: manager role denied")

    # ── Branch: inactive student ──────────────────────────────────────────────
    def test_WB03_inactive_student_branch(self):
        """is_active == 0 branch"""
        auth.login("S002", "pass456")
        result = complaint_service.register_complaint("Maintenance", "x", agreed=True)
        self.assertFalse(result["success"])
        self.assertIn("not an active student", result["message"])
        print("WB03 PASS – Branch: inactive student")

    # ── Branch: empty category ────────────────────────────────────────────────
    def test_WB04_empty_category_branch(self):
        auth.login("S001", "pass123")
        result = complaint_service.register_complaint("", "desc", agreed=True)
        self.assertFalse(result["success"])
        print("WB04 PASS – Branch: empty category")

    # ── Branch: whitespace-only description ───────────────────────────────────
    def test_WB05_whitespace_description_branch(self):
        auth.login("S001", "pass123")
        result = complaint_service.register_complaint("Maintenance", "   \t\n", agreed=True)
        self.assertFalse(result["success"])
        print("WB05 PASS – Branch: whitespace description")

    # ── Branch: agreement False ───────────────────────────────────────────────
    def test_WB06_agreement_false_branch(self):
        auth.login("S001", "pass123")
        result = complaint_service.register_complaint("Maintenance", "desc", agreed=False)
        self.assertFalse(result["success"])
        print("WB06 PASS – Branch: agreement not accepted")

    # ── Branch: invalid photo extension ──────────────────────────────────────
    def test_WB07_invalid_photo_extension(self):
        auth.login("S001", "pass123")
        for bad_ext in [".exe", ".sh", ".docx", ".mp4"]:
            result = complaint_service.register_complaint(
                "Maintenance", "desc", photo_path=f"file{bad_ext}", agreed=True
            )
            self.assertFalse(result["success"], f"Should reject {bad_ext}")
        print("WB07 PASS – Branch: multiple invalid extensions rejected")

    # ── Branch: valid photo extensions ───────────────────────────────────────
    def test_WB08_valid_photo_extensions(self):
        auth.login("S001", "pass123")
        for ext in [".jpg", ".jpeg", ".png", ".gif", ".pdf"]:
            reset_db()
            auth.login("S001", "pass123")
            result = complaint_service.register_complaint(
                "Other", "desc", photo_path=f"file{ext}", agreed=True
            )
            self.assertTrue(result["success"], f"Should accept {ext}")
        print("WB08 PASS – Branch: all valid extensions accepted")

    # ── Branch: no photo (optional) ───────────────────────────────────────────
    def test_WB09_no_photo_optional(self):
        auth.login("S001", "pass123")
        result = complaint_service.register_complaint(
            "Security", "Broken lock", photo_path="", agreed=True
        )
        self.assertTrue(result["success"])
        print("WB09 PASS – Branch: photo is optional")

    # ── Branch: duplicate below threshold ────────────────────────────────────
    def test_WB10_duplicate_below_threshold(self):
        auth.login("S001", "pass123")
        threshold = complaint_service.DUPLICATE_THRESHOLD
        for i in range(threshold - 1):
            r = complaint_service.register_complaint(
                "Cleanliness", f"Issue {i}", agreed=True
            )
            self.assertTrue(r["success"])
        print(f"WB10 PASS – Branch: {threshold-1} complaints allowed (below threshold)")

    # ── Branch: duplicate AT threshold → notice ───────────────────────────────
    def test_WB11_duplicate_at_threshold(self):
        auth.login("S001", "pass123")
        threshold = complaint_service.DUPLICATE_THRESHOLD
        for _ in range(threshold):
            complaint_service.register_complaint("Internet", "No Wi-Fi", agreed=True)
        result = complaint_service.register_complaint("Internet", "No Wi-Fi", agreed=True)
        self.assertFalse(result["success"])
        self.assertIn("notice", result["message"])
        print("WB11 PASS – Branch: duplicate AT threshold triggers notice")

    # ── Path: full happy path ─────────────────────────────────────────────────
    def test_WB12_full_happy_path(self):
        """End-to-end: login → register → check status"""
        auth.login("S001", "pass123")
        reg = complaint_service.register_complaint(
            "Mess / Food", "Cold food served", photo_path="food.jpg", agreed=True
        )
        self.assertTrue(reg["success"])
        cid = reg["complaint_id"]
        self.assertTrue(cid.startswith("CMP-"))

        status = complaint_service.check_complaint_status(cid)
        self.assertTrue(status["success"])
        self.assertEqual(status["complaint"]["status"], "Pending")
        print(f"WB12 PASS – Full happy path, complaint {cid} status=Pending")

    # ── Condition: complaint_id empty string ──────────────────────────────────
    def test_WB13_check_status_empty_id(self):
        result = complaint_service.check_complaint_status("")
        self.assertFalse(result["success"])
        self.assertIn("required", result["message"])
        print("WB13 PASS – Condition: empty complaint ID rejected")

    # ── Condition: complaint_id whitespace ────────────────────────────────────
    def test_WB14_check_status_whitespace_id(self):
        result = complaint_service.check_complaint_status("   ")
        self.assertFalse(result["success"])
        print("WB14 PASS – Condition: whitespace complaint ID rejected")

    # ── Condition: login empty fields ─────────────────────────────────────────
    def test_WB15_login_empty_fields(self):
        r1 = auth.login("", "pass123")
        self.assertFalse(r1["success"])
        r2 = auth.login("S001", "")
        self.assertFalse(r2["success"])
        print("WB15 PASS – Condition: login with empty fields rejected")


if __name__ == "__main__":
    print("=" * 60)
    print("  WHITE-BOX TEST SUITE — UC-02 Register Complaint")
    print("=" * 60)
    loader = unittest.TestLoader()
    loader.sortTestMethodsUsing = None
    suite = loader.loadTestsFromTestCase(TestWhiteBox)
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    print(f"\n  Result: {passed}/{result.testsRun} tests passed")