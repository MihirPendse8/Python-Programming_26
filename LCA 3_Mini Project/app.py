"""
app.py
Main entry point and web application controller for the Gym Management System.
Built with Flask, SQLite, and Jinja2 templates.
"""

import datetime
import calendar
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, Response
import database
import reports

# Initialize the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'college-gym-secret-key-2026'


# ============================================================================
# MODULE 1: DASHBOARD
# ============================================================================

@app.route('/')
def dashboard():
    """Homepage route: renders the starting dashboard with real-time gym metrics."""
    dashboard_data = database.get_dashboard_data()
    today_date = datetime.date.today().strftime('%A, %d %B %Y')
    return render_template(
        'dashboard.html',
        stats=dashboard_data,
        today_date=today_date
    )


# ============================================================================
# MODULE 2: MEMBER MANAGEMENT
# ============================================================================

@app.route('/members')
def members():
    """
    Member Directory: Lists all members with dynamic status badges.
    Supports searching by name/phone and filtering by plan and status.
    """
    search_query = request.args.get('search', '').strip()
    selected_status = request.args.get('status', '').strip().lower()
    selected_plan = request.args.get('plan', '').strip()

    # Convert plan to integer if provided and valid
    plan_id = int(selected_plan) if selected_plan.isdigit() else None

    # Retrieve filtered members and all available plans for the dropdown
    all_members = database.get_all_members(
        search_query=search_query if search_query else None,
        status_filter=selected_status if selected_status else None,
        plan_filter=plan_id
    )
    plans = database.get_all_plans()

    return render_template(
        'members.html',
        members=all_members,
        plans=plans,
        search_query=search_query,
        selected_status=selected_status,
        selected_plan=selected_plan
    )


@app.route('/members/add', methods=['GET', 'POST'])
def add_member():
    """
    Add a new member.
    Automatically calculates expiry date from start date and selected plan duration.
    """
    plans = database.get_all_plans()
    today_str = datetime.date.today().isoformat()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        gender = request.form.get('gender', '').strip()
        plan_id = request.form.get('plan_id', '').strip()
        start_date = request.form.get('start_date', '').strip()

        # Validation
        errors = []
        if not name:
            errors.append("Full Name is required.")
        if not phone:
            errors.append("Phone Number is required.")
        if gender not in ['Male', 'Female', 'Non-binary']:
            errors.append("Please select a valid gender option.")
        if not plan_id or not plan_id.isdigit():
            errors.append("Please select a valid membership plan.")
        if not start_date:
            errors.append("Membership Start Date is required.")
        else:
            try:
                datetime.date.fromisoformat(start_date)
            except ValueError:
                errors.append("Invalid start date format. Please use YYYY-MM-DD.")

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template(
                'member_form.html',
                mode='add',
                plans=plans,
                today=today_str,
                form_data=request.form
            )

        try:
            new_id = database.add_member(
                name=name,
                phone=phone,
                email=email if email else None,
                gender=gender,
                plan_id=int(plan_id),
                start_date_str=start_date
            )
            flash(f"Member '{name}' added successfully!", 'success')
            return redirect(url_for('members'))
        except Exception as e:
            flash(f"Error adding member: {str(e)}", 'error')
            return render_template(
                'member_form.html',
                mode='add',
                plans=plans,
                today=today_str,
                form_data=request.form
            )

    return render_template(
        'member_form.html',
        mode='add',
        plans=plans,
        today=today_str,
        form_data=None
    )


@app.route('/members/<int:member_id>/edit', methods=['GET', 'POST'])
def edit_member(member_id):
    """
    Edit an existing member's contact information (Name, Phone, Email, Gender).
    Membership plan changes and renewals are reserved for the Memberships module.
    """
    member = database.get_member_by_id(member_id)
    if not member:
        flash("Member not found.", 'error')
        return redirect(url_for('members'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        gender = request.form.get('gender', '').strip()

        # Validation
        errors = []
        if not name:
            errors.append("Full Name cannot be empty.")
        if not phone:
            errors.append("Phone Number cannot be empty.")
        if gender not in ['Male', 'Female', 'Non-binary']:
            errors.append("Please select a valid gender option.")

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('member_form.html', mode='edit', member=member, form_data=request.form)

        try:
            database.update_member(
                member_id=member_id,
                name=name,
                phone=phone,
                email=email if email else None,
                gender=gender
            )
            flash(f"Member '{name}' details updated successfully!", 'success')
            return redirect(url_for('members'))
        except Exception as e:
            flash(f"Error updating member: {str(e)}", 'error')
            return render_template('member_form.html', mode='edit', member=member, form_data=request.form)

    return render_template('member_form.html', mode='edit', member=member, form_data=None)


@app.route('/members/<int:member_id>/toggle-status', methods=['POST'])
def toggle_member(member_id):
    """
    Soft Deactivation / Reactivation:
    - Active or Expired members are set to Inactive (is_active = 0).
    - Inactive members are set back to Active (is_active = 1).
    - Never hard-deletes records; preserves historical attendance.
    """
    member = database.get_member_by_id(member_id)
    if not member:
        flash("Member not found.", 'error')
        return redirect(url_for('members'))

    database.toggle_member_status(member_id)
    
    # Check new status to give an appropriate flash message
    updated_member = database.get_member_by_id(member_id)
    if updated_member['is_active'] == 0:
        flash(f"Member '{member['name']}' has been deactivated.", 'success')
    else:
        flash(f"Member '{member['name']}' has been reactivated.", 'success')

    return redirect(url_for('members'))


# ============================================================================
# MODULE 3: MEMBERSHIP MANAGEMENT
# ============================================================================

@app.route('/memberships')
def memberships():
    """
    Memberships overview:
    - Fixed plan offerings retrieved from SQLite.
    - Expiring soon monitoring (active members expiring within 0-7 days).
    - Expired memberships monitoring (already expired members).
    - Excludes manually inactive members from both monitoring lists.
    """
    plans = database.get_all_plans()
    all_members = database.get_all_members()
    today = datetime.date.today()

    expiring_soon = []
    expired_members = []

    for m in all_members:
        # Exclude manually inactive members from monitoring lists
        if m['is_active'] == 0 or m['status'] == 'Inactive':
            continue

        end_date = datetime.date.fromisoformat(m['end_date'])
        days_remaining = (end_date - today).days

        if m['status'] == 'Active':
            # Expiring between today and next 7 days, inclusive
            if 0 <= days_remaining <= 7:
                m['days_remaining'] = days_remaining
                expiring_soon.append(m)
        elif m['status'] == 'Expired':
            expired_members.append(m)

    # Sort expiring soon by soonest expiry first
    expiring_soon.sort(key=lambda x: x['end_date'])
    # Sort expired members by most recently expired first
    expired_members.sort(key=lambda x: x['end_date'], reverse=True)

    return render_template(
        'memberships.html',
        plans=plans,
        expiring_soon=expiring_soon,
        expired_members=expired_members
    )


@app.route('/memberships/<int:member_id>/renew', methods=['POST'])
def renew_membership(member_id):
    """
    Renew a member's membership using the selected plan.
    - Uses database.renew_member() without duplicating calculation logic.
    - If currently active: extends from existing expiry date.
    - If currently expired: restarts from today.
    - Resets is_active to 1.
    """
    plan_id_str = request.form.get('plan_id', '').strip()
    if not plan_id_str or not plan_id_str.isdigit():
        flash("Please select a valid membership plan.", 'error')
        return redirect(url_for('memberships'))

    plan_id = int(plan_id_str)
    member = database.get_member_by_id(member_id)
    if not member:
        flash("Member not found.", 'error')
        return redirect(url_for('memberships'))

    plan = database.get_plan_by_id(plan_id)
    if not plan:
        flash("Selected membership plan does not exist.", 'error')
        return redirect(url_for('memberships'))

    try:
        database.renew_member(member_id, plan_id)
        updated_member = database.get_member_by_id(member_id)
        flash(
            f"Membership for '{member['name']}' renewed successfully with the {plan['name']} plan! "
            f"New expiry date: {updated_member['end_date']}.",
            'success'
        )
    except Exception as e:
        flash(f"Error renewing membership: {str(e)}", 'error')

    return redirect(url_for('memberships'))


# ============================================================================
# MODULE 4: ATTENDANCE TRACKING
# ============================================================================

@app.route('/attendance', methods=['GET'])
def attendance():
    """
    Daily attendance tracking:
    - Mark Today's Attendance: Dropdown of active members who have not yet checked in today.
    - Attendance History: Daily records with previous/next day and today navigation.
    """
    today = datetime.date.today()
    selected_date_str = request.args.get('date', '').strip()

    if selected_date_str:
        try:
            target_date = datetime.date.fromisoformat(selected_date_str)
        except ValueError:
            flash("Invalid date format. Showing today's attendance.", 'error')
            target_date = today
    else:
        target_date = today

    date_filter = target_date.isoformat()
    selected_date_display = target_date.strftime('%A, %d %B %Y')
    prev_date = (target_date - datetime.timedelta(days=1)).isoformat()
    next_date = (target_date + datetime.timedelta(days=1)).isoformat()

    # Rule 4: Display only active members who have NOT checked in today
    today_checkins = database.get_attendance_by_date(today.isoformat())
    checked_in_ids = {r['member_id'] for r in today_checkins}

    all_members = database.get_all_members()
    eligible_members = [
        m for m in all_members
        if m['status'] == 'Active' and m['is_active'] == 1 and m['id'] not in checked_in_ids
    ]
    eligible_members.sort(key=lambda m: m['name'].lower())

    # Retrieve attendance records for the selected date
    attendance_records = database.get_attendance_by_date(date_filter)

    return render_template(
        'attendance.html',
        eligible_members=eligible_members,
        attendance_records=attendance_records,
        selected_date=date_filter,
        selected_date_display=selected_date_display,
        prev_date=prev_date,
        next_date=next_date,
        today=today.isoformat()
    )


@app.route('/attendance/check-in', methods=['POST'])
@app.route('/attendance', methods=['POST'])
def check_in_attendance():
    """
    Record a member's daily visit (arrival time only).
    - Captures one single timestamp for both database persistence and UI feedback.
    - Validates member existence and Active status.
    - Rejects Expired or manually Inactive members.
    - Prevents duplicate check-ins on the same day.
    """
    member_id_str = request.form.get('member_id', '').strip()
    if not member_id_str or not member_id_str.isdigit():
        flash("Please select a valid member to check in.", 'error')
        return redirect(url_for('attendance'))

    member_id = int(member_id_str)
    member = database.get_member_by_id(member_id)

    if not member:
        flash("Selected member does not exist.", 'error')
        return redirect(url_for('attendance'))

    # Validation: Reject manually inactive members
    if member['is_active'] == 0:
        flash(f"Cannot check in: Member '{member['name']}' is currently inactive.", 'error')
        return redirect(url_for('attendance'))

    # Validation: Reject expired memberships
    if member['status'] != 'Active':
        flash(f"Cannot check in: Membership for '{member['name']}' has expired.", 'error')
        return redirect(url_for('attendance'))

    # Capture timestamp ONCE for both database persistence and UI feedback
    now = datetime.datetime.now()
    today_str = now.date().isoformat()
    time_24h = now.strftime('%H:%M:%S')
    time_display = now.strftime('%I:%M %p')

    # Record attendance with duplicate prevention
    try:
        database.record_attendance(member_id, date_str=today_str, time_str=time_24h)
        flash(f"Attendance marked successfully for '{member['name']}' at {time_display}!", 'success')
    except (ValueError, sqlite3.IntegrityError):
        flash(
            f"Cannot check in: '{member['name']}' has already checked in today.",
            'error'
        )
    except Exception as e:
        flash(f"Error recording attendance: {str(e)}", 'error')

    return redirect(url_for('attendance'))


@app.route('/attendance/member')
@app.route('/attendance/member/<int:member_id>')
def member_attendance(member_id=None):
    """
    Individual member attendance monthly calendar:
    - Allows inspection of any member (Active, Expired, Inactive).
    - Monthly calendar grid:
        Green: Visit recorded.
        Light Red: Past date with no visit recorded.
        Neutral: Future dates or today without visit.
    - Monthly visit count and legend.
    - Previous and Next month navigation.
    """
    today = datetime.date.today()
    all_members = database.get_all_members()
    all_members.sort(key=lambda m: m['name'].lower())

    # Resolve target member
    req_member_id = request.args.get('member_id', '').strip()
    if req_member_id.isdigit():
        target_member_id = int(req_member_id)
    elif member_id is not None:
        target_member_id = member_id
    elif all_members:
        target_member_id = all_members[0]['id']
    else:
        target_member_id = None

    selected_member = None
    if target_member_id is not None:
        selected_member = database.get_member_by_id(target_member_id)
        if not selected_member and all_members:
            selected_member = all_members[0]

    # Resolve target month and year
    year_param = request.args.get('year', '').strip()
    month_param = request.args.get('month', '').strip()

    try:
        year = int(year_param) if year_param.isdigit() else today.year
        month = int(month_param) if month_param.isdigit() else today.month
        if not (1 <= month <= 12 and 1900 <= year <= 2100):
            year = today.year
            month = today.month
    except ValueError:
        year = today.year
        month = today.month

    # Navigation: previous and next month calculations
    prev_month = 12 if month == 1 else month - 1
    prev_year = year - 1 if month == 1 else year
    next_month = 1 if month == 12 else month + 1
    next_year = year + 1 if month == 12 else year

    # Retrieve attendance records for the selected member
    attended_dates = set()
    monthly_visits = 0
    if selected_member:
        history = database.get_member_attendance_history(selected_member['id'])
        attended_dates = {r['date'] for r in history}
        month_prefix = f"{year:04d}-{month:02d}"
        monthly_visits = sum(1 for d in attended_dates if d.startswith(month_prefix))

    # Build calendar matrix with Monday as the first weekday
    cal = calendar.Calendar(firstweekday=calendar.MONDAY)
    month_weeks = cal.monthdatescalendar(year, month)
    calendar_weeks = []

    for week in month_weeks:
        week_days = []
        for d in week:
            d_str = d.isoformat()
            is_current_month = (d.month == month)
            has_visit = (d_str in attended_dates)
            is_today = (d == today)
            is_past = (d < today)

            # Determine visual status:
            if not is_current_month:
                status = 'other-month'
            elif has_visit:
                status = 'recorded'     # Green: visit recorded
            elif is_past:
                status = 'no-record'    # Light red: past date with no visit recorded
            else:
                status = 'neutral'      # Neutral: future or today without visit

            week_days.append({
                'day_number': d.day,
                'date_str': d_str,
                'is_current_month': is_current_month,
                'has_visit': has_visit,
                'is_today': is_today,
                'status': status
            })
        calendar_weeks.append(week_days)

    month_name = calendar.month_name[month]
    weekday_headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    return render_template(
        'member_attendance.html',
        selected_member=selected_member,
        all_members=all_members,
        calendar_weeks=calendar_weeks,
        year=year,
        month=month,
        month_name=month_name,
        prev_year=prev_year,
        prev_month=prev_month,
        next_year=next_year,
        next_month=next_month,
        monthly_visits=monthly_visits,
        today=today,
        weekday_headers=weekday_headers
    )


# ============================================================================
# MODULE 5: PANDAS REPORTS & ANALYTICS
# ============================================================================

@app.route('/reports', endpoint='reports')
def reports_page():
    """
    Analytical reports dashboard computed using Pandas:
    - Membership summary (total, active, expired, inactive counts)
    - Plan distribution (enrollment counts and percentage share)
    - Attendance analysis (total visits, avg visits per recorded day, busiest weekday, daily counts)
    - Membership expiry analysis (upcoming 7 days and expired members)
    """
    summary = reports.get_membership_summary()
    plans_distribution = reports.get_plan_distribution()
    attendance_analysis = reports.get_attendance_analysis()
    expiry_analysis = reports.get_expiry_analysis()

    return render_template(
        'reports.html',
        summary=summary,
        plans_distribution=plans_distribution,
        attendance=attendance_analysis,
        expiry=expiry_analysis
    )


@app.route('/reports/export/members')
def export_members_csv():
    """
    Download gym members directory as a CSV file generated via Pandas.
    """
    csv_data = reports.generate_members_csv()
    today_str = datetime.date.today().isoformat()
    filename = f"gym_members_report_{today_str}.csv"
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


@app.route('/reports/export/attendance')
def export_attendance_csv():
    """
    Download attendance log as a CSV file generated via Pandas.
    """
    csv_data = reports.generate_attendance_csv()
    today_str = datetime.date.today().isoformat()
    filename = f"gym_attendance_report_{today_str}.csv"
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


# ============================================================================
# APPLICATION RUNNER
# ============================================================================

if __name__ == '__main__':
    # Verify and ensure the database is initialized
    database.init_db()

    # Start the local development server
    print("Starting Gym Management System at http://127.0.0.1:5000/")
    app.run(host='127.0.0.1', port=5000, debug=True)
