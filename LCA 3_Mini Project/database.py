"""
database.py
SQLite database operations and initialization for the Gym Management System.
Uses schema.sql as the single source of truth for table definitions and default plans.
"""

import os
import sqlite3
import datetime
import calendar

# Path definitions
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'college_gym.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'schema.sql')


def get_db():
    """Establish a connection to the SQLite database with row factory and foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name: row['name']
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn


def add_months(source_date, months):
    """
    Calendar-aware addition of months to a date.
    Properly handles month length variations (28, 30, 31 days) and leap years.
    """
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def compute_status(is_active, end_date_str):
    """
    Dynamically compute membership status:
    - is_active == 0  -> 'Inactive' (manually deactivated)
    - end_date >= today -> 'Active'
    - end_date < today  -> 'Expired'
    """
    if is_active == 0:
        return 'Inactive'
    
    today = datetime.date.today()
    if isinstance(end_date_str, str):
        end_date = datetime.date.fromisoformat(end_date_str)
    else:
        end_date = end_date_str
        
    return 'Active' if end_date >= today else 'Expired'


def init_db():
    """
    Initialize database using schema.sql.
    Seeds or verifies fictional demonstration data idempotently.
    """
    conn = get_db()
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    conn.executescript(schema_sql)
    conn.commit()

    seed_demo_data(conn)
    conn.close()


def seed_demo_data(conn):
    """
    Idempotently seeds clearly fictional Indian demonstration records covering:
    - 15 fictional Indian gym members from diverse regions
    - Realistic distribution across Monthly, Quarterly, Half-Yearly, and Annual plans
    - Varied statuses: Active, Expired, and Inactive (manually deactivated)
    - Upcoming expiries within the next 7 days for demonstration
    - Varied attendance records across recent days (respecting UNIQUE(member_id, date))
    
    Safety and Idempotency:
    - Safely replaces the legacy 5 fictional demo members if present.
    - Preserves all actual user-created records (never deletes non-demo phone numbers).
    - Checks for existing demo records to ensure restarts do not duplicate data.
    """
    today = datetime.date.today()
    cursor = conn.cursor()

    # Legacy demo phones to clean up if present
    legacy_demo_phones = [
        "9876500001", "9876500002", "9876500003", "9876500004", "9876500005"
    ]
    legacy_placeholders = ','.join('?' for _ in legacy_demo_phones)

    # 15 Fictional Indian Demo Members
    demo_members = [
        # 1. Aarav Sharma - Active (Monthly, started 10 days ago)
        (
            "Aarav Sharma",
            "9820112345",
            "aarav.sharma@example.in",
            "Male",
            1,  # Monthly
            (today - datetime.timedelta(days=10)).isoformat(),
            add_months(today - datetime.timedelta(days=10), 1).isoformat(),
            1
        ),
        # 2. Priya Nair - Upcoming Expiry (Monthly, expires in 4 days)
        (
            "Priya Nair",
            "9810223456",
            "priya.nair@example.in",
            "Female",
            1,  # Monthly
            (today - datetime.timedelta(days=26)).isoformat(),
            (today + datetime.timedelta(days=4)).isoformat(),
            1
        ),
        # 3. Rohan Patel - Upcoming Expiry (Quarterly, expires in 5 days)
        (
            "Rohan Patel",
            "9845034567",
            "rohan.patel@example.in",
            "Male",
            2,  # Quarterly
            (today - datetime.timedelta(days=85)).isoformat(),
            (today + datetime.timedelta(days=5)).isoformat(),
            1
        ),
        # 4. Ananya Chatterjee - Active (Annual, started 60 days ago)
        (
            "Ananya Chatterjee",
            "9830045678",
            "ananya.chatterjee@example.in",
            "Female",
            4,  # Annual
            (today - datetime.timedelta(days=60)).isoformat(),
            add_months(today - datetime.timedelta(days=60), 12).isoformat(),
            1
        ),
        # 5. Vikramaditya Singh - Active (Half-Yearly, started 45 days ago)
        (
            "Vikramaditya Singh",
            "9829056789",
            "vikram.singh@example.in",
            "Male",
            3,  # Half-Yearly
            (today - datetime.timedelta(days=45)).isoformat(),
            add_months(today - datetime.timedelta(days=45), 6).isoformat(),
            1
        ),
        # 6. Deepa Iyer - Active (Quarterly, started 30 days ago)
        (
            "Deepa Iyer",
            "9444067890",
            "deepa.iyer@example.in",
            "Female",
            2,  # Quarterly
            (today - datetime.timedelta(days=30)).isoformat(),
            add_months(today - datetime.timedelta(days=30), 3).isoformat(),
            1
        ),
        # 7. Mohammed Farooq - Active (Monthly, started 15 days ago)
        (
            "Mohammed Farooq",
            "9849078901",
            "mohammed.farooq@example.in",
            "Male",
            1,  # Monthly
            (today - datetime.timedelta(days=15)).isoformat(),
            add_months(today - datetime.timedelta(days=15), 1).isoformat(),
            1
        ),
        # 8. Sneha Kulkarni - Active (Annual, started 120 days ago)
        (
            "Sneha Kulkarni",
            "9892089012",
            "sneha.kulkarni@example.in",
            "Female",
            4,  # Annual
            (today - datetime.timedelta(days=120)).isoformat(),
            add_months(today - datetime.timedelta(days=120), 12).isoformat(),
            1
        ),
        # 9. Gurpreet Singh - Upcoming Expiry (Quarterly, expires in 2 days)
        (
            "Gurpreet Singh",
            "9872090123",
            "gurpreet.singh@example.in",
            "Male",
            2,  # Quarterly
            (today - datetime.timedelta(days=88)).isoformat(),
            (today + datetime.timedelta(days=2)).isoformat(),
            1
        ),
        # 10. Kavita Reddy - Expired (Monthly, expired 10 days ago)
        (
            "Kavita Reddy",
            "9866012345",
            "kavita.reddy@example.in",
            "Female",
            1,  # Monthly
            (today - datetime.timedelta(days=40)).isoformat(),
            (today - datetime.timedelta(days=10)).isoformat(),
            1
        ),
        # 11. Tanvi Deshmukh - Expired (Quarterly, expired 20 days ago)
        (
            "Tanvi Deshmukh",
            "9825023456",
            "tanvi.deshmukh@example.in",
            "Female",
            2,  # Quarterly
            (today - datetime.timedelta(days=110)).isoformat(),
            (today - datetime.timedelta(days=20)).isoformat(),
            1
        ),
        # 12. Amit Banerjee - Expired (Half-Yearly, expired 20 days ago)
        (
            "Amit Banerjee",
            "9831034567",
            "amit.banerjee@example.in",
            "Male",
            3,  # Half-Yearly
            (today - datetime.timedelta(days=200)).isoformat(),
            (today - datetime.timedelta(days=20)).isoformat(),
            1
        ),
        # 13. Kiran Verma - Expired (Annual, expired 35 days ago)
        (
            "Kiran Verma",
            "9711045678",
            "kiran.verma@example.in",
            "Non-binary",
            4,  # Annual
            (today - datetime.timedelta(days=400)).isoformat(),
            (today - datetime.timedelta(days=35)).isoformat(),
            1
        ),
        # 14. Arjun Menon - Inactive (Monthly, manually deactivated)
        (
            "Arjun Menon",
            "9435056789",
            "arjun.menon@example.in",
            "Male",
            1,  # Monthly
            (today - datetime.timedelta(days=15)).isoformat(),
            add_months(today - datetime.timedelta(days=15), 1).isoformat(),
            0  # Manually deactivated
        ),
        # 15. Pooja Joshi - Inactive (Half-Yearly, manually deactivated)
        (
            "Pooja Joshi",
            "9886067890",
            "pooja.joshi@example.in",
            "Female",
            3,  # Half-Yearly
            (today - datetime.timedelta(days=60)).isoformat(),
            add_months(today - datetime.timedelta(days=60), 6).isoformat(),
            0  # Manually deactivated
        ),
    ]

    new_demo_phones = [m[1] for m in demo_members]
    new_placeholders = ','.join('?' for _ in new_demo_phones)

    # 1. Clean up legacy demo members if still present
    legacy_present = cursor.execute(
        f"SELECT COUNT(*) FROM members WHERE phone IN ({legacy_placeholders})",
        legacy_demo_phones
    ).fetchone()[0]

    if legacy_present > 0:
        cursor.execute(
            f"""
            DELETE FROM attendance 
            WHERE member_id IN (SELECT id FROM members WHERE phone IN ({legacy_placeholders}))
            """,
            legacy_demo_phones
        )
        cursor.execute(
            f"DELETE FROM members WHERE phone IN ({legacy_placeholders})",
            legacy_demo_phones
        )
        conn.commit()

    # 2. Check if all 15 Indian demo members already exist
    existing_count = cursor.execute(
        f"SELECT COUNT(*) FROM members WHERE phone IN ({new_placeholders})",
        new_demo_phones
    ).fetchone()[0]

    if existing_count == len(demo_members):
        print("All 15 Indian demonstration records are present. Seeding skipped.")
        return

    # If partially present, clean up existing demo records before re-inserting to prevent anomalies
    if existing_count > 0:
        cursor.execute(
            f"""
            DELETE FROM attendance 
            WHERE member_id IN (SELECT id FROM members WHERE phone IN ({new_placeholders}))
            """,
            new_demo_phones
        )
        cursor.execute(
            f"DELETE FROM members WHERE phone IN ({new_placeholders})",
            new_demo_phones
        )
        conn.commit()

    # 3. Insert the 15 fictional Indian demo members
    cursor.executemany(
        """
        INSERT INTO members (name, phone, email, gender, plan_id, start_date, end_date, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        demo_members
    )
    conn.commit()

    # Map member phones to their generated IDs for attendance insertion
    rows = cursor.execute("SELECT id, phone FROM members").fetchall()
    phone_to_id = {row['phone']: row['id'] for row in rows}

    # 4. Insert varied attendance records across recent days
    demo_attendance_plan = [
        # Today's check-ins (5 members)
        ("9820112345", today.isoformat(), "06:45:00"),  # Aarav
        ("9830045678", today.isoformat(), "07:15:00"),  # Ananya
        ("9444067890", today.isoformat(), "08:00:00"),  # Deepa
        ("9892089012", today.isoformat(), "18:30:00"),  # Sneha
        ("9872090123", today.isoformat(), "19:15:00"),  # Gurpreet

        # 1 day ago (5 members)
        ("9820112345", (today - datetime.timedelta(days=1)).isoformat(), "06:50:00"),  # Aarav
        ("9810223456", (today - datetime.timedelta(days=1)).isoformat(), "07:30:00"),  # Priya
        ("9845034567", (today - datetime.timedelta(days=1)).isoformat(), "17:45:00"),  # Rohan
        ("9829056789", (today - datetime.timedelta(days=1)).isoformat(), "18:20:00"),  # Vikramaditya
        ("9849078901", (today - datetime.timedelta(days=1)).isoformat(), "19:10:00"),  # Mohammed

        # 2 days ago (5 members, including Kavita who checked in before expiring)
        ("9820112345", (today - datetime.timedelta(days=2)).isoformat(), "07:00:00"),  # Aarav
        ("9830045678", (today - datetime.timedelta(days=2)).isoformat(), "07:20:00"),  # Ananya
        ("9444067890", (today - datetime.timedelta(days=2)).isoformat(), "08:15:00"),  # Deepa
        ("9892089012", (today - datetime.timedelta(days=2)).isoformat(), "18:00:00"),  # Sneha
        ("9866012345", (today - datetime.timedelta(days=2)).isoformat(), "18:45:00"),  # Kavita

        # 3 days ago (5 members)
        ("9810223456", (today - datetime.timedelta(days=3)).isoformat(), "07:15:00"),  # Priya
        ("9845034567", (today - datetime.timedelta(days=3)).isoformat(), "08:00:00"),  # Rohan
        ("9829056789", (today - datetime.timedelta(days=3)).isoformat(), "18:30:00"),  # Vikramaditya
        ("9849078901", (today - datetime.timedelta(days=3)).isoformat(), "19:00:00"),  # Mohammed
        ("9872090123", (today - datetime.timedelta(days=3)).isoformat(), "19:45:00"),  # Gurpreet

        # 4 days ago (4 members)
        ("9820112345", (today - datetime.timedelta(days=4)).isoformat(), "06:40:00"),  # Aarav
        ("9830045678", (today - datetime.timedelta(days=4)).isoformat(), "07:10:00"),  # Ananya
        ("9444067890", (today - datetime.timedelta(days=4)).isoformat(), "08:05:00"),  # Deepa
        ("9892089012", (today - datetime.timedelta(days=4)).isoformat(), "18:15:00"),  # Sneha

        # 5 days ago (4 members, including Arjun who visited before deactivation)
        ("9810223456", (today - datetime.timedelta(days=5)).isoformat(), "07:25:00"),  # Priya
        ("9845034567", (today - datetime.timedelta(days=5)).isoformat(), "17:50:00"),  # Rohan
        ("9829056789", (today - datetime.timedelta(days=5)).isoformat(), "18:10:00"),  # Vikramaditya
        ("9435056789", (today - datetime.timedelta(days=5)).isoformat(), "07:45:00"),  # Arjun
    ]

    demo_attendance = [
        (phone_to_id[phone], date_str, time_str)
        for phone, date_str, time_str in demo_attendance_plan
        if phone in phone_to_id
    ]

    cursor.executemany(
        """
        INSERT INTO attendance (member_id, date, check_in_time)
        VALUES (?, ?, ?)
        """,
        demo_attendance
    )

    conn.commit()
    print("Seeded 15 fictional Indian demo members and attendance records.")


# ============================================================================
# QUERY HELPERS (Used by app.py and reports.py)
# ============================================================================

def get_all_plans():
    """Retrieve all fixed membership plans."""
    conn = get_db()
    plans = conn.execute("SELECT * FROM plans ORDER BY duration_months ASC").fetchall()
    conn.close()
    return plans


def get_plan_by_id(plan_id):
    """Retrieve a single plan by its ID."""
    conn = get_db()
    plan = conn.execute("SELECT * FROM plans WHERE id = ?", (plan_id,)).fetchone()
    conn.close()
    return plan


def get_all_members(search_query=None, status_filter=None, plan_filter=None):
    """
    Retrieve members with their plan name and dynamically calculated status.
    Supports optional search (by name/phone) and filtering (by status or plan).
    """
    conn = get_db()
    query = """
        SELECT m.*, p.name AS plan_name, p.duration_months, p.fee
        FROM members m
        JOIN plans p ON m.plan_id = p.id
        WHERE 1=1
    """
    params = []

    if search_query:
        query += " AND (m.name LIKE ? OR m.phone LIKE ?)"
        term = f"%{search_query.strip()}%"
        params.extend([term, term])

    if plan_filter:
        query += " AND m.plan_id = ?"
        params.append(plan_filter)

    query += " ORDER BY m.id DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()

    # Process dynamic status for each member
    members = []
    today = datetime.date.today()
    for row in rows:
        member_dict = dict(row)
        member_dict['status'] = compute_status(row['is_active'], row['end_date'])
        
        # Apply status filter in Python after dynamic calculation
        if status_filter and member_dict['status'].lower() != status_filter.lower():
            continue
            
        members.append(member_dict)

    return members


def get_member_by_id(member_id):
    """Retrieve single member details with dynamic status and plan information."""
    conn = get_db()
    query = """
        SELECT m.*, p.name AS plan_name, p.duration_months, p.fee
        FROM members m
        JOIN plans p ON m.plan_id = p.id
        WHERE m.id = ?
    """
    row = conn.execute(query, (member_id,)).fetchone()
    conn.close()

    if not row:
        return None

    member_dict = dict(row)
    member_dict['status'] = compute_status(row['is_active'], row['end_date'])
    return member_dict


def add_member(name, phone, email, gender, plan_id, start_date_str):
    """Add a new member. Calculates end_date using calendar-aware month addition."""
    plan = get_plan_by_id(plan_id)
    if not plan:
        raise ValueError("Invalid membership plan selected.")

    start_date = datetime.date.fromisoformat(start_date_str)
    end_date = add_months(start_date, plan['duration_months'])

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO members (name, phone, email, gender, plan_id, start_date, end_date, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (name.strip(), phone.strip(), email.strip() if email else None, gender, plan_id, start_date.isoformat(), end_date.isoformat())
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def update_member(member_id, name, phone, email, gender):
    """Update editable member contact details."""
    conn = get_db()
    conn.execute(
        """
        UPDATE members 
        SET name = ?, phone = ?, email = ?, gender = ?
        WHERE id = ?
        """,
        (name.strip(), phone.strip(), email.strip() if email else None, gender, member_id)
    )
    conn.commit()
    conn.close()


def toggle_member_status(member_id):
    """Toggle a member between Active (1) and Inactive (0) for soft deactivation."""
    member = get_member_by_id(member_id)
    if not member:
        return False

    new_active_state = 0 if member['is_active'] == 1 else 1
    conn = get_db()
    conn.execute("UPDATE members SET is_active = ? WHERE id = ?", (new_active_state, member_id))
    conn.commit()
    conn.close()
    return True


def renew_member(member_id, new_plan_id):
    """
    Renew a member's membership using calendar-aware date addition.
    - If currently expired: new period starts today.
    - If currently active: new period extends from existing end_date.
    - Resets is_active to 1 (reactivates member if inactive).
    """
    member = get_member_by_id(member_id)
    plan = get_plan_by_id(new_plan_id)
    if not member or not plan:
        raise ValueError("Member or plan not found.")

    today = datetime.date.today()
    current_end = datetime.date.fromisoformat(member['end_date'])

    if current_end < today:
        # Expired: renewal begins today
        new_start = today
        new_end = add_months(today, plan['duration_months'])
    else:
        # Still active: extend from current end date
        new_start = datetime.date.fromisoformat(member['start_date'])
        new_end = add_months(current_end, plan['duration_months'])

    conn = get_db()
    conn.execute(
        """
        UPDATE members
        SET plan_id = ?, start_date = ?, end_date = ?, is_active = 1
        WHERE id = ?
        """,
        (new_plan_id, new_start.isoformat(), new_end.isoformat(), member_id)
    )
    conn.commit()
    conn.close()
    return True


def record_attendance(member_id, date_str=None, time_str=None):
    """
    Record attendance for a member.
    Enforces duplicate prevention: raises ValueError if already checked in on the given date.
    """
    today_str = date_str or datetime.date.today().isoformat()
    now_time = time_str or datetime.datetime.now().strftime('%H:%M:%S')

    conn = get_db()
    # Check duplicate
    existing = conn.execute(
        "SELECT id FROM attendance WHERE member_id = ? AND date = ?",
        (member_id, today_str)
    ).fetchone()

    if existing:
        conn.close()
        raise ValueError("Member has already checked in for this date.")

    conn.execute(
        "INSERT INTO attendance (member_id, date, check_in_time) VALUES (?, ?, ?)",
        (member_id, today_str, now_time)
    )
    conn.commit()
    conn.close()
    return True


def get_attendance_by_date(date_str=None):
    """Retrieve attendance records for a specific date (defaults to today)."""
    target_date = date_str or datetime.date.today().isoformat()
    conn = get_db()
    query = """
        SELECT a.id, a.date, a.check_in_time, m.id AS member_id, m.name, m.phone, p.name AS plan_name
        FROM attendance a
        JOIN members m ON a.member_id = m.id
        JOIN plans p ON m.plan_id = p.id
        WHERE a.date = ?
        ORDER BY a.check_in_time DESC
    """
    rows = conn.execute(query, (target_date,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_member_attendance_history(member_id):
    """Retrieve the check-in history for an individual member."""
    conn = get_db()
    rows = conn.execute(
        """
        SELECT date, check_in_time
        FROM attendance
        WHERE member_id = ?
        ORDER BY date DESC, check_in_time DESC
        """,
        (member_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_dashboard_data():
    """
    Calculate the four dashboard statistics and retrieve the 7-day upcoming expiry list.
    """
    today = datetime.date.today()
    today_str = today.isoformat()
    in_7_days_str = (today + datetime.timedelta(days=7)).isoformat()

    conn = get_db()
    
    # Total members
    total_members = conn.execute("SELECT COUNT(*) FROM members").fetchone()[0]

    # Active members (is_active = 1 AND end_date >= today)
    active_members = conn.execute(
        "SELECT COUNT(*) FROM members WHERE is_active = 1 AND end_date >= ?",
        (today_str,)
    ).fetchone()[0]

    # Expired members (is_active = 1 AND end_date < today)
    expired_members = conn.execute(
        "SELECT COUNT(*) FROM members WHERE is_active = 1 AND end_date < ?",
        (today_str,)
    ).fetchone()[0]

    # Today's attendance check-ins
    today_attendance = conn.execute(
        "SELECT COUNT(*) FROM attendance WHERE date = ?",
        (today_str,)
    ).fetchone()[0]

    # Upcoming expiries (expiring between today and today + 7 days, currently active)
    upcoming_query = """
        SELECT m.id, m.name, m.phone, m.end_date, p.name AS plan_name
        FROM members m
        JOIN plans p ON m.plan_id = p.id
        WHERE m.is_active = 1 AND m.end_date >= ? AND m.end_date <= ?
        ORDER BY m.end_date ASC
    """
    upcoming_rows = conn.execute(upcoming_query, (today_str, in_7_days_str)).fetchall()
    conn.close()

    return {
        'total_members': total_members,
        'active_members': active_members,
        'expired_members': expired_members,
        'today_attendance': today_attendance,
        'upcoming_expiries': [dict(r) for r in upcoming_rows]
    }
