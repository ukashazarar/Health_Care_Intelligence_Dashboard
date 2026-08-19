"""
data_loader.py
----------------
Central data-access layer for the Medical Operation Intelligence Dashboard.

Responsibilities:
    1. Read every sheet from the hospital Excel dataset.
    2. Clean each sheet (trim strings, fix dtypes, drop exact duplicates,
       handle missing values) so every downstream page works on tidy data.
    3. Cache the result with Streamlit so the (fairly large, ~9MB / 100k+ row)
       workbook is parsed only once per session.

Every function here is pure / side-effect free (besides the Streamlit cache),
which makes it easy to unit-test outside of Streamlit as well.
"""

from pathlib import Path
import pandas as pd
import streamlit as st

# Default bundled dataset. A user can also upload their own file from the
# sidebar (see Home.py) which overrides this path at runtime.
DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "Hospital_Dataset_Complete_Project.xlsx"

REQUIRED_SHEETS = [
    "Hospital_Visits",
    "laboratory data",
    "pharmacy data",
    "Ambulance_Transportation",
    "Staff_Scheduling",
    "Appointments",
    "OT_Dashboard",
    "ER_Monitoring_Summary",
]


# ----------------------------------------------------------------------
# Generic cleaning helpers
# ----------------------------------------------------------------------
def _strip_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Trim whitespace on every text/object column."""
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].astype("string").str.strip()
    return df


def _parse_dates(df: pd.DataFrame, cols) -> pd.DataFrame:
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def _basic_clean(df: pd.DataFrame, date_cols=None) -> pd.DataFrame:
    """Shared cleaning pipeline applied to every sheet."""
    df = df.copy()
    df = _strip_strings(df)
    if date_cols:
        df = _parse_dates(df, date_cols)
    # Drop fully-duplicated rows (safe: never drops a legitimately repeated
    # transaction, since IDs are unique columns and duplicates would mean an
    # exact copy of every field).
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)
    return df


# ----------------------------------------------------------------------
# Sheet-specific cleaning
# ----------------------------------------------------------------------
def _clean_visits(df: pd.DataFrame) -> pd.DataFrame:
    df = _basic_clean(df, date_cols=["Visit_Date"])
    numeric_cols = [
        "Age", "Waiting_Time_Min", "Length_of_Stay", "Pharmacy_Cost",
        "Consultation_Fee", "Lab_Cost", "Room_Charges", "Total_Bill",
        "Satisfaction_Score",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["Visit_ID", "Visit_Date"])
    # Guard against impossible negative values from bad source data.
    for col in ["Waiting_Time_Min", "Length_of_Stay", "Total_Bill"]:
        if col in df.columns:
            df.loc[df[col] < 0, col] = pd.NA
    df["Month"] = df["Visit_Date"].dt.to_period("M").astype(str)
    df["Year"] = df["Visit_Date"].dt.year
    return df


def _clean_lab(df: pd.DataFrame) -> pd.DataFrame:
    df = _basic_clean(df, date_cols=["Sample Collection Date & Time", "Test Date"])
    df["Discount Amount"] = pd.to_numeric(df["Discount Amount"], errors="coerce").fillna(0)
    df["Test Cost"] = pd.to_numeric(df["Test Cost"], errors="coerce")
    df["Net Amount"] = pd.to_numeric(df["Net Amount"], errors="coerce")
    df = df.dropna(subset=["Lab Transaction ID", "Test Date"])
    df["Month"] = df["Test Date"].dt.to_period("M").astype(str)
    return df


def _clean_pharmacy(df: pd.DataFrame) -> pd.DataFrame:
    df = _basic_clean(df, date_cols=["Prescription Date"])
    df["Discount Amount"] = pd.to_numeric(df["Discount Amount"], errors="coerce").fillna(0)
    for col in ["Quantity Dispensed", "Unit Price", "Total Amount", "Net Amount"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["Pharmacy Transaction ID", "Prescription Date"])
    df["Month"] = df["Prescription Date"].dt.to_period("M").astype(str)
    return df


def _clean_er(df: pd.DataFrame) -> pd.DataFrame:
    df = _basic_clean(df)
    df["Case_Count"] = pd.to_numeric(df["Case_Count"], errors="coerce").fillna(0)
    # YearMonth arrives as e.g. "2023-01" -> keep as string but also build a
    # real Timestamp for correct chronological sorting/plotting.
    df["YearMonth_dt"] = pd.to_datetime(df["YearMonth"], format="%Y-%m", errors="coerce")
    df = df.sort_values("YearMonth_dt").reset_index(drop=True)
    return df


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------
@st.cache_data(show_spinner="Reading & cleaning hospital dataset...")
def load_all_data(file_bytes: bytes | None = None, file_path: str | None = None) -> dict:
    """
    Load every sheet of the hospital workbook and return a dict of cleaned
    DataFrames keyed by short names used across the app.

    Parameters
    ----------
    file_bytes: raw bytes of an uploaded .xlsx (takes priority if given)
    file_path:  path on disk to read instead of the bundled default dataset
    """
    if file_bytes is not None:
        source = pd.io.common.BytesIO(file_bytes)
    else:
        source = file_path or str(DEFAULT_DATA_PATH)

    xls = pd.ExcelFile(source)
    missing = [s for s in REQUIRED_SHEETS if s not in xls.sheet_names]
    if missing:
        raise ValueError(
            f"The uploaded workbook is missing required sheet(s): {missing}. "
            f"Found sheets: {xls.sheet_names}"
        )

    visits = _clean_visits(pd.read_excel(xls, "Hospital_Visits"))
    lab = _clean_lab(pd.read_excel(xls, "laboratory data"))
    pharmacy = _clean_pharmacy(pd.read_excel(xls, "pharmacy data"))
    ambulance = _basic_clean(pd.read_excel(xls, "Ambulance_Transportation"), date_cols=["Call_Date"])
    staff = _basic_clean(pd.read_excel(xls, "Staff_Scheduling"), date_cols=["Date"])
    appointments = _basic_clean(pd.read_excel(xls, "Appointments"), date_cols=["Appointment_Date"])
    ot = _basic_clean(pd.read_excel(xls, "OT_Dashboard"), date_cols=["OT_Date"])
    er = _clean_er(pd.read_excel(xls, "ER_Monitoring_Summary"))

    # Derived helper columns used by several pages.
    for _df, date_col in [
        (ambulance, "Call_Date"), (staff, "Date"),
        (appointments, "Appointment_Date"), (ot, "OT_Date"),
    ]:
        _df["Month"] = _df[date_col].dt.to_period("M").astype(str)

    return {
        "visits": visits,
        "lab": lab,
        "pharmacy": pharmacy,
        "ambulance": ambulance,
        "staff": staff,
        "appointments": appointments,
        "ot": ot,
        "er": er,
    }


def get_data_for_page() -> dict:
    """
    Used by every page under pages/. Prefers the dataset already loaded (and
    possibly uploaded by the user) on the Overview page via st.session_state;
    falls back to the bundled default file so each page also works if opened
    directly.
    """
    if "data" in st.session_state:
        return st.session_state["data"]

    if not DEFAULT_DATA_PATH.exists():
        st.error(
            "No dataset loaded yet. Please open the **Overview** page first "
            "(or upload a dataset there) so it can be shared with this page."
        )
        st.stop()

    data = load_all_data(file_path=str(DEFAULT_DATA_PATH))
    st.session_state["data"] = data
    return data


def get_global_date_bounds(data: dict):
    """Return (min_date, max_date) across every date-bearing sheet, used to
    initialise sidebar date filters sensibly."""
    dates = pd.concat([
        data["visits"]["Visit_Date"],
        data["appointments"]["Appointment_Date"],
        data["ot"]["OT_Date"],
        data["ambulance"]["Call_Date"],
        data["staff"]["Date"],
    ])
    dates = dates.dropna()
    return dates.min().date(), dates.max().date()
