# Health Care Operation Intelligence Dashboard

A production-grade **Business Intelligence and Decision Support System** that transforms raw hospital operational data into a secure, interactive, and insight-driven dashboard.

The system processes hospital data related to patients, laboratories, pharmacy, ambulance services, staff scheduling, appointments, operation theatres, and emergency monitoring. It converts raw operational data into **KPIs, interactive visualizations, alerts, trends, and decision-support insights** to help hospital administrators make faster and data-driven decisions.

**Raw Hospital Data → Data Cleaning → KPI Calculation → Interactive Dashboard → Alerts & Insights → Decision Support**

---

## 📊 Project Overview

The **Health Care Operation Intelligence Dashboard** is built using Python and Streamlit to provide a centralized view of important hospital operations.

The dashboard focuses on:

* Hospital patient visits and admissions
* Laboratory operations
* Pharmacy performance
* Ambulance transportation
* Staff scheduling
* Appointment management
* Operation theatre utilization
* Emergency department monitoring
* Revenue and operational trends
* KPI-based alerts
* PDF report generation

Each dashboard page presents a limited number of **decision-relevant KPIs**, interactive charts, and plain-language alerts instead of overwhelming users with unnecessary information.

---

## 📁 Project Structure

```text
hospital_dashboard/
│
├── Home.py                              # Application entry point + login
├── logo.png                             # Dashboard logo
├── README.md                            # Project documentation
├── requirements.txt                     # Python dependencies
│
├── data/
│   └── Hospital_Dataset_Complete_Project.xlsx
│                                         # Bundled sample hospital dataset
│
├── utils/
│   ├── __init__.py
│   ├── auth.py                           # Authentication and access control
│   ├── data_loader.py                    # Dataset loading and cleaning
│   ├── kpi.py                            # KPI calculations and alert rules
│   ├── pdf_generator.py                  # PDF report generation
│   └── styling.py                        # Dashboard styling and UI components
│
├── views/
│   ├── Overview.py                       # Executive overview
│   ├── Patient_Overview.py               # Patient analytics
│   ├── Laboratory.py                     # Laboratory analytics
│   ├── Pharmacy.py                       # Pharmacy analytics
│   ├── Ambulance.py                      # Ambulance analytics
│   ├── Staff_Scheduling.py               # Staff scheduling analytics
│   ├── Appointments.py                   # Appointment analytics
│   ├── OT_Dashboard.py                   # Operation theatre analytics
│   └── Emergency_Monitoring.py           # Emergency monitoring
│
└── .streamlit/
    ├── config.toml                       # Streamlit configuration
    ├── secrets.toml.example               # Example credentials format
    └── secrets.toml                      # Local credentials - NOT committed
```

---

# 🔐 Authentication

The dashboard includes a login system to restrict access to hospital operational information.

Authentication is implemented using:

* `Home.py` — Login interface
* `utils/auth.py` — Session-based authentication and access protection
* `.streamlit/secrets.toml` — Stores credentials locally
* `secrets.toml.example` — Provides the required credentials format without exposing private credentials

Every dashboard page also uses an authentication check so that pages cannot be directly accessed without signing in.

### Demo Credentials

For demonstration purposes, use:

```text
Username: admin
Password: admin123
```

> **Security Note:** The demo credentials are provided only for local/project demonstration. Change them before using the application in a real production environment.

### Credential Security

Real credentials are **not stored in the source code**.

The actual file:

```text
.streamlit/secrets.toml
```

is intentionally excluded from Git using `.gitignore`.

Only the following example file should be committed:

```text
.streamlit/secrets.toml.example
```

Never commit API keys, passwords, tokens, database credentials, or other sensitive information to GitHub.

---

# 📊 Dashboard Pages

## 1. Overview

The Overview page provides an executive-level summary of hospital operations.

### Features

* Curated executive KPIs
* Operational alerts
* Patient trends
* Revenue trends
* Department performance
* Interactive charts
* Data upload functionality
* Decision-support insights
* PDF report generation

---

## 2. Patient Overview

Based on the `Hospital_Visits` dataset.

### Key Information

* Patient demographics
* Hospital visits
* Admissions
* Billing information
* Patient satisfaction
* Operational trends

---

## 3. Laboratory

Based on the `laboratory data` sheet.

### Key Information

* Laboratory test volume
* Revenue
* Test category distribution
* Technician workload
* Laboratory performance

---

## 4. Pharmacy

Based on the `pharmacy data` sheet.

### Key Information

* Pharmacy sales
* Medicine categories
* Branch performance
* Medicine demand
* Dispensing trends

### Medicine Stock Intelligence

The source dataset does not contain a live **stock-on-hand** field.

Therefore, the dashboard uses **medicine dispensing velocity** as a practical demand indicator rather than displaying a misleading literal stock count.

---

## 5. Ambulance

Based on the `Ambulance_Transportation` sheet.

### Key Information

* Ambulance response time
* Travel time
* Fuel cost
* Driver workload
* Transportation trends

---

## 6. Staff Scheduling

Based on the `Staff_Scheduling` sheet.

### Key Information

* Staff workload
* Leave rate
* Overtime
* Duty types
* Emergency coverage
* Scheduling trends

---

## 7. Appointments

Based on the `Appointments` sheet.

### Key Information

* Completed appointments
* Cancelled appointments
* No-show rate
* Peak appointment hours
* Appointment trends

---

## 8. OT Dashboard

Based on the `OT_Dashboard` sheet.

### Key Information

* Surgery status
* Operation theatre utilization
* Room utilization
* Surgeon workload
* Surgery trends

---

## 9. Emergency Monitoring

Based on the `ER_Monitoring_Summary` sheet.

### Key Information

* Emergency case trends
* Monthly emergency volume
* Emergency categories
* Seasonal patterns
* Heatmap-based analysis

---

# 🚨 Decision-Support Alerts

The dashboard does not only display raw numbers.

It converts important operational metrics into **plain-language alerts** that can support hospital decision-making.

Examples:

```text
Bed occupancy is at 92% — prepare additional beds.
```

```text
Appointment no-show rate is increasing — review appointment confirmation procedures.
```

```text
Emergency cases are increasing — consider additional emergency coverage.
```

```text
Medicine dispensing velocity is high — monitor demand and reorder requirements.
```

The exact alerts are dynamically generated based on the underlying data and KPI rules.

---

# 📈 KPI Intelligence

The dashboard uses a centralized KPI calculation system implemented in:

```text
utils/kpi.py
```

This module is responsible for:

* KPI calculations
* Threshold evaluation
* Operational alerts
* Performance indicators
* Decision-support rules

Each page is intentionally designed around approximately **5–7 decision-relevant KPIs** to keep the dashboard focused and easy to understand.

---

# 📄 PDF Report Generation

The project includes a dedicated PDF generation module:

```text
utils/pdf_generator.py
```

This functionality allows dashboard information and important operational insights to be converted into a **PDF report**.

The PDF reporting functionality can be used to create a summarized report for hospital management and decision-making.

---

# 🎨 Design System

The dashboard uses a centralized styling system:

```text
utils/styling.py
```

This ensures visual consistency across all pages.

### Main Design Features

* Professional dashboard layout
* Gradient page headers
* KPI cards
* Alert cards
* Interactive chart containers
* Consistent typography
* Responsive layout
* Custom icons
* Highlighted important chart values
* Consistent filter bars
* Soft gradient application background
* Subtle UI animations

The application logo is stored at:

```text
logo.png
```

and is used as part of the dashboard branding.

---

# 📂 Dataset

The project includes a sample hospital dataset:

```text
data/Hospital_Dataset_Complete_Project.xlsx
```

The application expects the following exact worksheet names:

```text
Hospital_Visits
laboratory data
pharmacy data
Ambulance_Transportation
Staff_Scheduling
Appointments
OT_Dashboard
ER_Monitoring_Summary
```

The dataset can either be:

1. Used directly from the bundled `data/` folder, or
2. Replaced/uploaded through the dashboard using the file uploader.

No code changes are required as long as the replacement workbook follows the expected sheet and column structure.

---

# 🛠️ Technology Stack

| Technology       | Purpose                                   |
| ---------------- | ----------------------------------------- |
| **Python**       | Core programming language                 |
| **Streamlit**    | Interactive dashboard and web application |
| **Pandas**       | Data loading, cleaning and analysis       |
| **Plotly**       | Interactive data visualization            |
| **OpenPyXL**     | Excel file processing                     |
| **ReportLab**    | PDF report generation                     |
| **Git & GitHub** | Version control and project hosting       |

---

# ⚙️ Installation

## Requirements

* Python 3.10 or higher
* pip
* Git

---

## 1. Clone the Repository

```bash
git clone https://github.com/ukashazarar/Health_Care_Intelligence_Dashboard.git
```

Move into the project directory:

```bash
cd Health_Care_Intelligence_Dashboard
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Configure Credentials

The repository contains:

```text
.streamlit/secrets.toml.example
```

Create your local secrets file by copying the example.

### Windows

```bash
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
```

### Linux / macOS

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Then open:

```text
.streamlit/secrets.toml
```

and configure your credentials.

> **Important:** Never push `secrets.toml` to GitHub.

The `.gitignore` file already excludes:

```text
.streamlit/secrets.toml
```

---

# ▶️ Run the Application

Start the Streamlit application using:

```bash
streamlit run Home.py
```

The application will normally be available at:

```text
http://localhost:8501
```

Open the URL in your browser.

### Demo Login

```text
Username: admin
Password: admin123
```

---

# ☁️ Deploy on Streamlit Community Cloud

The project can be deployed using Streamlit Community Cloud.

### Steps

1. Push the project to GitHub.
2. Open Streamlit Community Cloud.
3. Select **New App**.
4. Select the GitHub repository.
5. Select the `main` branch.
6. Set the main file to:

```text
Home.py
```

7. Deploy the application.
8. Open the application's **Settings → Secrets** section.
9. Add the required credentials there.
10. Save and redeploy if required.

The deployment environment will install the dependencies from:

```text
requirements.txt
```

Do **not** upload or commit your local `.streamlit/secrets.toml`.

---

# 🔒 Security

This project follows basic credential-protection practices.

The following files and directories should not be committed:

```text
venv/
.venv/
__pycache__/
*.pyc
.env
.streamlit/secrets.toml
```

The repository should only contain:

```text
.streamlit/secrets.toml.example
```

as the example configuration.

If real credentials are accidentally pushed to GitHub, they should be considered compromised and replaced immediately.

---

# 🧪 Troubleshooting

| Problem                     | Solution                                             |
| --------------------------- | ---------------------------------------------------- |
| `ModuleNotFoundError`       | Run `pip install -r requirements.txt`                |
| Login fails                 | Check `.streamlit/secrets.toml`                      |
| Dataset not loading         | Verify the Excel file and worksheet names            |
| Blank/old data after upload | Refresh the browser                                  |
| Port already in use         | Run `streamlit run Home.py --server.port 8502`       |
| `No dataset loaded yet`     | Open the Overview page first                         |
| PDF generation error        | Verify the required PDF dependencies are installed   |
| Streamlit deployment fails  | Check `requirements.txt` and Streamlit Cloud secrets |

---

# 🚀 Future Scope

Possible future improvements include:

* Real-time hospital database integration
* Role-based access control
* Advanced predictive analytics
* Patient admission forecasting
* Emergency demand prediction
* Medicine demand forecasting
* Staff requirement prediction
* Automated email reports
* Database integration
* Cloud-based deployment
* Advanced anomaly detection
* Machine learning-based decision support
* Real-time hospital IoT integration

---

# 🎯 Project Objective

The main objective of the **Health Care Operation Intelligence Dashboard** is to transform fragmented hospital operational data into a centralized decision-support system.

Instead of manually analyzing spreadsheets, hospital administrators can monitor important operational metrics through a single interactive dashboard and quickly identify:

* Operational bottlenecks
* Increasing workload
* Emergency trends
* Appointment issues
* Resource utilization
* Staff workload
* Pharmacy demand
* Laboratory performance
* Patient-related trends

This enables **faster, clearer, and more data-driven operational decisions**.

---

# 📌 One-Line Summary

> **A Python and Streamlit Business Intelligence system that transforms hospital operational data into a secure, interactive dashboard with decision-grade KPIs, intelligent alerts, interactive visualizations, and PDF reporting for faster data-driven healthcare operations.**

---

# 📜 License

This project is licensed under the **MIT License**.

See the [`LICENSE`](LICENSE) file for details.

---

## 👨‍💻 Author

**Ukasha Ansari**

Health Care Operation Intelligence Dashboard
Built with Python, Streamlit, Pandas, Plotly and OpenPyXL.
