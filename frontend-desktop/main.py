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
    QSplitter, QFrame, QHeaderView, QSizePolicy, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from api_service import api


# Color scheme
COLORS = {
    'primary': '#4f46e5',
    'secondary': '#6366f1',
    'success': '#10b981',
    'danger': '#ef4444',
    'warning': '#f59e0b',
    'background': '#f1f5f9',
    'card': '#ffffff',
    'text': '#1e293b',
    'text_secondary': '#64748b',
}

CHART_COLORS = ['#4f46e5', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']


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
            QMessageBox.warning(self, "Login Failed", result.get("error", "Invalid credentials"))
    
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


class ChartCanvas(FigureCanvas):
    """Matplotlib canvas for embedding charts in Qt."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.fig.patch.set_facecolor('white')


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.current_data = None
        self.selected_dataset_id = None
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
            QTabWidget::pane { border: none; background: white; border-radius: 8px; }
            QTabBar::tab { padding: 10px 20px; margin-right: 5px; }
            QTabBar::tab:selected { background: #4f46e5; color: white; border-radius: 6px; }
        """)
        
        self.tabs.addTab(self.create_upload_tab(), "📤 Upload")
        self.tabs.addTab(self.create_data_tab(), "📊 Data")
        self.tabs.addTab(self.create_charts_tab(), "📈 Charts")
        self.tabs.addTab(self.create_history_tab(), "📋 History")
        
        content_layout.addWidget(self.tabs)
        main_layout.addWidget(content, 1)
    
    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['text']};
                color: white;
            }}
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 30, 20, 30)
        layout.setSpacing(20)
        
        # Brand
        brand = QLabel("🔬 Chemical Viz")
        brand.setFont(QFont("Arial", 14, QFont.Bold))
        brand.setStyleSheet("color: white;")
        layout.addWidget(brand)
        
        layout.addStretch()
        
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
                border-radius: 8px;
            }}
        """)
        header.setFixedHeight(60)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel("Chemical Equipment Parameter Visualizer")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        layout.addStretch()
        
        # User info placeholder
        user_label = QLabel("👤 Logged In")
        user_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(user_label)
        
        return header
    
    def create_upload_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Upload area
        upload_box = QGroupBox("Upload CSV File")
        upload_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px dashed #d1d5db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
            }
        """)
        upload_layout = QVBoxLayout(upload_box)
        upload_layout.setAlignment(Qt.AlignCenter)
        upload_layout.setSpacing(15)
        
        icon_label = QLabel("📁")
        icon_label.setFont(QFont("Arial", 48))
        icon_label.setAlignment(Qt.AlignCenter)
        upload_layout.addWidget(icon_label)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setAlignment(Qt.AlignCenter)
        self.file_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        upload_layout.addWidget(self.file_label)
        
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        
        browse_btn = QPushButton("Browse Files")
        browse_btn.setMinimumSize(150, 40)
        browse_btn.setStyleSheet(f"""
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
        browse_btn.clicked.connect(self.browse_file)
        btn_layout.addWidget(browse_btn)
        
        self.upload_btn = QPushButton("Upload")
        self.upload_btn.setMinimumSize(150, 40)
        self.upload_btn.setEnabled(False)
        self.upload_btn.setStyleSheet(f"""
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
            QPushButton:disabled {{
                background-color: #d1d5db;
            }}
        """)
        self.upload_btn.clicked.connect(self.upload_file)
        btn_layout.addWidget(self.upload_btn)
        
        upload_layout.addLayout(btn_layout)
        
        layout.addWidget(upload_box)
        
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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Stats section
        self.stats_widget = QWidget()
        stats_layout = QHBoxLayout(self.stats_widget)
        stats_layout.setSpacing(15)
        
        self.stat_cards = {}
        for stat in ["Total Equipment", "Avg Flowrate", "Avg Pressure", "Avg Temperature"]:
            card = self.create_stat_card(stat, "0")
            self.stat_cards[stat] = card
            stats_layout.addWidget(card)
        
        layout.addWidget(self.stats_widget)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        self.pdf_btn = QPushButton("📄 Download PDF Report")
        self.pdf_btn.setMinimumSize(200, 40)
        self.pdf_btn.setEnabled(False)
        self.pdf_btn.setStyleSheet(f"""
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
            QPushButton:disabled {{
                background-color: #d1d5db;
            }}
        """)
        self.pdf_btn.clicked.connect(self.download_pdf)
        actions_layout.addWidget(self.pdf_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Data table
        self.data_table = QTableWidget()
        self.data_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f1f5f9;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.data_table)
        
        return widget
    
    def create_stat_card(self, title, value):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 20, QFont.Bold))
        value_label.setStyleSheet(f"color: {COLORS['primary']};")
        value_label.setObjectName("value")
        layout.addWidget(value_label)
        
        return card
    
    def create_charts_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Scroll area for charts
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        charts_widget = QWidget()
        charts_layout = QVBoxLayout(charts_widget)
        charts_layout.setSpacing(20)
        
        # Chart 1: Type Distribution (Pie)
        chart1_group = QGroupBox("Equipment Type Distribution")
        chart1_layout = QVBoxLayout(chart1_group)
        self.pie_chart = ChartCanvas(width=6, height=4)
        chart1_layout.addWidget(self.pie_chart)
        charts_layout.addWidget(chart1_group)
        
        # Chart 2: Parameter Comparison (Bar)
        chart2_group = QGroupBox("Average Parameters by Equipment Type")
        chart2_layout = QVBoxLayout(chart2_group)
        self.bar_chart = ChartCanvas(width=8, height=4)
        chart2_layout.addWidget(self.bar_chart)
        charts_layout.addWidget(chart2_group)
        
        # Chart 3: Parameter Trends (Line)
        chart3_group = QGroupBox("Equipment Parameters Overview")
        chart3_layout = QVBoxLayout(chart3_group)
        self.line_chart = ChartCanvas(width=8, height=4)
        chart3_layout.addWidget(self.line_chart)
        charts_layout.addWidget(chart3_group)
        
        scroll.setWidget(charts_widget)
        layout.addWidget(scroll)
        
        return widget
    
    def create_history_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        header = QLabel("Recent Uploads (Last 5)")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(header)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_history)
        header_layout.addWidget(refresh_btn)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #e2e8f0;
            }
            QListWidget::item:selected {
                background-color: #e0e7ff;
            }
            QListWidget::item:hover {
                background-color: #f1f5f9;
            }
        """)
        self.history_list.itemDoubleClicked.connect(self.load_dataset_from_history)
        layout.addWidget(self.history_list)
        
        # Delete button
        delete_btn = QPushButton("🗑️ Delete Selected")
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['danger']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: #dc2626;
            }}
        """)
        delete_btn.clicked.connect(self.delete_selected_dataset)
        layout.addWidget(delete_btn, alignment=Qt.AlignRight)
        
        return widget
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.upload_btn.setEnabled(True)
    
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
            QMessageBox.information(self, "Success", "File uploaded successfully!")
        else:
            QMessageBox.warning(self, "Upload Failed", result.get("error", "Upload failed"))
    
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
        
        # Update table
        if equipment_list:
            columns = ["equipment_id", "equipment_name", "equipment_type", 
                      "flowrate", "pressure", "temperature"]
            self.data_table.setColumnCount(len(columns))
            self.data_table.setHorizontalHeaderLabels([c.replace("_", " ").title() for c in columns])
            self.data_table.setRowCount(len(equipment_list))
            
            for row, item in enumerate(equipment_list):
                for col, key in enumerate(columns):
                    value = item.get(key, "")
                    self.data_table.setItem(row, col, QTableWidgetItem(str(value)))
        
        self.pdf_btn.setEnabled(True)
    
    def update_charts(self):
        if not self.current_data:
            return
        
        summary = self.current_data.get("summary", {})
        equipment_list = self.current_data.get("equipment_list", [])
        type_distribution = summary.get("type_distribution", {})
        
        # Pie Chart - Type Distribution
        self.pie_chart.axes.clear()
        if type_distribution:
            labels = list(type_distribution.keys())
            sizes = list(type_distribution.values())
            colors = CHART_COLORS[:len(labels)]
            self.pie_chart.axes.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
            self.pie_chart.axes.set_title("Equipment Type Distribution")
        self.pie_chart.draw()
        
        # Bar Chart - Average Parameters by Type
        self.bar_chart.axes.clear()
        if equipment_list:
            import pandas as pd
            df = pd.DataFrame(equipment_list)
            if 'equipment_type' in df.columns:
                grouped = df.groupby('equipment_type').agg({
                    'flowrate': 'mean',
                    'pressure': 'mean', 
                    'temperature': 'mean'
                }).reset_index()
                
                x = range(len(grouped))
                width = 0.25
                
                self.bar_chart.axes.bar([i - width for i in x], grouped['flowrate'], 
                                        width, label='Flowrate', color=CHART_COLORS[0])
                self.bar_chart.axes.bar(x, grouped['pressure'], 
                                        width, label='Pressure', color=CHART_COLORS[1])
                self.bar_chart.axes.bar([i + width for i in x], grouped['temperature'], 
                                        width, label='Temperature', color=CHART_COLORS[2])
                
                self.bar_chart.axes.set_xticks(x)
                self.bar_chart.axes.set_xticklabels(grouped['equipment_type'])
                self.bar_chart.axes.legend()
                self.bar_chart.axes.set_title("Average Parameters by Equipment Type")
        self.bar_chart.draw()
        
        # Line Chart - Equipment Overview
        self.line_chart.axes.clear()
        if equipment_list:
            x = range(len(equipment_list))
            flowrates = [item.get('flowrate', 0) for item in equipment_list]
            pressures = [item.get('pressure', 0) for item in equipment_list]
            temperatures = [item.get('temperature', 0) for item in equipment_list]
            
            self.line_chart.axes.plot(x, flowrates, marker='o', label='Flowrate', color=CHART_COLORS[0])
            self.line_chart.axes.plot(x, pressures, marker='s', label='Pressure', color=CHART_COLORS[1])
            self.line_chart.axes.plot(x, temperatures, marker='^', label='Temperature', color=CHART_COLORS[2])
            
            self.line_chart.axes.legend()
            self.line_chart.axes.set_xlabel("Equipment Index")
            self.line_chart.axes.set_ylabel("Value")
            self.line_chart.axes.set_title("Equipment Parameters Overview")
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
                    f"   Equipment: {dataset['total_equipment']} | "
                    f"Uploaded: {dataset['uploaded_at']}"
                )
                item.setData(Qt.UserRole, dataset)
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
    
    def handle_logout(self):
        reply = QMessageBox.question(
            self,
            "Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
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
