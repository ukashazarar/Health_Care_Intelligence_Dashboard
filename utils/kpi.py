"""
kpi.py
------
All KPI math and the "intelligence" alert rules live here, kept separate
from the Streamlit UI so the logic is easy to test and re-use across pages.

Each `alert_*` function returns a tuple: (level, message)
    level: "critical" | "warning" | "good"
"""

import pandas as pd


def pct(numerator, denominator, decimals=1):
    """Safe percentage helper — never divides by zero."""
    if denominator in (0, None) or pd.isna(denominator) or denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, decimals)


def safe_mean(series):
    if series is None or len(series) == 0:
        return 0.0
    val = series.mean()
    return 0.0 if pd.isna(val) else round(float(val), 1)


def trend_pct(current, previous, decimals=1):
    """% change from previous -> current, used for KPI deltas."""
    if previous in (0, None) or pd.isna(previous) or previous == 0:
        return None
    return round(((current - previous) / previous) * 100, decimals)


# ----------------------------------------------------------------------
# Hospital-wide overview KPIs (Home page)
# ----------------------------------------------------------------------
def overview_kpis(visits: pd.DataFrame, ot: pd.DataFrame, appointments: pd.DataFrame,
                   staff: pd.DataFrame, pharmacy: pd.DataFrame, lab: pd.DataFrame) -> dict:
    total_patients = len(visits)
    total_revenue = visits["Total_Bill"].sum() + pharmacy["Net Amount"].sum() + lab["Net Amount"].sum()
    bed_occupancy = pct((visits["Bed_Status"] == "Occupied").sum(), len(visits))
    avg_wait = safe_mean(visits["Waiting_Time_Min"])
    avg_los = safe_mean(visits["Length_of_Stay"])
    readmission_rate = pct((visits["Readmission"] == "Yes").sum(), len(visits))
    pending_payment_rate = pct((visits["Payment_Status"] == "Pending").sum(), len(visits))
    avg_satisfaction = safe_mean(visits["Satisfaction_Score"])

    er_visits = visits[visits["Admission_Type"] == "Emergency"]
    er_avg_wait = safe_mean(er_visits["Waiting_Time_Min"])

    ot_total = len(ot)
    ot_completed_rate = pct((ot["Surgery_Status"] == "Completed").sum(), ot_total)
    ot_cancelled_rate = pct((ot["Surgery_Status"] == "Cancelled").sum(), ot_total)

    appt_total = len(appointments)
    appt_noshow_rate = pct((appointments["Status"] == "No-show").sum(), appt_total)
    appt_cancel_rate = pct((appointments["Status"] == "Cancelled").sum(), appt_total)

    staff_total = len(staff)
    staff_on_leave_rate = pct((staff["Leave_Status"] == "On Leave").sum(), staff_total)

    return dict(
        total_patients=total_patients,
        total_revenue=total_revenue,
        bed_occupancy=bed_occupancy,
        avg_wait=avg_wait,
        avg_los=avg_los,
        readmission_rate=readmission_rate,
        pending_payment_rate=pending_payment_rate,
        avg_satisfaction=avg_satisfaction,
        er_avg_wait=er_avg_wait,
        ot_total=ot_total,
        ot_completed_rate=ot_completed_rate,
        ot_cancelled_rate=ot_cancelled_rate,
        appt_total=appt_total,
        appt_noshow_rate=appt_noshow_rate,
        appt_cancel_rate=appt_cancel_rate,
        staff_total=staff_total,
        staff_on_leave_rate=staff_on_leave_rate,
    )


# ----------------------------------------------------------------------
# Alert / Intelligence rules
# Thresholds are documented inline; tune freely for a real deployment.
# ----------------------------------------------------------------------
def generate_alerts(k: dict, dept_load: pd.DataFrame = None) -> list:
    alerts = []

    # Bed occupancy
    if k["bed_occupancy"] >= 90:
        alerts.append(("critical", f"Bed occupancy is at {k['bed_occupancy']}% — hospital is almost full. Prepare additional beds / expedite discharges."))
    elif k["bed_occupancy"] >= 75:
        alerts.append(("warning", f"Bed occupancy is at {k['bed_occupancy']}% — monitor capacity closely."))
    else:
        alerts.append(("good", f"Bed occupancy is healthy at {k['bed_occupancy']}%."))

    # ER waiting time
    if k["er_avg_wait"] >= 45:
        alerts.append(("critical", f"Average Emergency waiting time is {k['er_avg_wait']} min — Emergency department is overloaded. Deploy more doctors/staff."))
    elif k["er_avg_wait"] >= 30:
        alerts.append(("warning", f"Average Emergency waiting time is {k['er_avg_wait']} min — trending high."))

    # Readmission rate
    if k["readmission_rate"] >= 15:
        alerts.append(("critical", f"Readmission rate is {k['readmission_rate']}% — review discharge & follow-up protocols."))
    elif k["readmission_rate"] >= 10:
        alerts.append(("warning", f"Readmission rate is {k['readmission_rate']}% — slightly elevated."))

    # OT cancellations
    if k["ot_cancelled_rate"] >= 15:
        alerts.append(("critical", f"OT cancellation rate is {k['ot_cancelled_rate']}% — investigate scheduling/resource conflicts."))
    elif k["ot_cancelled_rate"] >= 8:
        alerts.append(("warning", f"OT cancellation rate is {k['ot_cancelled_rate']}% — keep an eye on OT scheduling."))

    # Appointment no-shows
    if k["appt_noshow_rate"] >= 15:
        alerts.append(("warning", f"Appointment no-show rate is {k['appt_noshow_rate']}% — consider SMS/call reminders."))

    # Staff leave
    if k["staff_on_leave_rate"] >= 20:
        alerts.append(("critical", f"{k['staff_on_leave_rate']}% of scheduled staff are on leave — staffing shortage risk."))
    elif k["staff_on_leave_rate"] >= 12:
        alerts.append(("warning", f"{k['staff_on_leave_rate']}% of scheduled staff are on leave — monitor coverage."))

    # Pending payments
    if k["pending_payment_rate"] >= 25:
        alerts.append(("warning", f"{k['pending_payment_rate']}% of bills are still pending payment — follow up on collections."))

    # Patient satisfaction
    if k["avg_satisfaction"] < 3:
        alerts.append(("critical", f"Average patient satisfaction score is {k['avg_satisfaction']}/5 — needs urgent attention."))
    elif k["avg_satisfaction"] < 3.8:
        alerts.append(("warning", f"Average patient satisfaction score is {k['avg_satisfaction']}/5 — room for improvement."))

    # Department overload (highest patient-volume department)
    if dept_load is not None and len(dept_load) > 0:
        top_dept = dept_load.iloc[0]
        share = pct(top_dept["Patients"], dept_load["Patients"].sum())
        if share >= 35:
            alerts.append(("warning", f"{top_dept['Department']} handles {share}% of all patient visits — highest workload, consider reallocating staff."))

    return alerts
