"""
reports.py
Analytical reports and statistical summaries for the Gym Management System.
Built with Pandas to perform meaningful grouping, aggregation, and summary calculations.
"""

import datetime
import pandas as pd
import database


def get_membership_summary():
    """
    Generate overall membership counts and status breakdown using Pandas.
    - Total members count
    - Active members count
    - Expired members count
    - Inactive members count
    Uses dynamic status logic computed by database.get_all_members().
    """
    members = database.get_all_members()
    if not members:
        return {
            'total_members': 0,
            'active_count': 0,
            'expired_count': 0,
            'inactive_count': 0
        }

    # Load records into Pandas DataFrame
    df = pd.DataFrame(members)

    # Use Pandas value_counts to aggregate dynamically computed statuses
    status_counts = df['status'].value_counts()

    return {
        'total_members': len(df),
        'active_count': int(status_counts.get('Active', 0)),
        'expired_count': int(status_counts.get('Expired', 0)),
        'inactive_count': int(status_counts.get('Inactive', 0))
    }


def get_plan_distribution():
    """
    Calculate member enrollment distribution and percentage share across plans.
    - Includes all fixed plans even when enrollment count is zero.
    - Counts all members (Active, Expired, and Inactive).
    - Uses Pandas groupby, merge, and vector percentage calculation.
    """
    # 1. Load all fixed plans into a DataFrame
    plans = database.get_all_plans()
    plans_df = pd.DataFrame([dict(p) for p in plans])

    # 2. Load all members
    members = database.get_all_members()
    if not members:
        plans_df['member_count'] = 0
        plans_df['percentage'] = 0.0
        return plans_df.to_dict(orient='records')

    members_df = pd.DataFrame(members)

    # 3. Group members by plan_id and aggregate counts
    plan_counts = members_df.groupby('plan_id').size().reset_index(name='member_count')

    # 4. Left join to ensure plans with zero members remain present
    merged_df = pd.merge(plans_df, plan_counts, left_on='id', right_on='plan_id', how='left')
    merged_df['member_count'] = merged_df['member_count'].fillna(0).astype(int)

    # 5. Calculate percentage of total membership
    total_members = len(members_df)
    merged_df['percentage'] = (merged_df['member_count'] / total_members * 100).round(1)

    # Sort by plan duration ascending
    merged_df = merged_df.sort_values(by='duration_months')

    return merged_df.to_dict(orient='records')


def get_attendance_analysis():
    """
    Analyze gym visit records using Pandas:
    - Total attendance visits
    - Unique recorded days count
    - Average visits per recorded attendance day (mean of daily visit counts)
    - Busiest weekday based on total check-ins
    - Daily attendance breakdown table
    Safely handles empty attendance datasets without division by zero.
    """
    conn = database.get_db()
    query = """
        SELECT 
            a.id, 
            a.date, 
            a.check_in_time, 
            m.name AS member_name, 
            p.name AS plan_name
        FROM attendance a
        JOIN members m ON a.member_id = m.id
        JOIN plans p ON m.plan_id = p.id
        ORDER BY a.date DESC, a.check_in_time DESC
    """
    try:
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()

    if df.empty:
        return {
            'total_visits': 0,
            'unique_days': 0,
            'avg_per_recorded_day': 0.0,
            'busiest_weekday': 'No data recorded',
            'busiest_weekday_count': 0,
            'daily_counts': []
        }

    # Convert date to datetime to derive weekday names
    df['date_dt'] = pd.to_datetime(df['date'])
    df['weekday_name'] = df['date_dt'].dt.day_name()

    total_visits = len(df)

    # Group visits by date and weekday name
    daily_df = df.groupby(['date', 'weekday_name']).size().reset_index(name='visit_count')
    daily_df = daily_df.sort_values(by='date', ascending=False)
    unique_days = len(daily_df)

    # Calculate average visits per recorded day (not per calendar day)
    avg_per_recorded_day = round(float(daily_df['visit_count'].mean()), 2)

    # Determine busiest weekday
    weekday_counts = df['weekday_name'].value_counts()
    busiest_weekday = str(weekday_counts.idxmax())
    busiest_weekday_count = int(weekday_counts.max())

    return {
        'total_visits': total_visits,
        'unique_days': unique_days,
        'avg_per_recorded_day': avg_per_recorded_day,
        'busiest_weekday': busiest_weekday,
        'busiest_weekday_count': busiest_weekday_count,
        'daily_counts': daily_df.to_dict(orient='records')
    }


def get_expiry_analysis():
    """
    Analyze upcoming and expired memberships using Pandas:
    - Excludes manually inactive accounts (is_active == 0).
    - Identifies active memberships expiring within the next 7 days (0 <= days_remaining <= 7).
    - Identifies already expired memberships.
    """
    members = database.get_all_members()
    if not members:
        return {
            'upcoming_expiries': [],
            'expired_members': [],
            'upcoming_count': 0,
            'expired_count': 0
        }

    df = pd.DataFrame(members)

    # Exclude manually inactive accounts
    active_pool_df = df[(df['is_active'] == 1) & (df['status'] != 'Inactive')].copy()

    if active_pool_df.empty:
        return {
            'upcoming_expiries': [],
            'expired_members': [],
            'upcoming_count': 0,
            'expired_count': 0
        }

    today = datetime.date.today()
    active_pool_df['end_date_dt'] = pd.to_datetime(active_pool_df['end_date']).dt.date
    active_pool_df['days_remaining'] = active_pool_df['end_date_dt'].apply(lambda d: (d - today).days)

    # Filter upcoming expiries: status is Active and expires within 0 to 7 days inclusive
    upcoming_df = active_pool_df[
        (active_pool_df['status'] == 'Active') & 
        (active_pool_df['days_remaining'] >= 0) & 
        (active_pool_df['days_remaining'] <= 7)
    ].sort_values(by='end_date')

    # Filter expired memberships: status is Expired
    expired_df = active_pool_df[active_pool_df['status'] == 'Expired'].sort_values(by='end_date', ascending=False)

    return {
        'upcoming_expiries': upcoming_df.to_dict(orient='records'),
        'expired_members': expired_df.to_dict(orient='records'),
        'upcoming_count': len(upcoming_df),
        'expired_count': len(expired_df)
    }


def generate_members_csv():
    """
    Generate CSV string of the members directory using Pandas DataFrame.to_csv(index=False).
    Includes clean, human-readable column headers and omits internal database keys.
    """
    members = database.get_all_members()
    columns_map = {
        'id': 'Member ID',
        'name': 'Full Name',
        'phone': 'Phone Number',
        'email': 'Email Address',
        'gender': 'Gender',
        'plan_name': 'Membership Plan',
        'fee': 'Plan Fee (INR)',
        'start_date': 'Start Date',
        'end_date': 'Expiry Date',
        'status': 'Status'
    }

    if not members:
        empty_df = pd.DataFrame(columns=list(columns_map.values()))
        return empty_df.to_csv(index=False)

    df = pd.DataFrame(members)
    export_df = df[list(columns_map.keys())].copy()
    export_df['email'] = export_df['email'].fillna('N/A')
    export_df = export_df.rename(columns=columns_map)
    export_df = export_df.sort_values(by='Member ID')

    return export_df.to_csv(index=False)


def generate_attendance_csv():
    """
    Generate CSV string of gym visit history using Pandas DataFrame.to_csv(index=False).
    Derives day of week and formats human-readable column headers.
    """
    conn = database.get_db()
    query = """
        SELECT 
            a.id AS attendance_id,
            a.date,
            a.check_in_time,
            m.id AS member_id,
            m.name AS member_name,
            m.phone,
            p.name AS plan_name
        FROM attendance a
        JOIN members m ON a.member_id = m.id
        JOIN plans p ON m.plan_id = p.id
        ORDER BY a.date DESC, a.check_in_time DESC
    """
    try:
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()

    columns_map = {
        'attendance_id': 'Attendance ID',
        'date': 'Date',
        'day_of_week': 'Day of Week',
        'check_in_time': 'Check-in Time',
        'member_id': 'Member ID',
        'member_name': 'Member Name',
        'phone': 'Phone Number',
        'plan_name': 'Membership Plan'
    }

    if df.empty:
        empty_df = pd.DataFrame(columns=list(columns_map.values()))
        return empty_df.to_csv(index=False)

    df['day_of_week'] = pd.to_datetime(df['date']).dt.day_name()
    export_df = df[list(columns_map.keys())].copy()
    export_df = export_df.rename(columns=columns_map)

    return export_df.to_csv(index=False)
