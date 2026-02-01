import sys
import os
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QHeaderView, QLineEdit, QFormLayout,
                             QFrame, QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy, QScrollArea)
from PyQt5.QtCore import Qt, QSize, QPoint, QPropertyAnimation, QRect, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QPixmap, QPainter, QBrush, QPen, QLinearGradient
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

API_URL = "http://localhost:8000/api/"

# Premium Color Palette
class Theme:
    """
    Centralized design tokens for the ChemViz Pro desktop application.
    Follows a Slate/Indigo aesthetic for a premium industrial feel.
    """
    PRIMARY = "#4f46e5"      # Indigo 600
    PRIMARY_HOVER = "#4338ca" # Indigo 700
    SECONDARY = "#64748b"    # Slate 500
    SUCCESS = "#10b981"      # Emerald 500
    BG_MAIN = "#f8fafc"      # Slate 50
    CARD_BG = "#ffffff"
    TEXT_MAIN = "#0f172a"    # Slate 900
    TEXT_MUTED = "#64748b"   # Slate 500
    BORDER = "#e2e8f0"       # Slate 200

# Advanced Stylesheet
STYLESHEET = f"""
* {{
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
}}

QMainWindow, QWidget {{
    background-color: {Theme.BG_MAIN};
}}

QLabel {{
    color: {Theme.TEXT_MAIN};
}}

QLineEdit {{
    padding: 12px 16px;
    border: 1px solid {Theme.BORDER};
    border-radius: 8px;
    background-color: #ffffff;
    font-size: 14px;
    color: {Theme.TEXT_MAIN};
}}

QLineEdit:focus {{
    border: 2px solid {Theme.PRIMARY};
}}

QPushButton {{
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    color: white;
    background-color: {Theme.PRIMARY};
}}

QPushButton:hover {{
    background-color: {Theme.PRIMARY_HOVER};
}}

QPushButton#secondary {{
    background-color: transparent;
    color: {Theme.PRIMARY};
    border: 1.5px solid {Theme.PRIMARY};
}}

QPushButton#secondary:hover {{
    background-color: #f5f3ff;
}}

QPushButton#upload_btn {{
    background-color: {Theme.SUCCESS};
}}

QPushButton#upload_btn:hover {{
    background-color: #059669;
}}

QTabWidget::pane {{
    border: none;
    background: transparent;
}}

QTabBar::tab {{
    padding: 12px 30px;
    margin-right: 10px;
    background: transparent;
    color: {Theme.TEXT_MUTED};
    font-weight: 600;
    font-size: 13px;
    border-bottom: 2px solid transparent;
}}

QTabBar::tab:hover {{
    color: {Theme.TEXT_MAIN};
}}

QTabBar::tab:selected {{
    color: {Theme.PRIMARY};
    border-bottom: 2px solid {Theme.PRIMARY};
}}

QTableWidget {{
    background-color: #ffffff;
    border: none;
    border-radius: 12px;
}}

QHeaderView::section {{
    background-color: #f8fafc;
    padding: 12px;
    border: none;
    font-weight: 600;
    color: {Theme.TEXT_MUTED};
    text-transform: uppercase;
    font-size: 11px;
}}

QScrollBar:vertical {{
    border: none;
    background: transparent;
    width: 6px;
}}

QScrollBar::handle:vertical {{
    background: #cbd5e1;
    border-radius: 3px;
}}
"""

class AnimatedButton(QPushButton):
    """
    A custom QPushButton with shadow effects and pointer cursor 
    to enhance interactive feedback.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_shadow()
        self.setCursor(Qt.PointingHandCursor)

    def _set_shadow(self):
        """Applies a subtle drop shadow to the button."""
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(4)
        self.shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(self.shadow)

class GlassCard(QFrame):
    """
    A stylized container with soft shadows and rounded corners, 
    mimicking modern 'glassmorphism' design patterns.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            GlassCard {{
                background-color: white;
                border: 1px solid {Theme.BORDER};
                border-radius: 20px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 15))
        self.setGraphicsEffect(shadow)

class LogoWidget(QWidget):
    """
    Custom-drawn SVG-like logo using QPainter.
    Represents the ChemViz brand with a chemical flask icon inside a gradient glow.
    """
    def __init__(self, size=80, parent=None):
        super().__init__(parent)
        self.size = size
        self.setFixedSize(size, size)
    
    def paintEvent(self, event):
        """Standard Qt paint event to render the custom logo."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Outer Glow
        gradient = QLinearGradient(0, 0, self.size, self.size)
        gradient.setColorAt(0, QColor("#6366f1")) # Indigo 500
        gradient.setColorAt(1, QColor("#a855f7")) # Purple 500
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, self.size, self.size)
        
        # Flask Icon drawing
        painter.setPen(QPen(QColor("#ffffff"), 2.5))
        painter.setBrush(QBrush(QColor("#ffffff")))
        
        cx, cy = self.size // 2, self.size // 2
        # Neck
        painter.drawRect(cx - 5, cy - 18, 10, 6)
        # Liquid line
        painter.setOpacity(0.5)
        painter.drawPolygon([
            QPoint(cx - 7, cy - 10),
            QPoint(cx + 7, cy - 10),
            QPoint(cx + 16, cy + 12),
            QPoint(cx - 16, cy + 12),
        ])
        painter.setOpacity(1.0)
        # Outline
        painter.setBrush(Qt.NoBrush)
        painter.drawPolygon([
            QPoint(cx - 6, cy - 12),
            QPoint(cx + 6, cy - 12),
            QPoint(cx + 18, cy + 15),
            QPoint(cx - 18, cy + 15),
        ])

class LoginDialog(QWidget):
    """
    Initial entry point for the application.
    Handles user credentials input and provides a splash-screen-like branding experience.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ChemViz - Login")
        self.setFixedSize(450, 650)
        self.setStyleSheet(STYLESHEET)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(10)
        
        # Logo
        self.logo = LogoWidget(90)
        layout.addWidget(self.logo, 0, Qt.AlignCenter)
        
        layout.addSpacing(20)
        
        # Title
        title = QLabel("ChemViz")
        title.setStyleSheet("font-size: 36px; font-weight: 800; color: #1e293b; letter-spacing: -1.5px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Sign in to experience the dashboard")
        subtitle.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-size: 15px; font-weight: 400;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(40)
        
        # Login Inputs
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)
        
        layout.addSpacing(10)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(30)
        
        # Login Button
        self.login_btn = AnimatedButton("Sign In")
        self.login_btn.setFixedHeight(50)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f46e5, stop:1 #7c3aed);
                font-size: 16px;
                font-weight: 600;
            }
        """)
        layout.addWidget(self.login_btn)
        
        layout.addStretch()
        
        # Footer
        footer = QLabel("Powered by FOSSEE • IIT Bombay")
        footer.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-size: 12px; font-weight: 500;")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

class WorkerWindow(QMainWindow):
    """
    Main Dashboard terminal for ChemViz Pro.
    
    Features:
    - Multi-tab navigation (Overview vs Analytics).
    - Asynchronous API integration via 'requests'.
    - Integrated Matplotlib visualization.
    - PDF Report management.
    """
    def __init__(self, auth):
        super().__init__()
        self.auth = auth
        self.current_dataset_id = None
        self.setWindowTitle("ChemViz - Dashboard")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(STYLESHEET)
        
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Sidebar-style Header
        self.header = QFrame()
        self.header.setFixedHeight(80)
        self.header.setStyleSheet(f"background-color: white; border-bottom: 1px solid {Theme.BORDER};")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        # Brand
        brand_layout = QHBoxLayout()
        mini_logo = LogoWidget(45)
        brand_layout.addWidget(mini_logo)
        title = QLabel("ChemViz")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #1e293b;")
        brand_layout.addWidget(title)
        header_layout.addLayout(brand_layout)
        
        header_layout.addStretch()
        
        # User Profile
        self.user_label = QLabel("👤 Welcome")
        self.user_label.setStyleSheet(f"""
            padding: 8px 16px;
            background-color: #f1f5f9;
            border-radius: 20px;
            color: {Theme.TEXT_MAIN};
            font-size: 13px;
            font-weight: 600;
        """)
        header_layout.addWidget(self.user_label)
        
        self.main_layout.addWidget(self.header)
        
        # Main Content
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        self.upload_tab = QWidget()
        self.dashboard_tab = QWidget()
        
        self.tabs.addTab(self.upload_tab, "   Overview   ")
        self.tabs.addTab(self.dashboard_tab, "   Analytics & History   ")
        
        self.init_upload_ui()
        self.init_dashboard_ui()
        
    def init_upload_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Centered Upload Component
        self.upload_card = GlassCard()
        self.upload_card.setFixedSize(650, 480)
        card_layout = QVBoxLayout(self.upload_card)
        card_layout.setContentsMargins(50, 50, 50, 50)
        card_layout.setSpacing(25)
        
        icon = QLabel("📊")
        icon.setStyleSheet("font-size: 80px;")
        icon.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(icon)
        
        title = QLabel("Analyze New Telemetry")
        title.setStyleSheet("font-size: 26px; font-weight: 700;")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)
        
        desc = QLabel("Upload CSV data from your chemical equipment to generate insights")
        desc.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-size: 15px;")
        desc.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(desc)
        
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet(f"""
            padding: 20px;
            border: 2px dashed {Theme.BORDER};
            border-radius: 12px;
            background-color: {Theme.BG_MAIN};
            color: {Theme.TEXT_MUTED};
        """)
        self.file_path_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.file_path_label)
        
        btn_layout = QHBoxLayout()
        self.select_btn = AnimatedButton("Select File")
        self.select_btn.setObjectName("secondary")
        self.select_btn.clicked.connect(self.select_file)
        btn_layout.addWidget(self.select_btn)
        
        self.upload_btn = AnimatedButton("Start Analysis")
        self.upload_btn.setObjectName("upload_btn")
        self.upload_btn.setEnabled(False)
        self.upload_btn.clicked.connect(self.upload_file)
        btn_layout.addWidget(self.upload_btn)
        card_layout.addLayout(btn_layout)
        
        # Center in page
        outer_layout = QHBoxLayout()
        outer_layout.addStretch()
        outer_layout.addWidget(self.upload_card)
        outer_layout.addStretch()
        
        layout.addStretch()
        layout.addLayout(outer_layout)
        layout.addStretch()
        
        self.upload_tab.setLayout(layout)
        self.selected_file_path = None

    def init_dashboard_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(30)
        
        # History Side
        history_side = GlassCard()
        history_side.setFixedWidth(400)
        history_layout = QVBoxLayout(history_side)
        history_layout.setContentsMargins(25, 25, 25, 25)
        
        htitle = QLabel("Analysis History")
        htitle.setStyleSheet("font-size: 20px; font-weight: 700; margin-bottom: 10px;")
        history_layout.addWidget(htitle)
        
        self.refresh_btn = AnimatedButton("Refresh List")
        self.refresh_btn.setObjectName("secondary")
        self.refresh_btn.clicked.connect(self.load_history)
        history_layout.addWidget(self.refresh_btn)
        
        self.history_list = QTableWidget()
        self.history_list.setColumnCount(3)
        self.history_list.setHorizontalHeaderLabels(["ID", "Date", "Units"])
        self.history_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_list.setShowGrid(False)
        self.history_list.verticalHeader().setVisible(False)
        self.history_list.cellClicked.connect(self.history_item_clicked)
        history_layout.addWidget(self.history_list)
        
        layout.addWidget(history_side)
        
        # Viz Side
        viz_side = GlassCard()
        self.viz_layout = QVBoxLayout(viz_side)
        self.viz_layout.setContentsMargins(30, 30, 30, 30)
        
        self.viz_title = QLabel("System Performance Dashboard")
        self.viz_title.setStyleSheet("font-size: 20px; font-weight: 700;")
        self.viz_layout.addWidget(self.viz_title)
        
        self.stats_area = QLabel("Select an analysis to view parameters")
        self.stats_area.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-size: 15px; margin-bottom: 20px;")
        self.viz_layout.addWidget(self.stats_area)
        
        self.download_report_btn = AnimatedButton("📥 Download PDF Report")
        self.download_report_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #4f46e5;
                border: 1.5px solid #4f46e5;
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 10px;
            }
            QPushButton:hover {
                background-color: #f5f3ff;
            }
            QPushButton:disabled {
                border-color: #e2e8f0;
                color: #94a3b8;
            }
        """)
        self.download_report_btn.setEnabled(False)
        self.download_report_btn.clicked.connect(lambda: self.download_report())
        self.viz_layout.addWidget(self.download_report_btn)
        
        # Matplotlib Graph
        self.figure = Figure(facecolor='white', dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.viz_layout.addWidget(self.canvas)
        
        layout.addWidget(viz_side)
        self.dashboard_tab.setLayout(layout)

    def select_file(self):
        """Opens a file dialog to select the equipment CSV telemetry file."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV Files (*.csv)", options=options)
        if file_path:
            self.selected_file_path = file_path
            self.file_path_label.setText(f"✅ {os.path.basename(file_path)}")
            self.file_path_label.setStyleSheet("padding: 20px; border: 2px solid #10b981; border-radius: 12px; background-color: #f0fdf4; color: #065f46; font-weight: bold;")
            self.upload_btn.setEnabled(True)

    def upload_file(self):
        """Sends the selected CSV to the Django backend for processing."""
        self.upload_btn.setText("Analyzing...")
        self.upload_btn.setEnabled(False)
        filename = os.path.basename(self.selected_file_path)
        name_without_ext = os.path.splitext(filename)[0]
        
        files = {'csv_file': open(self.selected_file_path, 'rb')}
        data = {'name': name_without_ext}
        
        try:
            response = requests.post(f"{API_URL}datasets/upload/", files=files, data=data, auth=self.auth)
            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Analysis complete!")
                self.load_history()
                resp_data = response.json()
                self.current_dataset_id = resp_data.get('id')
                self.display_data(resp_data)
                self.tabs.setCurrentIndex(1)
            else:
                QMessageBox.critical(self, "Error", "Upload failed.")
        except:
            QMessageBox.critical(self, "Error", "Connection failed.")
        self.upload_btn.setText("Start Analysis")
        self.upload_btn.setEnabled(True)

    def load_history(self):
        """Fetches the last 5 datasets from the server to populate the history sidebar."""
        try:
            response = requests.get(f"{API_URL}datasets/history/", auth=self.auth)
            if response.status_code == 200:
                history = response.json()
                self.history_list.setRowCount(len(history))
                for i, item in enumerate(history):
                    self.history_list.setItem(i, 0, QTableWidgetItem(str(item['id'])))
                    self.history_list.setItem(i, 1, QTableWidgetItem(item['uploaded_at'][:10]))
                    self.history_list.setItem(i, 2, QTableWidgetItem(str(item['total_equipment'])))
        except: pass

    def history_item_clicked(self, row, col):
        """Callback for selecting an entry in the history table."""
        upload_id = self.history_list.item(row, 0).text()
        # Fetching details implicitly or from history (if history is detailed)
        # For now we trigger download as a primary action for history rows
        self.download_report(upload_id)

    def download_report(self, upload_id=None):
        """Triggers the PDF report download and saves it to the local filesystem."""
        target_id = upload_id if upload_id else self.current_dataset_id
        if not target_id:
            return
            
        try:
            response = requests.get(f"{API_URL}reports/{target_id}/pdf/", auth=self.auth)
            if response.status_code == 200:
                path, _ = QFileDialog.getSaveFileName(self, "Save Analysis Report", f"ChemViz_Report_{target_id}.pdf", "PDF (*.pdf)")
                if path:
                    with open(path, 'wb') as f: f.write(response.content)
                    QMessageBox.information(self, "Saved", "Detailed report saved to your computer.")
            else:
                QMessageBox.critical(self, "Error", f"Failed to download report (Status: {response.status_code})")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")

    def display_data(self, data):
        """
        Populates the dashboard charts and metrics using the analyzed data.
        Renders pie charts for distribution and line charts for telemetry trends.
        """
        self.current_dataset_id = data.get('id')
        self.download_report_btn.setEnabled(True)
        self.stats_area.setText(f"System Health: {data['avg_health_score']:.1f}%  |  Avg Flow: {data['avg_flowrate']:.2f} L/min  |  Avg Pressure: {data['avg_pressure']:.2f} Bar")
        self.figure.clear()
        
        # Subplot 1: Equipment Distribution
        ax1 = self.figure.add_subplot(211)
        dist = data['equipment_type_distribution']
        colors = ['#6366f1', '#a855f7', '#ec4899', '#f43f5e', '#f97316', '#eab308']
        ax1.pie(dist.values(), labels=dist.keys(), autopct='%1.0f%%', colors=colors, startangle=90, wedgeprops={'width': 0.4, 'edgecolor': 'w'})
        ax1.set_title("Equipment Distribution", fontsize=11, fontweight='bold')
        
        # Subplot 2: Parameter Trends (Top 10)
        ax2 = self.figure.add_subplot(212)
        equip = data['equipment_data'][:10]
        names = [e['name'][:6] for e in equip]
        flows = [e['flowrate'] for e in equip]
        pressurs = [e['pressure'] for e in equip]
        
        ax2.plot(names, flows, label='Flow', marker='o', color='#4f46e5', linewidth=2)
        ax2.plot(names, pressurs, label='Pressure', marker='s', color='#f43f5e', linewidth=2)
        ax2.grid(True, linestyle='--', alpha=0.3)
        ax2.set_title("Sample Equipment Performance", fontsize=11, fontweight='bold')
        ax2.legend(fontsize=8)
        
        self.figure.tight_layout()
        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    login = LoginDialog()
    auth_creds = None
    
    def on_login():
        global auth_creds
        u, p = login.username_input.text(), login.password_input.text()
        if u and p:
            auth_creds = (u, p)
            login.close()
            window.auth = auth_creds
            window.user_label.setText(f"👤 {u}")
            window.show()
            window.load_history()
            
    login.login_btn.clicked.connect(on_login)
    login.password_input.returnPressed.connect(on_login)
    
    window = WorkerWindow(None)
    login.show()
    sys.exit(app.exec_())
