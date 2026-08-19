# Health Care Operation Intelligence Dashboard

A production-grade Business Intelligence / Decision Support System that turns
raw hospital operational data into a secure, real-time, interactive
dashboard — built with **Python, Pandas, Plotly and Streamlit**.

Raw data (patients, lab, pharmacy, ambulance, staff, appointments, OT,
emergency) → cleaning → curated KPIs → insight-driven charts → alerts →
faster, data-driven decisions for hospital administrators.

---

## 1. Project structure

```
hospital_dashboard/
├── Home.py                          # Login gate + sidebar navigation (entry point)
├── views/
│   ├── Overview.py                  # Executive KPIs, alerts, trends, revenue mix
│   ├── Patient_Overview.py          # Hospital_Visits deep-dive
│   ├── Laboratory.py                # laboratory data
│   ├── Pharmacy.py                  # pharmacy data
│   ├── Ambulance.py                 # Ambulance_Transportation
│   ├── Staff_Scheduling.py          # Staff_Scheduling
│   ├── Appointments.py              # Appointments
│   ├── OT_Dashboard.py              # OT_Dashboard
│   └── Emergency_Monitoring.py      # ER_Monitoring_Summary
├── utils/
│   ├── auth.py                      # Session-based access guard for every page
│   ├── data_loader.py               # Reads + cleans every sheet (cached)
│   ├── kpi.py                       # KPI math + alert/"intelligence" rules
│   └── styling.py                   # Design system: theme, KPI cards, icons, insight charts
├── data/
│   └── Hospital_Dataset_Complete_Project.xlsx   # Bundled sample dataset
├── .streamlit/
│   ├── config.toml                  # Theme + server config
│   └── secrets.toml.example         # Copy to secrets.toml and set real credentials
├── requirements.txt
└── README.md
```

## 2. What each page shows

| Page | Source sheet | Highlights |
|---|---|---|
| Overview | all sheets | 7 curated executive KPIs, live alerts, trends, revenue mix |
| Patient Overview | `Hospital_Visits` | Demographics, admissions, billing, satisfaction |
| Laboratory | `laboratory data` | Test volume, revenue, category mix, technician load |
| Pharmacy | `pharmacy data` | Sales, category/branch performance, demand intelligence |
| Ambulance | `Ambulance_Transportation` | Response/travel time, fuel cost, driver workload |
| Staff Scheduling | `Staff_Scheduling` | Leave rate, overtime, duty types, emergency coverage |
| Appointments | `Appointments` | Completion/cancellation/no-show rate, peak hours |
| OT Dashboard | `OT_Dashboard` | Surgery status, room utilization, surgeon workload |
| Emergency Monitoring | `ER_Monitoring_Summary` | Monthly case trends, category/season heatmap |

Each page is intentionally trimmed to its **5–7 most decision-relevant KPIs**
(one visually emphasized "hero" metric plus supporting metrics), an
**Alerts** section that turns raw numbers into plain-language guidance
(e.g. *"Bed occupancy is at 92% — prepare additional beds"*), and bar charts
that highlight the single most important bar (max/min) instead of a wall of
same-colored columns.

> **Note on medicine stock:** the source dataset does not include a live
> stock-on-hand column, so the Pharmacy page surfaces **dispensing velocity**
> (fastest-moving medicines) as a practical proxy for reorder alerts instead
> of a literal stock count.

## 3. Authentication

Sign-in is required before any dashboard page is reachable:

- `Home.py` shows a login form and only mounts the sidebar navigation after
  a successful sign-in.
- `utils/auth.py` adds a second safety net (`require_login()`) on every
  individual page, in case its direct URL is opened before signing in.
- Credentials are read from `.streamlit/secrets.toml` (see
  `secrets.toml.example` for the format) rather than hardcoded in source.
  **Never commit your real `secrets.toml`** — it is already listed in
  `.gitignore`.

Default demo credentials (set in `secrets.toml.example`):

| Username | Password |
|---|---|
| `admin` | `admin123` |
| `doctor` | `hospital2026` |

Change these before deploying to production.

## 4. Run locally

**Requirements:** Python 3.10+

```bash
# 1. (Recommended) create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up your credentials
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit .streamlit/secrets.toml with your own username/password pairs

# 4. Run the app
streamlit run Home.py
```

The app opens at **http://localhost:8501**. The bundled Excel file in
`data/Hospital_Dataset_Complete_Project.xlsx` loads automatically — no setup
needed. You can also upload a different workbook (same 8 sheet names) from
the sidebar on the Overview page; every other page will automatically use
that uploaded data too.

## 5. Deploy to Streamlit Community Cloud

1. Push this folder to a **GitHub repository** (keep the `data/` folder in
   the repo so the sample dataset ships with the app, or remove it and rely
   purely on the in-app uploader). Do **not** commit `.streamlit/secrets.toml`.
2. Go to <https://share.streamlit.io/> → **New app**.
3. Select your repository, branch, and set **Main file path** to `Home.py`.
4. In the app's **Settings → Secrets**, paste the contents of your local
   `secrets.toml` (this is how Streamlit Cloud injects `st.secrets`).
5. Click **Deploy**. Streamlit Cloud installs everything from
   `requirements.txt` automatically.
6. Any time you `git push` changes, the deployed app auto-updates.

### Other deployment options
- **Render / Railway / Fly.io / a VM:** run
  `streamlit run Home.py --server.port $PORT --server.address 0.0.0.0`
  and provide `.streamlit/secrets.toml` on the server (or environment-based
  secrets, per platform).
- **Docker:**
  ```dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY . .
  RUN pip install --no-cache-dir -r requirements.txt
  EXPOSE 8501
  CMD ["streamlit", "run", "Home.py", "--server.address=0.0.0.0"]
  ```

## 6. Using your own hospital data

The app expects an Excel workbook with these **exact sheet names**:

```
Hospital_Visits, laboratory data, pharmacy data, Ambulance_Transportation,
Staff_Scheduling, Appointments, OT_Dashboard, ER_Monitoring_Summary
```

Either replace `data/Hospital_Dataset_Complete_Project.xlsx` with your own
file (same sheet/column names), or use the **file uploader** in the sidebar
of the Overview page at runtime — no code changes required.

## 7. Design system

`utils/styling.py` is the single source of truth for the look and feel, so
every page stays visually consistent:

- A hand-built, stroke-based icon set (no emoji, no external icon-font CDN).
- `page_header()` — the gradient banner at the top of every page.
- `filter_bar()` — a bordered filter card at the **top of each page** (not
  the sidebar) so filters are visible without extra clicks, matching the
  in-page filter pattern used across the dashboard.
- `render_kpi_cards()` — a clean KPI grid with one visually emphasized
  "hero" metric and color-coded tone (good / warning / critical).
- `gradient_bar()` — a bar chart helper that shades every bar along a
  smooth color scale driven by its own value (darker = higher), so the
  trend is visible from color alone, not just bar height.
- `chart_title()` / `section_title()` — consistent headings, used inside
  `st.container(border=True)` chart cards so every grid stays aligned.
- Subtle fade-in animations and a soft gradient app background for a
  polished, non-distracting feel.

## 8. Tech stack

- **Streamlit** — multipage web app / UI framework
- **Pandas** — Excel ingestion, cleaning, aggregation
- **Plotly** — interactive charts (line, bar, pie, heatmap)
- **openpyxl** — Excel engine used by Pandas

## 9. Troubleshooting

| Issue | Fix |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` inside your active environment |
| Blank/old data after uploading a new file | Refresh the browser tab — Streamlit caches by file content, so a genuinely new file will reload automatically |
| "No dataset loaded yet" on a sub-page | Open the **Overview** page first (via the sidebar) at least once per session |
| Login fails with correct-looking credentials | Confirm `.streamlit/secrets.toml` exists and matches the format in `secrets.toml.example` |
| Port already in use | `streamlit run Home.py --server.port 8502` |

---

**One-line summary:** *A Python/Streamlit Business Intelligence system that
transforms raw hospital operational data into a secure, curated dashboard —
7-or-fewer decision-grade KPIs per page, insight-highlighted charts, and
plain-language alerts — helping administrators monitor operations in real
time and make faster, data-driven decisions.*
