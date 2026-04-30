# SE_LAB_EXAM_HOSTEL_MANAGEMENT_SYSTEM
# Hostel Management System — UC-02: Register Complaint

## Project Structure

```
hostel_complaint_system/
├── main.py                        ← CLI entry point (run the app)
├── README.md
├── database/
│   └── models.py                  ← SQLite schema & seed data
├── app/
│   ├── auth.py                    ← Login / logout / session
│   └── complaint_service.py       ← Register & check complaint logic
└── tests/
    ├── test_blackbox.py           ← TC01–TC15 (from xlsx)
    └── test_whitebox.py           ← WB01–WB15 (branch/path coverage)
```

---

## How to Run

### 1. Run the interactive CLI app

```bash
cd hostel_complaint_system
python main.py
```

Demo credentials:
| Role              | User ID | Password |
|-------------------|---------|----------|
| Student (active)  | S001    | pass123  |
| Student (inactive)| S002    | pass456  |
| Complaint Manager | M001    | mgr789   |

---

### 2. Run Black-Box Tests (TC01–TC15)

```bash
cd hostel_complaint_system
python tests/test_blackbox.py
```

Or with unittest runner:
```bash
python -m unittest tests.test_blackbox -v
```

---

### 3. Run White-Box Tests (WB01–WB15)

```bash
cd hostel_complaint_system
python tests/test_whitebox.py
```

Or with unittest runner:
```bash
python -m unittest tests.test_whitebox -v
```

---

### 4. Run ALL tests together

```bash
cd hostel_complaint_system
python -m unittest discover -s tests -v
```

---
### 5. Single Black-Box Tests (TC01–TC15)

```bash
cd hostel_complaint_system
python tests/test_blackbox_demo.py
```


## Use Case: UC-02 Register Complaint

| Field            | Value                                      |
|------------------|--------------------------------------------|
| Use Case ID      | UC-02                                      |
| Use Case Name    | Register Complaint                         |
| Created By       | Complaint Manager                          |
| Actors           | Complaint Manager, Students                |
| Priority         | High                                       |
| Preconditions    | User logged in with valid credentials; active student |
| Frequency of Use | Medium                                     |

### Flow of Events
1. Student logs into the Hostel Management System with valid credentials
2. Student navigates to the complaint registration interface
3. Student fills all required fields (category, description, optional photo)
4. Student verifies all information and checks the agreement checkbox
5. Student submits the Complaint Registration Form
6. Student logs out; success message shown with Complaint ID

### Exception Flow
- If student is not active → access denied, cannot register complaint

### Post-Conditions
- Complaint is stored in the database; visible to complaint manager

### Exceptions
- Too many same complaints → sends a college-wide notice instead

---

## Black-Box Test Cases (from xlsx)

| Test ID | Description                                      | Expected Output                        |
|---------|--------------------------------------------------|----------------------------------------|
| TC01    | Login with valid credentials                     | User logged in successfully            |
| TC02    | Login with invalid credentials                   | Error message displayed                |
| TC03    | Access complaint form as active student          | Complaint form displayed               |
| TC04    | Access complaint form as inactive student        | Access denied message                  |
| TC05    | Submit complaint with all valid fields           | Complaint registered with ID           |
| TC06    | Submit complaint with missing fields             | Validation error message               |
| TC07    | Submit without agreement checkbox                | Prompt to accept agreement             |
| TC08    | Upload valid photo attachment                    | Photo uploaded successfully            |
| TC09    | Upload invalid file type                         | File type error message                |
| TC10    | Check complaint status with valid ID             | Correct status displayed               |
| TC11    | Check complaint status with invalid ID           | Error message displayed                |
| TC12    | Submit with empty description field              | Validation error for required field    |
| TC13    | Submit without selecting complaint category      | Prompt to select category              |
| TC14    | Session timeout during complaint submission      | User redirected to login               |
| TC15    | Multiple same complaints submitted               | System triggers notice instead         |

---

## White-Box Test Coverage

| Test ID | Branch / Path Covered                              |
|---------|----------------------------------------------------|
| WB01    | Not logged in → early return                       |
| WB02    | Manager role → denied                              |
| WB03    | Inactive student → denied                          |
| WB04    | Empty category → validation                        |
| WB05    | Whitespace-only description → validation           |
| WB06    | Agreement = False → validation                     |
| WB07    | Invalid photo extensions (.exe .sh .docx .mp4)    |
| WB08    | Valid photo extensions (.jpg .jpeg .png .gif .pdf) |
| WB09    | No photo → optional, complain succeeds             |
| WB10    | Duplicates below threshold → allowed              |
| WB11    | Duplicates at threshold → notice triggered         |
| WB12    | Full happy path end-to-end                         |
| WB13    | Check status with empty complaint ID               |
| WB14    | Check status with whitespace complaint ID          |
| WB15    | Login with empty user ID / password               |
