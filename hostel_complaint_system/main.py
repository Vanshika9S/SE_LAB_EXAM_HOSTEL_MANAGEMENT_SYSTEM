#!/usr/bin/env python3
"""
Hostel Management System — CLI
Use Case: UC-02  Register Complaint
"""

import sys
import os

# Make sure imports work from any working directory
sys.path.insert(0, os.path.dirname(__file__))

from database.models import init_db
from app.auth import login, logout, get_current_user, is_logged_in
from app.complaint_service import (
    register_complaint,
    check_complaint_status,
    get_all_complaints,
)

CATEGORIES = [
    "Maintenance",
    "Mess / Food",
    "Cleanliness",
    "Security",
    "Internet",
    "Other",
]


def separator(char="─", width=60):
    print(char * width)


def print_header(title: str):
    separator("═")
    print(f"  🏫  {title}")
    separator("═")


def print_menu(options: list):
    separator()
    for i, opt in enumerate(options, 1):
        print(f"  [{i}] {opt}")
    separator()


def input_required(prompt: str) -> str:
    while True:
        val = input(prompt).strip()
        if val:
            return val
        print("  ⚠  This field is required.")


def do_login():
    print("\n── Login ──────────────────────────────────────")
    uid = input("  User ID   : ").strip()
    pwd = input("  Password  : ").strip()
    result = login(uid, pwd)
    if result["success"]:
        u = result["user"]
        role_label = "Complaint Manager" if u["role"] == "complaint_manager" else "Student"
        active_label = "" if u["is_active"] else "  ⚠  (Inactive account)"
        print(f"\n  ✅  Welcome, {u['name']} [{role_label}]{active_label}")
    else:
        print(f"\n  ❌  {result['message']}")


def do_register_complaint():
    print("\n── Register Complaint ─────────────────────────")

    if not is_logged_in():
        print("  ❌  You must be logged in first.")
        return

    user = get_current_user()
    if not user["is_active"] or user["role"] != "student":
        print("  ❌  Access denied: only active students can register complaints.")
        return

    # Select category
    print("\n  Complaint Categories:")
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"    [{i}] {cat}")
    cat_input = input("\n  Select category (number): ").strip()
    if not cat_input.isdigit() or not (1 <= int(cat_input) <= len(CATEGORIES)):
        print("  ❌  Invalid category selection.")
        return
    category = CATEGORIES[int(cat_input) - 1]

    description = input_required("\n  Description : ")

    photo = input("  Photo path (press Enter to skip): ").strip()

    print("\n  Agreement: I confirm all information provided is true.")
    agreed_input = input("  Type 'yes' to agree: ").strip().lower()
    agreed = agreed_input == "yes"

    result = register_complaint(category, description, photo, agreed)

    if result["success"]:
        print(f"\n  ✅  Complaint registered successfully!")
        print(f"      Complaint ID : {result['complaint_id']}")
        print("      You may now log out.")
    else:
        print(f"\n  ❌  {result['message']}")


def do_check_status():
    print("\n── Check Complaint Status ─────────────────────")
    cid = input("  Enter Complaint ID: ").strip()
    result = check_complaint_status(cid)
    if result["success"]:
        c = result["complaint"]
        separator()
        print(f"  Complaint ID  : {c['complaint_id']}")
        print(f"  Category      : {c['category']}")
        print(f"  Description   : {c['description']}")
        print(f"  Status        : {c['status']}")
        print(f"  Submitted     : {c['created_at']}")
        if c["photo_path"]:
            print(f"  Photo         : {c['photo_path']}")
        separator()
    else:
        print(f"\n  ❌  {result['message']}")


def do_view_all_complaints():
    """Available to complaint managers."""
    user = get_current_user()
    if user is None or user["role"] != "complaint_manager":
        print("  ❌  Access denied: only complaint managers can view all complaints.")
        return
    complaints = get_all_complaints()
    if not complaints:
        print("  No complaints found.")
        return
    separator()
    print(f"  {'ID':<14} {'Category':<15} {'Status':<12} {'User':<8} {'Date'}")
    separator("-")
    for c in complaints:
        print(f"  {c['complaint_id']:<14} {c['category']:<15} {c['status']:<12} {c['user_id']:<8} {c['created_at'][:10]}")
    separator()


def do_logout():
    logout()
    print("  ✅  Logged out successfully.")


def main():
    print()
    init_db()
    print_header("Hostel Management System")
    print("  Use Case UC-02 : Register Complaint")
    print("  Demo Accounts  :")
    print("    Student (active)   : S001 / pass123")
    print("    Student (inactive) : S002 / pass456")
    print("    Manager            : M001 / mgr789")

    while True:
        user = get_current_user()
        user_info = f"  Logged in as: {user['name']}" if user else "  Not logged in"
        print(f"\n{user_info}")

        if not is_logged_in():
            print_menu(["Login", "Check Complaint Status", "Exit"])
            choice = input("  Choose: ").strip()
            if choice == "1":
                do_login()
            elif choice == "2":
                do_check_status()
            elif choice == "3":
                print("\n  Goodbye! 👋")
                break
        else:
            role = user["role"]
            if role == "student":
                print_menu(["Register Complaint", "Check Complaint Status", "Logout", "Exit"])
                choice = input("  Choose: ").strip()
                if choice == "1":
                    do_register_complaint()
                elif choice == "2":
                    do_check_status()
                elif choice == "3":
                    do_logout()
                elif choice == "4":
                    print("\n  Goodbye! 👋")
                    break
            else:
                print_menu(["View All Complaints", "Check Complaint Status", "Logout", "Exit"])
                choice = input("  Choose: ").strip()
                if choice == "1":
                    do_view_all_complaints()
                elif choice == "2":
                    do_check_status()
                elif choice == "3":
                    do_logout()
                elif choice == "4":
                    print("\n  Goodbye! 👋")
                    break


if __name__ == "__main__":
    main()