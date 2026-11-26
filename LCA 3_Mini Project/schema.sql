-- schema.sql
-- Single source of truth for table definitions and default plans

PRAGMA foreign_keys = ON;

-- 1. Fixed Membership Plans (fee in whole rupees)
CREATE TABLE IF NOT EXISTS plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    duration_months INTEGER NOT NULL,
    fee INTEGER NOT NULL
);

-- 2. Member Information (stores current active period only)
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    gender TEXT NOT NULL,
    plan_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES plans (id)
);

-- 3. Daily Attendance (one check-in per member per day)
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    date DATE NOT NULL,
    check_in_time TIME NOT NULL,
    FOREIGN KEY (member_id) REFERENCES members (id),
    UNIQUE(member_id, date)
);

-- Default demonstration plans
INSERT OR IGNORE INTO plans (id, name, duration_months, fee) VALUES
(1, 'Monthly', 1, 1000),
(2, 'Quarterly', 3, 2700),
(3, 'Half-Yearly', 6, 5000),
(4, 'Annual', 12, 9000);
