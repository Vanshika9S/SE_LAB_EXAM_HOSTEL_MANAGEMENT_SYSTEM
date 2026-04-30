#!/usr/bin/env python3
"""
Black-Box Test Demo — UC-02 Register Complaint
Simulates each test case with visible input/output like the CLI
"""

import sys
import os
import time

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

def header(tc_id, description):
    print("\n" + "═" * 55)
    print(f"  TEST CASE : {tc_id}")
    print(f"  DESC      : {description}")
    print("═" * 55)

def show_input(label, value):
    print(f"  >> {label:<12}: {value}")

def show_output(expected, actual, passed):
    print(f"  Expected  : {expected}")
    print(f"  Got       : {actual}")
    print(f"  Result    : {'✅ PASS' if passed else '❌ FAIL'}")

def pause():
    input("\n  [ Press Enter for next test case ] ")
    reset_db()

# ── TC01 ────────────────────────────────────────────────────────────────────
def tc01():
    header("TC01", "Login with valid credentials")
    show_input("User ID", "S001")
    show_input("Password", "pass123")
    result = auth.login("S001", "pass123")
    show_output(
        "User logged in successfully",
        f"Welcome, {result['user']['name']} [Student]" if result["success"] else result["message"],
        result["success"]
    )
    pause()

# ── TC02 ────────────────────────────────────────────────────────────────────
def tc02():
    header("TC02", "Login with invalid credentials")
    show_input("User ID", "S001")
    show_input("Password", "wrongpass")
    result = auth.login("S001", "wrongpass")
    show_output(
        "Error message displayed",
        result["message"],
        not result["success"]
    )
    pause()

# ── TC03 ────────────────────────────────────────────────────────────────────
def tc03():
    header("TC03", "Access complaint form as active student")
    show_input("User ID", "S001")
    show_input("Password", "pass123")
    auth.login("S001", "pass123")
    accessible = auth.is_active_student()
    show_output(
        "Complaint form displayed",
        "Complaint form accessible" if accessible else "Access denied",
        accessible
    )
    pause()

# ── TC04 ────────────────────────────────────────────────────────────────────
def tc04():
    header("TC04", "Access complaint form as inactive student")
    show_input("User ID", "S002")
    show_input("Password", "pass456")
    auth.login("S002", "pass456")
    result = complaint_service.register_complaint("Maintenance", "Broken door", agreed=True)
    show_output(
        "Access denied message",
        result["message"],
        not result["success"]
    )
    pause()

# ── TC05 ────────────────────────────────────────────────────────────────────
def tc05():
    header("TC05", "Submit complaint with all valid fields")
    show_input("User ID", "S001")
    show_input("Category", "Maintenance")
    show_input("Description", "Broken window in room 101")
    show_input("Photo", "photo.jpg")
    show_input("Agreement", "yes")
    auth.login("S001", "pass123")
    result = complaint_service.register_complaint(
        "Maintenance", "Broken window in room 101", photo_path="photo.jpg", agreed=True
    )
    show_output(
        "Complaint registered with ID",
        f"Complaint ID: {result['complaint_id']}" if result["success"] else result["message"],
        result["success"]
    )
    pause()

# ── TC06 ────────────────────────────────────────────────────────────────────
def tc06():
    header("TC06", "Submit complaint with missing fields (no description)")
    show_input("User ID", "S001")
    show_input("Category", "Mess / Food")
    show_input("Description", "(empty)")
    show_input("Agreement", "yes")
    auth.login("S001", "pass123")
    result = complaint_service.register_complaint("Mess / Food", "", agreed=True)
    show_output(
        "Validation error message",
        result["message"],
        not result["success"]
    )
    pause()

# ── TC07 ────────────────────────────────────────────────────────────────────
def tc07():
    header("TC07", "Submit complaint without agreement checkbox")
    show_input("User ID", "S001")
    show_input("Category", "Security")
    show_input("Description", "Broken gate")
    show_input("Agreement", "no (unchecked)")
    auth.login("S001", "pass123")
    result = complaint_service.register_complaint("Security", "Broken gate", agreed=False)
    show_output(
        "Prompt to accept agreement",
        result["message"],
        not result["success"]
    )
    pause()

# ── TC08 ────────────────────────────────────────────────────────────────────
def tc08():
    header("TC08", "Upload valid photo attachment")
    show_input("User ID", "S001")
    show_input("Category", "Cleanliness")
    show_input("Description", "Dirty bathroom")
    show_input("Photo", "photo.jpg")
    show_input("Agreement", "yes")
    auth.login("S001", "pass123")
    result = complaint_service.register_complaint(
        "Cleanliness", "Dirty bathroom", photo_path="photo.jpg", agreed=True
    )
    show_output(
        "Photo uploaded successfully",
        f"Complaint ID: {result['complaint_id']}" if result["success"] else result["message"],
        result["success"]
    )
    pause()

# ── TC09 ────────────────────────────────────────────────────────────────────
def tc09():
    header("TC09", "Upload invalid file type")
    show_input("User ID", "S001")
    show_input("Category", "Internet")
    show_input("Description", "No Wi-Fi")
    show_input("Photo", "virus.exe")
    show_input("Agreement", "yes")
    auth.login("S001", "pass123")
    result = complaint_service.register_complaint(
        "Internet", "No Wi-Fi", photo_path="virus.exe", agreed=True
    )
    show_output(
        "File type error message",
        result["message"],
        not result["success"]
    )
    pause()

# ── TC10 ────────────────────────────────────────────────────────────────────
def tc10():
    header("TC10", "Check complaint status with valid ID")
    auth.login("S001", "pass123")
    reg = complaint_service.register_complaint("Other", "Random issue", agreed=True)
    cid = reg["complaint_id"]
    show_input("Complaint ID", cid)
    result = complaint_service.check_complaint_status(cid)
    show_output(
        "Correct status displayed",
        f"Status: {result['complaint']['status']}" if result["success"] else result["message"],
        result["success"]
    )
    pause()

# ── TC11 ────────────────────────────────────────────────────────────────────
def tc11():
    header("TC11", "Check complaint status with invalid ID")
    show_input("Complaint ID", "INVALID-ID-9999")
    result = complaint_service.check_complaint_status("INVALID-ID-9999")
    show_output(
        "Error message displayed",
        result["message"],
        not result["success"]
    )
    pause()

# ── TC12 ────────────────────────────────────────────────────────────────────
def tc12():
    header("TC12", "Submit complaint with empty description field")
    show_input("User ID", "S001")
    show_input("Category", "Maintenance")
    show_input("Description", "(whitespace only)")
    show_input("Agreement", "yes")
    auth.login("S001", "pass123")
    result = complaint_service.register_complaint("Maintenance", "   ", agreed=True)
    show_output(
        "Validation error for required field",
        result["message"],
        not result["success"]
    )
    pause()

# ── TC13 ────────────────────────────────────────────────────────────────────
def tc13():
    header("TC13", "Submit complaint without selecting complaint category")
    show_input("User ID", "S001")
    show_input("Category", "(empty)")
    show_input("Description", "Some issue")
    show_input("Agreement", "yes")
    auth.login("S001", "pass123")
    result = complaint_service.register_complaint("", "Some issue", agreed=True)
    show_output(
        "Prompt to select category",
        result["message"],
        not result["success"]
    )
    pause()

# ── TC14 ────────────────────────────────────────────────────────────────────
def tc14():
    header("TC14", "Session timeout during complaint submission")
    show_input("User ID", "S001")
    show_input("Action", "Login then session expires (logout)")
    auth.login("S001", "pass123")
    auth.logout()  # simulate session timeout
    result = complaint_service.register_complaint("Maintenance", "Broken fan", agreed=True)
    show_output(
        "User redirected to login",
        result["message"],
        not result["success"]
    )
    pause()

# ── TC15 ────────────────────────────────────────────────────────────────────
def tc15():
    header("TC15", "Multiple same complaints submitted")
    show_input("User ID", "S001")
    show_input("Category", "Mess / Food")
    show_input("Action", f"Submit same complaint {complaint_service.DUPLICATE_THRESHOLD}+ times")
    auth.login("S001", "pass123")
    for i in range(complaint_service.DUPLICATE_THRESHOLD):
        r = complaint_service.register_complaint("Mess / Food", "Cold food", agreed=True)
        print(f"  Attempt {i+1} : Complaint ID = {r.get('complaint_id', 'N/A')}")
    result = complaint_service.register_complaint("Mess / Food", "Cold food", agreed=True)
    show_output(
        "System triggers notice instead",
        result["message"],
        not result["success"]
    )
    print("\n  [ End of all test cases ]")


if __name__ == "__main__":
    init_db()
    reset_db()

    print("═" * 55)
    print("  🏫  Hostel Management System")
    print("  BLACK-BOX TEST DEMO — UC-02 Register Complaint")
    print("═" * 55)
    print("  15 test cases will run one by one.")
    print("  Press Enter after each to continue.")
    input("  [ Press Enter to Start ] ")

    tc01()
    tc02()
    tc03()
    tc04()
    tc05()
    tc06()
    tc07()
    tc08()
    tc09()
    tc10()
    tc11()
    tc12()
    tc13()
    tc14()
    tc15()

    print("\n" + "═" * 55)
    print("  ✅  All 15 Black-Box Test Cases Completed!")
    print("═" * 55)