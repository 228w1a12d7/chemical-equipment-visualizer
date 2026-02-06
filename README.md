# Chemical Equipment Parameter Visualizer

A hybrid Web + Desktop application for visualizing and analyzing chemical equipment data. Upload CSV files containing equipment parameters and get instant analytics, visualizations, and PDF reports.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2+-green.svg)
![React](https://img.shields.io/badge/React-18.2+-61dafb.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-41cd52.svg)

---

## 🌐 Live Demo

| Component | URL | Status |
|-----------|-----|--------|
| **Web Frontend** | [https://frontend-web-nu-blue.vercel.app](https://frontend-web-nu-blue.vercel.app) | ✅ Live |
| **API Backend** | [https://chemical-equipment-api-production.up.railway.app](https://chemical-equipment-api-production.up.railway.app) | ✅ Live |

### Backend Test Credentials
- **Username:** `admin`
- **Password:** `admin123`

> **Both frontend and backend are fully deployed and connected!** You can test the complete application at the Web Frontend URL above.

---

## 📋 Features

- **CSV Upload**: Upload equipment data files with drag-and-drop support (Web) or file picker (Desktop)
- **Data Summary API**: View total count, averages, and equipment type distribution
- **Interactive Visualizations**: Charts using Chart.js (Web) and Matplotlib (Desktop)
  - Pie chart for equipment type distribution
  - Bar chart for average parameters by type
  - Line chart for equipment parameters overview
- **History Management**: Store and access the last 5 uploaded datasets
- **PDF Reports**: Generate downloadable PDF reports with summaries and data tables
- **Authentication**: User registration and login with token-based authentication
- **Logout Confirmation**: Modal dialog to confirm logout action
- **Dual Frontend**: Both Web (React) and Desktop (PyQt5) interfaces
- **Responsive Design**: Modern UI with smooth animations

---

## 🏗️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend (Web) | React.js + Chart.js | Interactive web interface with charts |
| Frontend (Desktop) | PyQt5 + Matplotlib | Native desktop application |
| Backend | Django + Django REST Framework | REST API server |
| Data Handling | Pandas | CSV parsing and analytics |
| Database | SQLite | Store uploaded datasets |
| PDF Generation | ReportLab | Generate PDF reports |

---

## 🚀 Quick Start (Run Locally)

### Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- npm or yarn

### 1. Clone the Repository

```bash
git clone https://github.com/228w1a12d7/chemical-equipment-visualizer.git
cd chemical-equipment-visualizer
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

The backend API will be running at `http://localhost:8000/api/`

### 3. Web Frontend Setup

```bash
# Open a new terminal and navigate to frontend-web
cd frontend-web

# Install dependencies
npm install

# Start the development server
npm start
```

The web application will be running at `http://localhost:3000`

### 4. Desktop Frontend Setup

```bash
# Open a new terminal and navigate to frontend-desktop
cd frontend-desktop

# Install dependencies (use the same venv or create new)
pip install -r requirements.txt

# Run the application
python main.py
```

---

## 📊 Sample Data

A sample CSV file (`sample_equipment_data.csv`) is included for testing:

```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Reactor-001,Reactor,150.5,25.3,180.0
Pump-001,Pump,200.0,45.0,25.0
HeatExchanger-001,Heat Exchanger,350.0,15.2,120.5
```

| Column | Description | Example |
|--------|-------------|---------|
| Equipment Name | Unique identifier | Reactor-001 |
| Type | Equipment type | Reactor, Pump, Heat Exchanger |
| Flowrate | Flow rate value | 150.5 |
| Pressure | Pressure value | 25.3 |
| Temperature | Temperature value | 180.0 |

---

## 🔌 API Endpoints

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | Register new user |
| `/api/auth/login/` | POST | Login user |
| `/api/auth/logout/` | POST | Logout user |
| `/api/auth/user/` | GET | Get current user info |

### Data Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload/` | POST | Upload CSV file |
| `/api/datasets/` | GET | Get upload history (last 5) |
| `/api/datasets/{id}/` | GET | Get specific dataset |
| `/api/datasets/{id}/delete/` | DELETE | Delete a dataset |
| `/api/datasets/{id}/pdf/` | GET | Download PDF report |

### Example Response (Upload):
```json
{
  "message": "File uploaded successfully",
  "dataset_id": 1,
  "summary": {
    "total_equipment": 25,
    "avg_flowrate": 234.62,
    "avg_pressure": 31.34,
    "avg_temperature": 82.66,
    "type_distribution": {
      "Reactor": 5,
      "Pump": 4,
      "Heat Exchanger": 3
    }
  }
}
```

---

## 🧪 Testing Instructions

### For Interviewers/Reviewers:

**Option A: Run Everything Locally (Recommended)**
```bash
# Terminal 1 - Backend
cd backend && pip install -r requirements.txt && python manage.py migrate && python manage.py runserver

# Terminal 2 - Frontend
cd frontend-web && npm install && npm start

# Open browser: http://localhost:3000
```

**Option B: Use Live Frontend with Local Backend**
1. Start backend locally (see above)
2. Visit: https://frontend-web-nu-blue.vercel.app
3. The frontend will connect to `localhost:8000` by default

**Test Flow:**
1. Register a new account
2. Login with your credentials
3. Upload `sample_equipment_data.csv`
4. View charts and statistics
5. Download PDF report
6. Check upload history

---

## 📁 Project Structure

```
chemical-equipment-visualizer/
├── backend/                    # Django Backend
│   ├── chemical_visualizer/    # Django project settings
│   ├── api/                    # REST API app
│   ├── manage.py
│   └── requirements.txt
├── frontend-web/               # React Web Frontend
│   ├── src/
│   │   ├── components/         # Charts, DataTable, FileUpload
│   │   ├── pages/              # Dashboard, Login, Register
│   │   └── services/           # API client
│   └── package.json
├── frontend-desktop/           # PyQt5 Desktop Frontend
│   ├── main.py
│   ├── api_service.py
│   └── requirements.txt
├── sample_equipment_data.csv   # Sample test data
└── README.md
```

---

## 🚀 Deployment

### Deploy Backend to Render (Free)

1. Go to [render.com](https://render.com) → Sign up with GitHub
2. Click **"New +"** → **"Web Service"**
3. Select repository: `chemical-equipment-visualizer`
4. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt && python manage.py migrate`
   - **Start Command**: `gunicorn chemical_visualizer.wsgi:application`
5. Add environment variables:
   - `DJANGO_SECRET_KEY`: (generate a random key)
   - `CORS_ALLOW_ALL`: `true`
6. Deploy!

### Deploy Frontend to Vercel (Free)

```bash
cd frontend-web
npm install -g vercel
vercel --prod
```

---
## 👨‍💻 Author

**Kundana Sree Bavisetti**
- Gmail: [kundanasree3989@gmail.com](kundanasree3989@gmail.com)
---

## 📞 Support

For questions or issues, [open an issue](kundanasree3989@gmail.com) on GitHub.
