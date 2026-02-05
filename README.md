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
│   ├── api/                    # REST API app
│   │   ├── models.py           # Database models
│   │   ├── views.py            # API views
│   │   ├── serializers.py      # DRF serializers
│   │   └── urls.py             # API routes
│   ├── manage.py
│   └── requirements.txt
├── frontend-web/               # React Web Frontend
│   ├── public/
│   ├── src/
│   │   ├── components/         # Reusable components
│   │   ├── context/            # Auth context
│   │   ├── pages/              # Page components
│   │   ├── services/           # API service
│   │   └── App.js
│   └── package.json
├── frontend-desktop/           # PyQt5 Desktop Frontend
│   ├── main.py                 # Main application
│   ├── api_service.py          # API client
│   └── requirements.txt
├── sample_equipment_data.csv   # Sample data for testing
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- npm or yarn

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/chemical-equipment-visualizer.git
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

# Create a superuser (optional, for admin access)
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

The backend API will be running at `http://localhost:8000/api/`

### 3. Web Frontend Setup

```bash
# Open a new terminal
cd frontend-web

# Install dependencies
npm install

# Start the development server
npm start
```

The web application will be running at `http://localhost:3000`

### 4. Desktop Frontend Setup

```bash
# Open a new terminal
cd frontend-desktop

# Create virtual environment (or use the same as backend)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## 📊 Sample Data

A sample CSV file (`sample_equipment_data.csv`) is included for testing. The CSV must contain these columns:

| Column | Description |
|--------|-------------|
| Equipment Name | Unique identifier for the equipment |
| Type | Equipment type (e.g., Reactor, Pump, Heat Exchanger) |
| Flowrate | Flow rate value (numeric) |
| Pressure | Pressure value (numeric) |
| Temperature | Temperature value (numeric) |

## 🔌 API Endpoints

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | Register new user |
| `/api/auth/login/` | POST | Login user |
| `/api/auth/logout/` | POST | Logout user |
| `/api/auth/user/` | GET | Get current user info |

### Data

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload/` | POST | Upload CSV file |
| `/api/datasets/` | GET | Get upload history (last 5) |
| `/api/datasets/{id}/` | GET | Get specific dataset |
| `/api/datasets/{id}/delete/` | DELETE | Delete dataset |
| `/api/datasets/{id}/pdf/` | GET | Download PDF report |

## 📸 Screenshots

### Web Application
- **Dashboard**: Upload CSV files and view data summary
- **Data View**: Table view with statistics cards
- **Charts**: Interactive pie charts and bar graphs
- **History**: Access previous uploads

### Desktop Application
- **Login**: Secure authentication
- **Upload**: File picker for CSV selection
- **Data View**: Table and statistics
- **Charts**: Matplotlib visualizations

## 🔐 Authentication

The application uses token-based authentication:

1. Register a new account or login
2. The token is stored locally
3. All API requests include the token in the `Authorization` header
4. Tokens can be invalidated by logging out

## 🧪 Testing

### Backend Tests

```bash
cd backend
python manage.py test
```

### Using Sample Data

1. Start the backend server
2. Launch either the web or desktop frontend
3. Register/Login with a test account
4. Upload the `sample_equipment_data.csv` file
5. View the generated statistics and charts

## 🚀 Deployment

### Backend (Production)

```bash
# Update settings for production
# Set DEBUG = False
# Configure ALLOWED_HOSTS
# Use a production database

pip install gunicorn
gunicorn chemical_visualizer.wsgi:application
```

### Web Frontend (Production)

```bash
cd frontend-web
npm run build
# Serve the build folder with nginx or similar
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django REST Framework for the excellent API toolkit
- React and Chart.js for web visualizations
- PyQt5 and Matplotlib for desktop capabilities
- Pandas for data processing

## 📞 Support

For questions or issues, please open an issue on GitHub.
