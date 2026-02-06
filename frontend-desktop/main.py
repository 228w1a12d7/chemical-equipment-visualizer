"""
Chemical Equipment Parameter Visualizer - Desktop Application
PyQt5-based desktop client for the Chemical Equipment Visualizer
"""

import sys
import os
from typing import Optional, Dict, Any, List

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTabWidget, QTableWidget,
    QTableWidgetItem, QFileDialog, QMessageBox, QDialog,
    QFormLayout, QListWidget, QListWidgetItem, QGroupBox,
    QSplitter, QFrame, QHeaderView, QSizePolicy, QScrollArea,
    QDateEdit, QComboBox, QSpinBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QColor, QPalette

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from api_service import api


# Color schemes for light and dark mode
LIGHT_COLORS = {
    'primary': '#4f46e5',
    'secondary': '#6366f1',
    'success': '#10b981',
    'danger': '#ef4444',
    'warning': '#f59e0b',
    'background': '#f1f5f9',
    'card': '#ffffff',
    'text': '#1e293b',
    'text_secondary': '#64748b',
    'sidebar': '#1e293b',
    'table_header': '#4f46e5',
    'table_alt': '#f8fafc',
    'border': '#e2e8f0',
}

DARK_COLORS = {
    'primary': '#818cf8',
    'secondary': '#6366f1',
    'success': '#34d399',
    'danger': '#f87171',
    'warning': '#fbbf24',
    'background': '#0f172a',
    'card': '#1e293b',
    'text': '#f1f5f9',
    'text_secondary': '#94a3b8',
    'sidebar': '#020617',
    'table_header': '#4f46e5',
    'table_alt': '#334155',
    'border': '#334155',
}

# Default to light mode
COLORS = LIGHT_COLORS.copy()

# Vibrant colors for impressive charts
CHART_COLORS = [
    '#4f46e5',  # Indigo
    '#06b6d4',  # Cyan
    '#10b981',  # Emerald
    '#f59e0b',  # Amber
    '#ef4444',  # Red
    '#8b5cf6',  # Purple
    '#ec4899',  # Pink
    '#14b8a6',  # Teal
    '#f97316',  # Orange
    '#6366f1',  # Violet
    '#84cc16',  # Lime
    '#0ea5e9',  # Sky
]


def show_styled_message(parent, title, message, msg_type="info"):
    """Show a styled message dialog with visible fonts."""
    dialog = QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setFixedSize(400, 180)
    dialog.setStyleSheet(f"""
        QDialog {{
            background-color: white;
        }}
        QLabel {{
            color: #1e293b;
            font-size: 14px;
        }}
        QPushButton {{
            background-color: {COLORS['primary']};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 30px;
            font-size: 14px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {COLORS['secondary']};
        }}
    """)
    
    layout = QVBoxLayout(dialog)
    layout.setSpacing(20)
    layout.setContentsMargins(30, 30, 30, 30)
    
    # Icon and message
    icon_text = "✓" if msg_type == "info" else "⚠"
    icon_color = COLORS['success'] if msg_type == "info" else COLORS['warning']
    
    icon_label = QLabel(icon_text)
    icon_label.setStyleSheet(f"font-size: 36px; color: {icon_color};")
    icon_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(icon_label)
    
    msg_label = QLabel(message)
    msg_label.setStyleSheet("font-size: 15px; color: #1e293b; font-weight: 500;")
    msg_label.setAlignment(Qt.AlignCenter)
    msg_label.setWordWrap(True)
    layout.addWidget(msg_label)
    
    # OK button
    ok_btn = QPushButton("OK")
    ok_btn.setFixedWidth(100)
    ok_btn.clicked.connect(dialog.accept)
    
    btn_layout = QHBoxLayout()
    btn_layout.addStretch()
    btn_layout.addWidget(ok_btn)
    btn_layout.addStretch()
    layout.addLayout(btn_layout)
    
    dialog.exec_()


class WorkerThread(QThread):
    """Thread for background API calls."""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class LoginDialog(QDialog):
    """Login dialog window."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login - Chemical Equipment Visualizer")
        self.setFixedSize(400, 350)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("🔬 Chemical Equipment Visualizer")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Sign in to your account")
        subtitle.setStyleSheet(f"color: {COLORS['text_secondary']};")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setMinimumHeight(40)
        form_layout.addRow("Username:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        form_layout.addRow("Password:", self.password_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.login_btn = QPushButton("Login")
        self.login_btn.setMinimumHeight(40)
        self.login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
        """)
        self.login_btn.clicked.connect(self.handle_login)
        btn_layout.addWidget(self.login_btn)
        
        self.register_btn = QPushButton("Register")
        self.register_btn.setMinimumHeight(40)
        self.register_btn.clicked.connect(self.show_register)
        btn_layout.addWidget(self.register_btn)
        
        layout.addLayout(btn_layout)
        
        # Enter key triggers login
        self.password_input.returnPressed.connect(self.handle_login)
    
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return
        
        self.login_btn.setEnabled(False)
        self.login_btn.setText("Logging in...")
        
        result = api.login(username, password)
        
        self.login_btn.setEnabled(True)
        self.login_btn.setText("Login")
        
        if result["success"]:
            self.accept()
        else:
            error_msg = result.get("error", "Invalid credentials")
            if "not found" in error_msg.lower() or "sign up" in error_msg.lower():
                reply = QMessageBox.question(
                    self, "User Not Found",
                    "User not found. Would you like to sign up?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.show_register()
            else:
                QMessageBox.warning(self, "Login Failed", error_msg)
    
    def show_register(self):
        dialog = RegisterDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.accept()


class RegisterDialog(QDialog):
    """Registration dialog window."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register - Chemical Equipment Visualizer")
        self.setFixedSize(400, 420)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("Create Account")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choose a username")
        self.username_input.setMinimumHeight(40)
        form_layout.addRow("Username:", self.username_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        self.email_input.setMinimumHeight(40)
        form_layout.addRow("Email:", self.email_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Create a password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        form_layout.addRow("Password:", self.password_input)
        
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirm password")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setMinimumHeight(40)
        form_layout.addRow("Confirm:", self.confirm_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.register_btn = QPushButton("Register")
        self.register_btn.setMinimumHeight(40)
        self.register_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
        """)
        self.register_btn.clicked.connect(self.handle_register)
        btn_layout.addWidget(self.register_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumHeight(40)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def handle_register(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        if not username or not email or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters")
            return
        
        self.register_btn.setEnabled(False)
        self.register_btn.setText("Registering...")
        
        result = api.register(username, email, password)
        
        self.register_btn.setEnabled(True)
        self.register_btn.setText("Register")
        
        if result["success"]:
            QMessageBox.information(self, "Success", "Account created successfully!")
            self.accept()
        else:
            error_msg = str(result.get("error", "Registration failed"))
            QMessageBox.warning(self, "Registration Failed", error_msg)


class LogoutConfirmDialog(QDialog):
    """Custom styled logout confirmation dialog."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Logout")
        self.setFixedSize(350, 200)
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet(f"""
            QDialog {{
                background-color: white;
                border-radius: 12px;
            }}
            QLabel {{
                color: #1e293b;
            }}
            QPushButton {{
                min-height: 40px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Icon
        icon_label = QLabel("🚪")
        icon_label.setFont(QFont("Arial", 36))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Message
        message = QLabel("Are you sure you want to logout?")
        message.setFont(QFont("Arial", 14))
        message.setAlignment(Qt.AlignCenter)
        message.setStyleSheet("color: #374151; margin: 10px 0;")
        layout.addWidget(message)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #e5e7eb;
                color: #374151;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #d1d5db;
            }}
        """)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        self.logout_btn = QPushButton("Yes, Logout")
        self.logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['danger']};
                color: white;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #dc2626;
            }}
        """)
        self.logout_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.logout_btn)
        
        layout.addLayout(btn_layout)


class ChartCanvas(FigureCanvas):
    """Matplotlib canvas for embedding charts in Qt."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='white')
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.fig.patch.set_facecolor('white')
        self.axes.set_facecolor('#fafafa')
        self.fig.set_tight_layout(True)
        self.setMinimumHeight(int(height * dpi * 0.9))


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.current_data = None
        self.selected_dataset_id = None
        self.dark_mode = False
        self.date_filter_start = None
        self.date_filter_end = None
        self.setup_ui()
        self.load_history()
    
    def setup_ui(self):
        self.setWindowTitle("Chemical Equipment Parameter Visualizer")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(f"background-color: {COLORS['background']};")
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Content area
        content = QWidget()
        content.setStyleSheet(f"background-color: {COLORS['background']};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = self.create_header()
        content_layout.addWidget(header)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { 
                border: none; 
                background: white; 
                border-radius: 8px; 
            }
            QTabBar::tab { 
                padding: 12px 30px; 
                margin-right: 10px; 
                background: #e2e8f0;
                color: #1e293b;
                font-size: 14px;
                font-weight: 600;
                border-radius: 6px;
                min-width: 80px;
            }
            QTabBar::tab:selected { 
                background: #4f46e5; 
                color: white; 
                border-radius: 6px; 
            }
            QTabBar::tab:hover:!selected {
                background: #cbd5e1;
            }
        """)
        
        self.tabs.addTab(self.create_upload_tab(), "  Upload  ")
        self.tabs.addTab(self.create_data_tab(), "  Data  ")
        self.tabs.addTab(self.create_charts_tab(), "  Charts  ")
        self.tabs.addTab(self.create_history_tab(), "  History  ")
        
        content_layout.addWidget(self.tabs)
        main_layout.addWidget(content, 1)
    
    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(180)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['sidebar']};
                color: white;
            }}
        """)
        sidebar.setObjectName("sidebar")
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 30, 20, 30)
        layout.setSpacing(20)
        
        # Brand
        brand = QLabel("🔬 Chemical Viz")
        brand.setFont(QFont("Arial", 14, QFont.Bold))
        brand.setStyleSheet("color: white;")
        layout.addWidget(brand)
        
        layout.addStretch()
        
        # Dark mode toggle
        self.dark_mode_btn = QPushButton("🌙 Dark Mode")
        self.dark_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: 1px solid white;
                border-radius: 6px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.dark_mode_btn.clicked.connect(self.toggle_dark_mode)
        layout.addWidget(self.dark_mode_btn)
        
        # Logout button
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: 1px solid white;
                border-radius: 6px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        logout_btn.clicked.connect(self.handle_logout)
        layout.addWidget(logout_btn)
        
        return sidebar
    
    def create_header(self):
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card']};
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }}
        """)
        header.setFixedHeight(70)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(25, 0, 25, 0)
        
        title = QLabel("Chemical Equipment Parameter Visualizer")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text']};")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # User info placeholder
        user_label = QLabel("👤 Logged In")
        user_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px;")
        layout.addWidget(user_label)
        
        return header
    
    def create_upload_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Upload area container
        upload_container = QFrame()
        upload_container.setStyleSheet(f"""
            QFrame {{
                background-color: #f8fafc;
                border: 2px dashed {COLORS['primary']};
                border-radius: 16px;
            }}
        """)
        upload_container.setMinimumHeight(350)
        
        upload_layout = QVBoxLayout(upload_container)
        upload_layout.setAlignment(Qt.AlignCenter)
        upload_layout.setSpacing(20)
        upload_layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title_label = QLabel("📤 Upload CSV File")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet(f"color: {COLORS['primary']}; background: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        upload_layout.addWidget(title_label)
        
        # Icon
        icon_label = QLabel("📁")
        icon_label.setFont(QFont("Arial", 56))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("background: transparent;")
        upload_layout.addWidget(icon_label)
        
        # File status label
        self.file_label = QLabel("No file selected")
        self.file_label.setAlignment(Qt.AlignCenter)
        self.file_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px; background: transparent;")
        upload_layout.addWidget(self.file_label)
        
        # Buttons container
        btn_container = QWidget()
        btn_container.setStyleSheet("background: transparent;")
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(20)
        
        browse_btn = QPushButton("📂 Browse Files")
        browse_btn.setMinimumSize(180, 52)
        browse_btn.setCursor(Qt.PointingHandCursor)
        browse_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 15px;
                padding: 12px 24px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
            QPushButton:pressed {{
                background-color: #3730a3;
            }}
        """)
        browse_btn.clicked.connect(self.browse_file)
        btn_layout.addWidget(browse_btn)
        
        self.upload_btn = QPushButton("Upload")
        self.upload_btn.setMinimumSize(180, 52)
        self.upload_btn.setEnabled(False)
        self.upload_btn.setCursor(Qt.PointingHandCursor)
        self.upload_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 16px;
                padding: 12px 24px;
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
            QPushButton:pressed {{
                background-color: #047857;
            }}
            QPushButton:disabled {{
                background-color: #d1d5db;
                color: #6b7280;
            }}
        """)
        self.upload_btn.clicked.connect(self.upload_file)
        btn_layout.addWidget(self.upload_btn)
        
        upload_layout.addWidget(btn_container)
        
        layout.addWidget(upload_container)
        
        # Instructions
        instructions = QLabel(
            "Supported format: CSV files with columns:\n"
            "equipment_id, equipment_name, equipment_type, flowrate, pressure, temperature"
        )
        instructions.setStyleSheet(f"color: {COLORS['text_secondary']};")
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)
        
        layout.addStretch()
        
        return widget
    
    def create_data_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Stats section
        self.stats_widget = QWidget()
        stats_layout = QHBoxLayout(self.stats_widget)
        stats_layout.setSpacing(20)
        
        self.stat_cards = {}
        stat_configs = [
            ("Total Equipment", "🔧"),
            ("Avg Flowrate", "💧"),
            ("Avg Pressure", "📊"),
            ("Avg Temperature", "🌡️")
        ]
        for stat_name, icon in stat_configs:
            card = self.create_stat_card(f"{icon} {stat_name}", "0")
            self.stat_cards[stat_name] = card
            stats_layout.addWidget(card)
        
        layout.addWidget(self.stats_widget)
        
        # Date filter section
        filter_frame = QFrame()
        filter_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card']};
                border-radius: 8px;
                padding: 10px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(15, 10, 15, 10)
        
        filter_label = QLabel("📅 Date Filter:")
        filter_label.setStyleSheet(f"color: {COLORS['text']}; font-weight: bold;")
        filter_layout.addWidget(filter_label)
        
        start_label = QLabel("Start:")
        start_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        filter_layout.addWidget(start_label)
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        self.start_date_edit.setStyleSheet(f"""
            QDateEdit {{
                padding: 8px;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                background: {COLORS['card']};
                color: {COLORS['text']};
            }}
        """)
        filter_layout.addWidget(self.start_date_edit)
        
        end_label = QLabel("End:")
        end_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        filter_layout.addWidget(end_label)
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setStyleSheet(f"""
            QDateEdit {{
                padding: 8px;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                background: {COLORS['card']};
                color: {COLORS['text']};
            }}
        """)
        filter_layout.addWidget(self.end_date_edit)
        
        self.filter_btn = QPushButton("🔍 Apply Filter")
        self.filter_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
        """)
        self.filter_btn.clicked.connect(self.apply_date_filter)
        filter_layout.addWidget(self.filter_btn)
        
        self.clear_filter_btn = QPushButton("✖ Clear")
        self.clear_filter_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['text_secondary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: #4a5568;
            }}
        """)
        self.clear_filter_btn.clicked.connect(self.clear_date_filter)
        filter_layout.addWidget(self.clear_filter_btn)
        
        filter_layout.addStretch()
        layout.addWidget(filter_frame)
        
        # Actions row with PDF, CSV, and Add Equipment
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 10, 0, 10)
        
        self.pdf_btn = QPushButton("📄 Download PDF Report")
        self.pdf_btn.setMinimumSize(200, 45)
        self.pdf_btn.setEnabled(False)
        self.pdf_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
            QPushButton:disabled {{
                background-color: #d1d5db;
            }}
        """)
        self.pdf_btn.clicked.connect(self.download_pdf)
        actions_layout.addWidget(self.pdf_btn)
        
        self.csv_btn = QPushButton("📊 Export as CSV")
        self.csv_btn.setMinimumSize(160, 45)
        self.csv_btn.setEnabled(False)
        self.csv_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
            QPushButton:disabled {{
                background-color: #d1d5db;
            }}
        """)
        self.csv_btn.clicked.connect(self.download_csv)
        actions_layout.addWidget(self.csv_btn)
        
        self.add_equipment_btn = QPushButton("➕ Add Equipment")
        self.add_equipment_btn.setMinimumSize(160, 45)
        self.add_equipment_btn.setEnabled(False)
        self.add_equipment_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['warning']};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: #d97706;
            }}
            QPushButton:disabled {{
                background-color: #d1d5db;
            }}
        """)
        self.add_equipment_btn.clicked.connect(self.show_add_equipment_dialog)
        actions_layout.addWidget(self.add_equipment_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Data table
        self.data_table = QTableWidget()
        self.data_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                font-size: 14px;
                color: #1e293b;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item {
                padding: 15px;
                color: #1e293b;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #4f46e5;
                color: white;
                padding: 16px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QTableWidget::item:selected {
                background-color: #e0e7ff;
                color: #1e293b;
            }
        """)
        self.data_table.verticalHeader().setVisible(False)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setShowGrid(True)
        self.data_table.verticalHeader().setDefaultSectionSize(50)
        self.data_table.setStyleSheet(self.data_table.styleSheet() + """
            QTableWidget::item:alternate {
                background-color: #f8fafc;
            }
        """)
        layout.addWidget(self.data_table)
        
        return widget
    
    def create_stat_card(self, title, value):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card']};
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #e2e8f0;
            }}
        """)
        card.setMinimumHeight(120)
        card.setMinimumWidth(180)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 15, 18, 15)
        layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px; font-weight: bold;")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 26, QFont.Bold))
        value_label.setStyleSheet(f"color: {COLORS['primary']};")
        value_label.setObjectName("value")
        layout.addWidget(value_label)
        
        return card
    
    def create_charts_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Scroll area for charts
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background-color: #f8fafc;
            }
            QScrollBar:vertical {
                background: #e2e8f0;
                width: 14px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background: #94a3b8;
                border-radius: 7px;
                min-height: 40px;
            }
            QScrollBar::handle:vertical:hover {
                background: #64748b;
            }
        """)
        
        charts_widget = QWidget()
        charts_widget.setStyleSheet("background-color: #f8fafc;")
        charts_layout = QVBoxLayout(charts_widget)
        charts_layout.setSpacing(25)
        charts_layout.setContentsMargins(20, 20, 20, 20)
        
        # Styling for group boxes
        group_style = """
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                color: #1e293b;
                border: 2px solid #e2e8f0;
                border-radius: 14px;
                margin-top: 25px;
                padding: 25px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px;
                background-color: white;
            }
        """
        
        # Chart 1: Type Distribution (Pie)
        chart1_group = QGroupBox("📊 Equipment Type Distribution")
        chart1_group.setStyleSheet(group_style)
        chart1_layout = QVBoxLayout(chart1_group)
        chart1_layout.setContentsMargins(20, 30, 20, 20)
        self.pie_chart = ChartCanvas(width=8, height=5)
        chart1_layout.addWidget(self.pie_chart)
        charts_layout.addWidget(chart1_group)
        
        # Chart 2: Parameter Comparison (Bar)
        chart2_group = QGroupBox("📈 Average Parameters by Equipment Type")
        chart2_group.setStyleSheet(group_style)
        chart2_layout = QVBoxLayout(chart2_group)
        chart2_layout.setContentsMargins(20, 30, 20, 20)
        self.bar_chart = ChartCanvas(width=10, height=5)
        chart2_layout.addWidget(self.bar_chart)
        charts_layout.addWidget(chart2_group)
        
        # Chart 3: Parameter Trends (Line)
        chart3_group = QGroupBox("📉 Equipment Parameters Overview")
        chart3_group.setStyleSheet(group_style)
        chart3_layout = QVBoxLayout(chart3_group)
        chart3_layout.setContentsMargins(20, 30, 20, 20)
        self.line_chart = ChartCanvas(width=10, height=5)
        chart3_layout.addWidget(self.line_chart)
        charts_layout.addWidget(chart3_group)
        
        # Add spacer at bottom
        charts_layout.addSpacing(30)
        
        scroll.setWidget(charts_widget)
        layout.addWidget(scroll)
        
        return widget
    
    def create_history_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header section with card styling
        header_card = QFrame()
        header_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card']};
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }}
        """)
        header_card_layout = QHBoxLayout(header_card)
        header_card_layout.setContentsMargins(20, 15, 20, 15)
        
        header = QLabel("📋 Recent Uploads (Last 5)")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet(f"color: {COLORS['text']};")
        header_card_layout.addWidget(header)
        
        header_card_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setMinimumSize(120, 40)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
        """)
        refresh_btn.clicked.connect(self.load_history)
        header_card_layout.addWidget(refresh_btn)
        
        layout.addWidget(header_card)
        
        # History list with more height
        self.history_list = QListWidget()
        self.history_list.setMinimumHeight(300)
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                font-size: 14px;
                color: #1e293b;
            }
            QListWidget::item {
                padding: 20px;
                border-bottom: 1px solid #e2e8f0;
                color: #1e293b;
                font-size: 14px;
                min-height: 60px;
            }
            QListWidget::item:selected {
                background-color: #e0e7ff;
                color: #1e293b;
            }
            QListWidget::item:hover {
                background-color: #f1f5f9;
            }
        """)
        self.history_list.itemDoubleClicked.connect(self.load_dataset_from_history)
        layout.addWidget(self.history_list, stretch=1)
        
        # Tips section to fill empty space
        tips_card = QFrame()
        tips_card.setStyleSheet(f"""
            QFrame {{
                background-color: #f0f9ff;
                border-radius: 12px;
                border: 1px solid #bae6fd;
            }}
        """)
        tips_layout = QVBoxLayout(tips_card)
        tips_layout.setContentsMargins(20, 15, 20, 15)
        tips_layout.setSpacing(10)
        
        tips_header = QLabel("💡 Tips")
        tips_header.setFont(QFont("Arial", 14, QFont.Bold))
        tips_header.setStyleSheet("color: #0369a1;")
        tips_layout.addWidget(tips_header)
        
        tips_text = QLabel(
            "• Double-click on any dataset to load it\n"
            "• Upload CSV files with equipment data\n"
            "• View charts and statistics in the Data and Charts tabs\n"
            "• Download PDF reports for selected datasets"
        )
        tips_text.setStyleSheet("color: #0c4a6e; font-size: 13px; line-height: 1.5;")
        tips_layout.addWidget(tips_text)
        
        layout.addWidget(tips_card)
        
        # Delete button
        delete_btn = QPushButton("🗑️ Delete Selected")
        delete_btn.setMinimumSize(160, 45)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['danger']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #dc2626;
            }}
        """)
        delete_btn.clicked.connect(self.delete_selected_dataset)
        layout.addWidget(delete_btn, alignment=Qt.AlignRight)
        
        return widget
    
    def browse_file(self):
        """Open file dialog to select CSV file using native macOS picker."""
        try:
            import subprocess
            
            # Use native macOS file picker via AppleScript - guaranteed to work
            script = '''
            tell application "System Events"
                activate
            end tell
            set theFile to choose file with prompt "Select a CSV file" of type {"csv", "CSV", "public.comma-separated-values-text"} default location (path to home folder)
            return POSIX path of theFile
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                file_path = result.stdout.strip()
                self.selected_file = file_path
                filename = os.path.basename(file_path)
                self.file_label.setText(filename)
                self.file_label.setStyleSheet(f"color: {COLORS['success']}; font-size: 14px; font-weight: bold; background: transparent;")
                self.upload_btn.setEnabled(True)
                self.upload_btn.setText("Upload")
            # User cancelled - do nothing
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open file dialog: {str(e)}")
    
    def upload_file(self):
        if not hasattr(self, 'selected_file'):
            return
        
        self.upload_btn.setEnabled(False)
        self.upload_btn.setText("Uploading...")
        
        result = api.upload_csv(self.selected_file)
        
        self.upload_btn.setEnabled(True)
        self.upload_btn.setText("Upload")
        
        if result["success"]:
            self.current_data = result["data"]
            self.selected_dataset_id = result["data"].get("dataset_id")
            self.update_data_display()
            self.update_charts()
            self.load_history()
            self.tabs.setCurrentIndex(1)  # Switch to data tab
            show_styled_message(self, "Success", "File uploaded successfully!", "info")
        else:
            show_styled_message(self, "Upload Failed", result.get("error", "Upload failed"), "warning")
    
    def update_data_display(self):
        if not self.current_data:
            return
        
        summary = self.current_data.get("summary", {})
        equipment_list = self.current_data.get("equipment_list", [])
        
        # Update stats
        self.stat_cards["Total Equipment"].findChild(QLabel, "value").setText(
            str(summary.get("total_equipment", 0))
        )
        self.stat_cards["Avg Flowrate"].findChild(QLabel, "value").setText(
            f"{summary.get('avg_flowrate', 0):.2f}"
        )
        self.stat_cards["Avg Pressure"].findChild(QLabel, "value").setText(
            f"{summary.get('avg_pressure', 0):.2f}"
        )
        self.stat_cards["Avg Temperature"].findChild(QLabel, "value").setText(
            f"{summary.get('avg_temperature', 0):.2f}"
        )
        
        # Update table - without # column, with Edit/Delete actions
        if equipment_list:
            columns = ["id", "name", "type", "flowrate", "pressure", "temperature"]
            column_headers = ["ID", "Equipment Name", "Type", "Flowrate", "Pressure", "Temperature", "Actions"]
            self.data_table.setColumnCount(len(column_headers))
            self.data_table.setHorizontalHeaderLabels(column_headers)
            self.data_table.setRowCount(len(equipment_list))
            
            # Set column widths
            self.data_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
            self.data_table.setColumnWidth(0, 70)  # ID column
            self.data_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Name
            self.data_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # Type
            self.data_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
            self.data_table.setColumnWidth(3, 90)  # Flowrate
            self.data_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
            self.data_table.setColumnWidth(4, 90)  # Pressure
            self.data_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
            self.data_table.setColumnWidth(5, 100)  # Temperature
            self.data_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
            self.data_table.setColumnWidth(6, 140)  # Actions
            
            for row, item in enumerate(equipment_list):
                equipment_id = item.get("id")
                
                # Data columns
                for col, key in enumerate(columns):
                    value = item.get(key, "")
                    table_item = QTableWidgetItem(str(value))
                    table_item.setTextAlignment(Qt.AlignCenter)
                    self.data_table.setItem(row, col, table_item)
                
                # Actions column with Edit and Delete buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 2, 5, 2)
                actions_layout.setSpacing(5)
                
                edit_btn = QPushButton("✏️")
                edit_btn.setFixedSize(35, 30)
                edit_btn.setToolTip("Edit Equipment")
                edit_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['warning']};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 14px;
                    }}
                    QPushButton:hover {{
                        background-color: #d97706;
                    }}
                """)
                edit_btn.clicked.connect(lambda checked, eid=equipment_id, data=item: self.edit_equipment(eid, data))
                actions_layout.addWidget(edit_btn)
                
                delete_btn = QPushButton("🗑️")
                delete_btn.setFixedSize(35, 30)
                delete_btn.setToolTip("Delete Equipment")
                delete_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['danger']};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 14px;
                    }}
                    QPushButton:hover {{
                        background-color: #dc2626;
                    }}
                """)
                delete_btn.clicked.connect(lambda checked, eid=equipment_id: self.delete_equipment(eid))
                actions_layout.addWidget(delete_btn)
                
                actions_layout.addStretch()
                self.data_table.setCellWidget(row, 6, actions_widget)
        
        self.pdf_btn.setEnabled(True)
        self.csv_btn.setEnabled(True)
        self.add_equipment_btn.setEnabled(True)
    
    def update_charts(self):
        if not self.current_data:
            return
        
        summary = self.current_data.get("summary", {})
        equipment_list = self.current_data.get("equipment_list", [])
        type_distribution = summary.get("type_distribution", {})
        
        # Pie Chart - Type Distribution (Enhanced)
        self.pie_chart.axes.clear()
        if type_distribution:
            labels = list(type_distribution.keys())
            sizes = list(type_distribution.values())
            colors = CHART_COLORS[:len(labels)]
            explode = [0.03] * len(labels)  # Slight explosion for all slices
            
            wedges, texts, autotexts = self.pie_chart.axes.pie(
                sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                explode=explode,
                textprops={'fontsize': 11, 'color': '#1e293b'}, 
                pctdistance=0.75,
                shadow=True,
                startangle=90,
                wedgeprops={'edgecolor': 'white', 'linewidth': 2}
            )
            for autotext in autotexts:
                autotext.set_fontsize(10)
                autotext.set_fontweight('bold')
                autotext.set_color('white')
            self.pie_chart.axes.set_title("Equipment Type Distribution", 
                                          fontsize=16, fontweight='bold', color='#1e293b', pad=20)
        self.pie_chart.fig.tight_layout()
        self.pie_chart.draw()
        
        # Bar Chart - Average Parameters by Type (Enhanced)
        self.bar_chart.axes.clear()
        if equipment_list:
            import pandas as pd
            df = pd.DataFrame(equipment_list)
            if 'type' in df.columns:
                grouped = df.groupby('type').agg({
                    'flowrate': 'mean',
                    'pressure': 'mean', 
                    'temperature': 'mean'
                }).reset_index()
                
                x = range(len(grouped))
                width = 0.25
                
                bars1 = self.bar_chart.axes.bar([i - width for i in x], grouped['flowrate'], 
                                        width, label='Flowrate', color=CHART_COLORS[0],
                                        edgecolor='white', linewidth=1)
                bars2 = self.bar_chart.axes.bar(x, grouped['pressure'], 
                                        width, label='Pressure', color=CHART_COLORS[1],
                                        edgecolor='white', linewidth=1)
                bars3 = self.bar_chart.axes.bar([i + width for i in x], grouped['temperature'], 
                                        width, label='Temperature', color=CHART_COLORS[2],
                                        edgecolor='white', linewidth=1)
                
                self.bar_chart.axes.set_xticks(x)
                self.bar_chart.axes.set_xticklabels(grouped['type'], rotation=45, ha='right', fontsize=11)
                self.bar_chart.axes.legend(loc='upper right', fontsize=11, framealpha=0.9)
                self.bar_chart.axes.set_title("Average Parameters by Equipment Type", 
                                              fontsize=16, fontweight='bold', color='#1e293b', pad=20)
                self.bar_chart.axes.set_ylabel("Value", fontsize=12, color='#475569')
                self.bar_chart.axes.set_xlabel("Equipment Type", fontsize=12, color='#475569')
                self.bar_chart.axes.grid(True, axis='y', alpha=0.3, linestyle='--')
                self.bar_chart.axes.set_axisbelow(True)
                
                # Add value labels on bars
                for bars in [bars1, bars2, bars3]:
                    for bar in bars:
                        height = bar.get_height()
                        if height > 0:
                            self.bar_chart.axes.annotate(f'{height:.0f}',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3), textcoords="offset points",
                                ha='center', va='bottom', fontsize=8, fontweight='bold')
        
        self.bar_chart.fig.tight_layout()
        self.bar_chart.draw()
        
        # Line Chart - Equipment Overview (Enhanced)
        self.line_chart.axes.clear()
        if equipment_list:
            x = list(range(len(equipment_list)))
            flowrates = [item.get('flowrate', 0) for item in equipment_list]
            pressures = [item.get('pressure', 0) for item in equipment_list]
            temperatures = [item.get('temperature', 0) for item in equipment_list]
            
            # Plot with fill under lines for modern look
            self.line_chart.axes.fill_between(x, flowrates, alpha=0.15, color=CHART_COLORS[0])
            self.line_chart.axes.plot(x, flowrates, marker='o', label='Flowrate', 
                                      color=CHART_COLORS[0], linewidth=2.5, markersize=7)
            
            self.line_chart.axes.fill_between(x, pressures, alpha=0.15, color=CHART_COLORS[1])
            self.line_chart.axes.plot(x, pressures, marker='s', label='Pressure', 
                                      color=CHART_COLORS[1], linewidth=2.5, markersize=7)
            
            self.line_chart.axes.fill_between(x, temperatures, alpha=0.15, color=CHART_COLORS[2])
            self.line_chart.axes.plot(x, temperatures, marker='^', label='Temperature', 
                                      color=CHART_COLORS[2], linewidth=2.5, markersize=7)
            
            self.line_chart.axes.legend(loc='upper right', fontsize=11, framealpha=0.9)
            self.line_chart.axes.set_xlabel("Equipment Index", fontsize=12, color='#475569')
            self.line_chart.axes.set_ylabel("Value", fontsize=12, color='#475569')
            self.line_chart.axes.set_title("Equipment Parameters Overview", 
                                           fontsize=16, fontweight='bold', color='#1e293b', pad=20)
            self.line_chart.axes.grid(True, alpha=0.3, linestyle='--')
            self.line_chart.axes.set_axisbelow(True)
            
            # Set x-axis ticks for better readability
            if len(x) > 15:
                step = max(1, len(x) // 10)
                self.line_chart.axes.set_xticks(x[::step])
        self.line_chart.fig.tight_layout()
        self.line_chart.draw()
    
    def load_history(self):
        result = api.get_history()
        
        self.history_list.clear()
        
        if result["success"]:
            datasets = result["data"].get("datasets", [])
            for dataset in datasets:
                item = QListWidgetItem()
                item.setText(
                    f"📄 {dataset['filename']}\n"
                    f"   ID: {dataset.get('id', 'N/A')}  |  "
                    f"Equipment: {dataset['total_equipment']}  |  "
                    f"Uploaded: {dataset['uploaded_at']}"
                )
                item.setData(Qt.UserRole, dataset)
                item.setSizeHint(item.sizeHint())
                self.history_list.addItem(item)
    
    def load_dataset_from_history(self, item):
        dataset = item.data(Qt.UserRole)
        if not dataset:
            return
        
        result = api.get_dataset(dataset['id'])
        
        if result["success"]:
            self.current_data = result["data"]
            self.selected_dataset_id = dataset['id']
            self.update_data_display()
            self.update_charts()
            self.tabs.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, "Error", "Failed to load dataset")
    
    def delete_selected_dataset(self):
        current_item = self.history_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select a dataset to delete")
            return
        
        dataset = current_item.data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{dataset['filename']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            result = api.delete_dataset(dataset['id'])
            
            if result["success"]:
                self.load_history()
                if self.selected_dataset_id == dataset['id']:
                    self.current_data = None
                    self.selected_dataset_id = None
                QMessageBox.information(self, "Success", "Dataset deleted successfully")
            else:
                QMessageBox.warning(self, "Error", "Failed to delete dataset")
    
    def download_pdf(self):
        if not self.selected_dataset_id:
            QMessageBox.warning(self, "Error", "Please select a dataset first")
            return
        
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF Report",
            f"equipment_report_{self.selected_dataset_id}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if save_path:
            result = api.download_pdf(self.selected_dataset_id, save_path)
            
            if result["success"]:
                QMessageBox.information(self, "Success", f"PDF saved to {save_path}")
            else:
                QMessageBox.warning(self, "Error", result.get("error", "Failed to download PDF"))
    
    def download_csv(self):
        """Download equipment data as CSV."""
        if not self.selected_dataset_id:
            QMessageBox.warning(self, "Error", "Please select a dataset first")
            return
        
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save CSV Export",
            f"equipment_data_{self.selected_dataset_id}.csv",
            "CSV Files (*.csv)"
        )
        
        if save_path:
            result = api.download_csv(self.selected_dataset_id, save_path)
            
            if result["success"]:
                QMessageBox.information(self, "Success", f"CSV saved to {save_path}")
            else:
                QMessageBox.warning(self, "Error", result.get("error", "Failed to export CSV"))
    
    def apply_date_filter(self):
        """Apply date filter to equipment list."""
        if not self.selected_dataset_id:
            QMessageBox.warning(self, "Error", "Please select a dataset first")
            return
        
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        
        result = api.get_equipment_list(self.selected_dataset_id, start_date, end_date)
        
        if result["success"]:
            # Update the equipment list in current_data
            self.current_data["equipment_list"] = result["data"].get("equipment_list", [])
            self.current_data["summary"] = result["data"].get("summary", self.current_data.get("summary", {}))
            self.update_data_display()
            show_styled_message(self, "Filter Applied", f"Showing data from {start_date} to {end_date}", "info")
        else:
            QMessageBox.warning(self, "Error", result.get("error", "Failed to filter data"))
    
    def clear_date_filter(self):
        """Clear date filter and reload full dataset."""
        if not self.selected_dataset_id:
            return
        
        result = api.get_dataset(self.selected_dataset_id)
        
        if result["success"]:
            self.current_data = result["data"]
            self.update_data_display()
            show_styled_message(self, "Filter Cleared", "Showing all equipment data", "info")
    
    def toggle_dark_mode(self):
        """Toggle between light and dark mode."""
        global COLORS
        self.dark_mode = not self.dark_mode
        
        if self.dark_mode:
            COLORS = DARK_COLORS.copy()
            self.dark_mode_btn.setText("☀️ Light Mode")
        else:
            COLORS = LIGHT_COLORS.copy()
            self.dark_mode_btn.setText("🌙 Dark Mode")
        
        # Update main window style
        self.setStyleSheet(f"background-color: {COLORS['background']};")
        
        # Refresh the UI
        self.update_data_display()
        show_styled_message(self, "Theme Changed", 
                           "Dark mode enabled" if self.dark_mode else "Light mode enabled", "info")
    
    def show_add_equipment_dialog(self):
        """Show dialog to add new equipment."""
        if not self.selected_dataset_id:
            QMessageBox.warning(self, "Error", "Please select a dataset first")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Equipment")
        dialog.setFixedSize(400, 350)
        dialog.setStyleSheet(f"""
            QDialog {{ background-color: {COLORS['card']}; }}
            QLabel {{ color: {COLORS['text']}; font-size: 13px; }}
            QLineEdit, QDoubleSpinBox {{
                padding: 10px;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                background: {COLORS['card']};
                color: {COLORS['text']};
            }}
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        title = QLabel("➕ Add New Equipment")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['primary']};")
        layout.addWidget(title)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("e.g., Pump-5")
        form.addRow("Name:", name_input)
        
        type_input = QLineEdit()
        type_input.setPlaceholderText("e.g., Pump, Valve, Compressor")
        form.addRow("Type:", type_input)
        
        flowrate_input = QDoubleSpinBox()
        flowrate_input.setRange(0, 10000)
        flowrate_input.setDecimals(2)
        form.addRow("Flowrate:", flowrate_input)
        
        pressure_input = QDoubleSpinBox()
        pressure_input.setRange(0, 1000)
        pressure_input.setDecimals(2)
        form.addRow("Pressure:", pressure_input)
        
        temperature_input = QDoubleSpinBox()
        temperature_input.setRange(-100, 1000)
        temperature_input.setDecimals(2)
        form.addRow("Temperature:", temperature_input)
        
        layout.addLayout(form)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['text_secondary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 25px;
            }}
        """)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        add_btn = QPushButton("Add Equipment")
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 25px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #059669; }}
        """)
        
        def submit():
            if not name_input.text() or not type_input.text():
                QMessageBox.warning(dialog, "Error", "Name and Type are required")
                return
            
            equipment_data = {
                "name": name_input.text(),
                "type": type_input.text(),
                "flowrate": flowrate_input.value(),
                "pressure": pressure_input.value(),
                "temperature": temperature_input.value()
            }
            
            result = api.add_equipment(self.selected_dataset_id, equipment_data)
            
            if result["success"]:
                dialog.accept()
                # Reload the dataset
                self.clear_date_filter()
                show_styled_message(self, "Success", "Equipment added successfully!", "info")
            else:
                QMessageBox.warning(dialog, "Error", result.get("error", "Failed to add equipment"))
        
        add_btn.clicked.connect(submit)
        btn_layout.addWidget(add_btn)
        
        layout.addLayout(btn_layout)
        dialog.exec_()
    
    def edit_equipment(self, equipment_id, current_data):
        """Show dialog to edit equipment."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Equipment")
        dialog.setFixedSize(400, 350)
        dialog.setStyleSheet(f"""
            QDialog {{ background-color: {COLORS['card']}; }}
            QLabel {{ color: {COLORS['text']}; font-size: 13px; }}
            QLineEdit, QDoubleSpinBox {{
                padding: 10px;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                background: {COLORS['card']};
                color: {COLORS['text']};
            }}
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        title = QLabel("✏️ Edit Equipment")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['warning']};")
        layout.addWidget(title)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        name_input = QLineEdit(current_data.get("name", ""))
        form.addRow("Name:", name_input)
        
        type_input = QLineEdit(current_data.get("type", ""))
        form.addRow("Type:", type_input)
        
        flowrate_input = QDoubleSpinBox()
        flowrate_input.setRange(0, 10000)
        flowrate_input.setDecimals(2)
        flowrate_input.setValue(float(current_data.get("flowrate", 0)))
        form.addRow("Flowrate:", flowrate_input)
        
        pressure_input = QDoubleSpinBox()
        pressure_input.setRange(0, 1000)
        pressure_input.setDecimals(2)
        pressure_input.setValue(float(current_data.get("pressure", 0)))
        form.addRow("Pressure:", pressure_input)
        
        temperature_input = QDoubleSpinBox()
        temperature_input.setRange(-100, 1000)
        temperature_input.setDecimals(2)
        temperature_input.setValue(float(current_data.get("temperature", 0)))
        form.addRow("Temperature:", temperature_input)
        
        layout.addLayout(form)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['text_secondary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 25px;
            }}
        """)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Changes")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['warning']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 25px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #d97706; }}
        """)
        
        def submit():
            equipment_data = {
                "name": name_input.text(),
                "type": type_input.text(),
                "flowrate": flowrate_input.value(),
                "pressure": pressure_input.value(),
                "temperature": temperature_input.value()
            }
            
            result = api.update_equipment(self.selected_dataset_id, equipment_id, equipment_data)
            
            if result["success"]:
                dialog.accept()
                self.clear_date_filter()
                show_styled_message(self, "Success", "Equipment updated successfully!", "info")
            else:
                QMessageBox.warning(dialog, "Error", result.get("error", "Failed to update equipment"))
        
        save_btn.clicked.connect(submit)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        dialog.exec_()
    
    def delete_equipment(self, equipment_id):
        """Delete equipment after confirmation."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete equipment #{equipment_id}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            result = api.delete_equipment(self.selected_dataset_id, equipment_id)
            
            if result["success"]:
                self.clear_date_filter()
                show_styled_message(self, "Success", "Equipment deleted successfully!", "info")
            else:
                QMessageBox.warning(self, "Error", result.get("error", "Failed to delete equipment"))
    
    def handle_logout(self):
        dialog = LogoutConfirmDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            api.logout()
            self.close()
            show_login()


def show_login():
    """Show login dialog and main window."""
    login_dialog = LoginDialog()
    
    if login_dialog.exec_() == QDialog.Accepted:
        main_window = MainWindow()
        main_window.show()
        return main_window
    return None


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Show login first
    main_window = show_login()
    
    if main_window:
        sys.exit(app.exec_())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
