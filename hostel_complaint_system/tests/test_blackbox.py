#!/usr/bin/env python3
"""
Black-Box Test Suite — UC-02 Register Complaint
Matches test cases from Complaint_TestCases_Updated.xlsx
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database.models import init_db, get_connection
from app import auth, complaint_service


def reset_db():
    """Wipe and reinitialise the in-memory-style DB between test runs."""
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


class TestRegisterComplaint(unittest.TestCase):

    def setUp(self):
        init_db()
        reset_db()

    # ── TC01: Login with valid credentials ──────────────────────────────────
    def test_TC01_login_valid(self):
        result = auth.login("S001", "pass123")
        self.assertTrue(result["success"], "TC01 FAIL")
        self.assertEqual(result["user"]["name"], "Alice Student")
        print("TC01 PASS – Login with valid credentials")

    # ── TC02: Login with invalid credentials ────────────────────────────────
    def test_TC02_login_invalid(self):
        result = auth.login("S001", "wrongpass")
        self.assertFalse(result["success"], "TC02 FAIL")
        self.assertIn("Invalid", result["message"])
        print("TC02 PASS – Login with invalid credentials")

    # ── TC03: Access complaint form as active student ────────────────────────
    def test_TC03_active_student_access(self):
        auth.login("S001", "pass123")
        self.assertTrue(auth.is_active_student(), "TC03 FAIL")
        print("TC03 PASS – Active student can access complaint form")

    # ── TC04: Access complaint form as inactive student ──────────────────────
    def test_TC04_inactive_student_access(self):
        auth.login("S002", "pass456")
        result = complaint_service.register_complaint(
            "Maintenance", "Broken door", agreed=True
        )
        self.assertFalse(result["success"], "TC04 FAIL")
        self.assertIn("not an active student", result["message"])
        print("TC04 PASS – Inactive student denied access")

    # ── TC05: Submit complaint with all valid fields ──────────────────────────
    def test_TC05_valid_complaint(self):
        auth.login("S001", "pass123")
        result = complaint_service.register_complaint(
            "Maintenance", "Broken window in room 101", agreed=True
        )
        self.assertTrue(result["success"], "TC05 FAIL")
        self.assertIn("complaint_id", result)
        print(f"TC05 PASS – Complaint registered: {result['complaint_id']}")

    # ── TC06: Submit with missing fields (empty description) ──────────────────
    def test_TC06_missing_description(self):
        auth.login("S001", "pass123")
        result = complaint_service.register_complaint(
            "Mess / Food", "", agreed=True
        )
        self.assertFalse(result["success"], "TC06 FAIL")
        self.assertIn("Description", result["message"])
        print("TC06 PASS – Missing description caught")

    # ── TC07: Submit without agreement checkbox ──────────────────────────────
    def test_TC07_no_agreement(self):
        auth.login("S001", "pass123")
        result = complaint_service.register_complaint(
            "Security", "Broken gate", agreed=False
        )
        self.assertFalse(result["success"], "TC07 FAIL")
        self.assertIn("agreement", result["message"])
        print("TC07 PASS – Agreement not accepted caught")

    # ── TC08: Upload valid photo attachment ───────────────────────────────────
    def test_TC08_valid_photo(self):
        auth.login("S001", "pass123")
        result = complaint_service.register_complaint(
            "Cleanliness", "Dirty bathroom", photo_path="photo.jpg", agreed=True
        )
        self.assertTrue(result["success"], "TC08 FAIL")
        print(f"TC08 PASS – Valid photo accepted: {result['complaint_id']}")

    # ── TC09: Upload invalid file type ────────────────────────────────────────
    def test_TC09_invalid_file_type(self):
        auth.login("S001", "pass123")
        result = complaint_service.register_complaint(
            "Internet", "No Wi-Fi", photo_path="virus.exe", agreed=True
        )
        self.assertFalse(result["success"], "TC09 FAIL")
        self.assertIn("Invalid file type", result["message"])
        print("TC09 PASS – Invalid file type rejected")

    # ── TC10: Check complaint status with valid ID ────────────────────────────
    def test_TC10_check_status_valid(self):
        auth.login("S001", "pass123")
        reg = complaint_service.register_complaint(
            "Other", "Random issue", agreed=True
        )
        cid = reg["complaint_id"]
        result = complaint_service.check_complaint_status(cid)
        self.assertTrue(result["success"], "TC10 FAIL")
        self.assertEqual(result["complaint"]["complaint_id"], cid)
        print(f"TC10 PASS – Status found: {result['complaint']['status']}")

    # ── TC11: Check complaint status with invalid ID ──────────────────────────
    def test_TC11_check_status_invalid(self):
        result = complaint_service.check_complaint_status("INVALID-ID-9999")
        self.assertFalse(result["success"], "TC11 FAIL")
        self.assertIn("No complaint found", result["message"])
        print("TC11 PASS – Invalid complaint ID caught")

    # ── TC12: Submit with empty description field ─────────────────────────────
    def test_TC12_empty_description(self):
        auth.login("S001", "pass123")
        result = complaint_service.register_complaint(
            "Maintenance", "   ", agreed=True
        )
        self.assertFalse(result["success"], "TC12 FAIL")
        self.assertIn("Description", result["message"])
        print("TC12 PASS – Empty description (whitespace) caught")

    # ── TC13: Submit without selecting complaint category ─────────────────────
    def test_TC13_no_category(self):
        auth.login("S001", "pass123")
        result = complaint_service.register_complaint(
            "", "Some issue", agreed=True
        )
        self.assertFalse(result["success"], "TC13 FAIL")
        self.assertIn("category", result["message"])
        print("TC13 PASS – Empty category caught")

    # ── TC14: Session timeout simulation ──────────────────────────────────────
    def test_TC14_session_timeout(self):
        auth.login("S001", "pass123")
        auth.logout()  # simulate session expiry
        result = complaint_service.register_complaint(
            "Maintenance", "Broken fan", agreed=True
        )
        self.assertFalse(result["success"], "TC14 FAIL")
        self.assertIn("logged in", result["message"])
        print("TC14 PASS – Session timeout / logged out state caught")

    # ── TC15: Multiple same complaints trigger notice ─────────────────────────
    def test_TC15_duplicate_complaints(self):
        auth.login("S001", "pass123")
        for _ in range(complaint_service.DUPLICATE_THRESHOLD):
            complaint_service.register_complaint(
                "Mess / Food", "Same issue again", agreed=True
            )
        result = complaint_service.register_complaint(
            "Mess / Food", "Same issue again", agreed=True
        )
        self.assertFalse(result["success"], "TC15 FAIL")
        self.assertIn("notice", result["message"])
        print("TC15 PASS – Duplicate threshold triggers notice")


if __name__ == "__main__":
    print("=" * 60)
    print("  BLACK-BOX TEST SUITE — UC-02 Register Complaint")
    print("=" * 60)
    loader = unittest.TestLoader()
    loader.sortTestMethodsUsing = None  # preserve definition order
    suite = loader.loadTestsFromTestCase(TestRegisterComplaint)
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    print(f"\n  Result: {passed}/{result.testsRun} tests passed")