# Gym Management System

A simple Gym Management System developed using Python, Flask, SQLite and Pandas as a college project.

## Features

- **Dashboard:** View the application dashboard.
- **Member Management:** Add, view, edit, search and deactivate members.
- **Membership Management:** Manage membership plans, expiry dates and renewals.
- **Attendance Management:** Record daily attendance and view attendance history.
- **Reports:** View membership and attendance reports and export data as CSV files.
- **Light/Dark Theme:** Switch between light and dark appearance.

## Technologies Used

- Python
- Flask
- SQLite
- Pandas
- HTML
- CSS

## Requirements

- Python 3.10 or newer recommended.
- pip (Python package installer).

## Installation and Setup

### 1. Download the project

Download or clone this repository and open the `college_submission` folder in your terminal.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**Windows:**

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
python app.py
```

### 6. Open the application

Open your browser and visit:

http://127.0.0.1:5000/

## Database

The application uses SQLite for storing member, membership plan and attendance information.

The included `college_gym.db` file contains sample demonstration data.

## Project Structure

```text
college_submission/
│
├── app.py
├── database.py
├── reports.py
├── schema.sql
├── requirements.txt
├── college_gym.db
├── README.md
│
├── static/
│   └── style.css
│
└── templates/
    ├── base.html
    ├── dashboard.html
    ├── members.html
    ├── member_form.html
    ├── memberships.html
    ├── attendance.html
    ├── member_attendance.html
    └── reports.html
```

## Note

This project was developed as a college submission project. It is designed for local use and demonstration purposes.