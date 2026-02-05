# Chemical Equipment Parameter Visualizer

A hybrid Web + Desktop application for visualizing and analyzing chemical equipment data. Upload CSV files containing equipment parameters and get instant analytics, visualizations, and PDF reports.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2+-green.svg)
![React](https://img.shields.io/badge/React-18.2+-61dafb.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-41cd52.svg)

## 📋 Features

- **CSV Upload**: Upload equipment data files with drag-and-drop support (Web) or file picker (Desktop)
- **Data Summary API**: View total count, averages, and equipment type distribution
- **Interactive Visualizations**: Charts using Chart.js (Web) and Matplotlib (Desktop)
- **History Management**: Store and access the last 5 uploaded datasets
- **PDF Reports**: Generate downloadable PDF reports with summaries and data tables
- **Authentication**: User registration and login with token-based authentication
- **Dual Frontend**: Both Web (React) and Desktop (PyQt5) interfaces

## 🏗️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend (Web) | React.js + Chart.js | Interactive web interface with charts |
| Frontend (Desktop) | PyQt5 + Matplotlib | Native desktop application |
| Backend | Django + Django REST Framework | REST API server |
| Data Handling | Pandas | CSV parsing and analytics |
| Database | SQLite | Store uploaded datasets |
| PDF Generation | ReportLab | Generate PDF reports |

## 📁 Project Structure

```
chemical-equipment-visualizer/
├── backend/                    # Django Backend
│   ├── chemical_visualizer/    # Django project settings
│   │   ├── settings.py         # Development settings
│   │   ├── settings_prod.py    # Production settings
│   │   ├── urls.py             # Main URL configuration
│   │   └── wsgi.py             # WSGI application
│   ├── api/                    # REST API app
│   │   ├── models.py           # Database models
│   │   ├── views.py            # API views
│   │   ├── serializers.py      # DRF serializers
│   │   └── urls.py             # API routes
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend-web/               # React Web Frontend
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/         # Reusable components
│   │   │   ├── Charts/         # Chart.js visualizations
│   │   │   ├── DataTable/      # Data table component
│   │   │   └── FileUpload/     # CSV upload component
│   │   ├── context/            # Auth context
│   │   ├── pages/              # Page components
│   │   │   ├── Dashboard.js    # Main dashboard
│   │   │   ├── Login.js        # Login page
│   │   │   └── Register.js     # Registration page
│   │   ├── services/           # API service
│   │   │   └── api.js          # Axios API client
│   │   └── App.js
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── frontend-desktop/           # PyQt5 Desktop Frontend
│   ├── main.py                 # Main application
│   ├── api_service.py          # API client
│   └── requirements.txt
├── sample_equipment_data.csv   # Sample data for testing
├── docker-compose.yml          # Docker deployment
├── render.yaml                 # Render.com deployment
├── railway.toml                # Railway deployment
├── netlify.toml                # Netlify deployment
├── vercel.json                 # Vercel deployment
├── deploy.sh                   # Local deployment script
├── stop.sh                     # Stop services script
├── build.sh                    # Build script
└── README.md
```

## 🚀 Quick Start

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

## 📊 Sample Data

A sample CSV file (`sample_equipment_data.csv`) is included for testing. The CSV contains 25 equipment records with these columns:

| Column | Description | Example |
|--------|-------------|---------|
| Equipment Name | Unique identifier | Reactor-001 |
| Type | Equipment type | Reactor, Pump, Heat Exchanger |
| Flowrate | Flow rate value | 150.5 |
| Pressure | Pressure value | 25.3 |
| Temperature | Temperature value | 180.0 |

### Sample Data Preview:
```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Reactor-001,Reactor,150.5,25.3,180.0
Pump-001,Pump,200.0,45.0,25.0
HeatExchanger-001,Heat Exchanger,350.0,15.2,120.5
```

## 🔌 API Endpoints

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | Register new user (requires: username, email, password, password_confirm) |
| `/api/auth/login/` | POST | Login user (requires: username, password) |
| `/api/auth/logout/` | POST | Logout user |
| `/api/auth/user/` | GET | Get current user info |

### Data Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload/` | POST | Upload CSV file (multipart/form-data) |
| `/api/datasets/` | GET | Get upload history (last 5 datasets) |
| `/api/datasets/{id}/` | GET | Get specific dataset with equipment list |
| `/api/datasets/{id}/delete/` | DELETE | Delete a dataset |
| `/api/datasets/{id}/pdf/` | GET | Download PDF report |

### Example API Response (Upload):
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

## 🔐 Authentication

The application uses token-based authentication:

1. Register a new account or login
2. The token is stored locally (localStorage for web, memory for desktop)
3. All API requests include the token in the `Authorization: Token <token>` header
4. Tokens can be invalidated by logging out

## 🧪 Testing the Application

### Quick Test Steps:

1. **Start Backend**: 
   ```bash
   cd backend && python manage.py runserver
   ```

2. **Start Frontend** (in new terminal):
   ```bash
   cd frontend-web && npm start
   ```

3. **Open Browser**: Go to `http://localhost:3000`

4. **Register**: Create a new account

5. **Upload CSV**: Use `sample_equipment_data.csv` from the project root

6. **View Results**: See statistics, charts, and download PDF report

## 🚀 Deployment

### Option 1: Deploy to Render (Recommended - Free Tier)

#### Step 1: Deploy Backend
1. Go to [render.com](https://render.com) and sign up
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account and select `chemical-equipment-visualizer`
4. Configure:
   - **Name**: `chemical-visualizer-api`
   - **Root Directory**: `backend`
   - **Build Command**: 
     ```
     pip install -r requirements.txt && pip install gunicorn whitenoise && python manage.py migrate && python manage.py collectstatic --noinput
     ```
   - **Start Command**: `gunicorn chemical_visualizer.wsgi:application`
5. Add Environment Variables:
   | Key | Value |
   |-----|-------|
   | `DJANGO_SETTINGS_MODULE` | `chemical_visualizer.settings_prod` |
   | `DJANGO_SECRET_KEY` | `your-secret-key-min-50-chars` |
   | `CORS_ALLOW_ALL` | `true` |
6. Click **"Create Web Service"**

#### Step 2: Deploy Frontend
1. Click **"New +"** → **"Static Site"**
2. Select same repository
3. Configure:
   - **Name**: `chemical-visualizer-web`
   - **Root Directory**: `frontend-web`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `build`
4. Add Environment Variable:
   | Key | Value |
   |-----|-------|
   | `REACT_APP_API_URL` | `https://YOUR-BACKEND-NAME.onrender.com/api` |
5. Click **"Create Static Site"**

### Option 2: Local Production Deployment

```bash
# Terminal 1: Start Backend
cd backend
pip install gunicorn whitenoise
python manage.py migrate
gunicorn chemical_visualizer.wsgi:application --bind 0.0.0.0:8000

# Terminal 2: Build and Serve Frontend
cd frontend-web
npm install && npm run build
npx serve -s build -l 3000
```

### Option 3: Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 📱 Desktop Application Features

The PyQt5 desktop application includes:
- **Login/Register dialogs** with form validation
- **File browser** for CSV selection
- **Data table** with sortable columns
- **Statistics cards** showing averages
- **Matplotlib charts**: Pie chart, Bar chart, Line chart
- **History panel** showing last 5 uploads
- **PDF download** functionality

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Kundana Sree**
- GitHub: [@228w1a12d7](https://github.com/228w1a12d7)

## 📞 Support

For questions or issues, please [open an issue](https://github.com/228w1a12d7/chemical-equipment-visualizer/issues) on GitHub.
