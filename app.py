#!/usr/bin/env python3
"""
TikTok to Facebook Automation App - Main GUI Application
PyQt5 based desktop application for automating TikTok video processing and Facebook upload
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox, QFormLayout,
    QCheckBox, QProgressBar, QSplitter, QFrame, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QMenu, QAction
)
import os
import sqlite3
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QIcon, QPixmap

# Import configuration
from config import (
    APP_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, BUTTON_STYLES,
    STATUS_LOG_MAX_LINES
)

# Import worker threads
from worker import AutomationWorker, ScrapingWorker, DownloadWorker, FacebookUploadWorker, FacebookLoginTestWorker, FacebookCookieLoginWorker

# Import data manager
from data_manager import DataManager


class MainWindow(QMainWindow):
    """Main application window for TikTok to Facebook automation"""
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.current_video_info = None
        self.current_video_id = None
        self.downloaded_video_path = None
        self.data_manager = DataManager()
        self.current_cookie_file = None
        self.discovered_pages = []
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(APP_TITLE)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        central_widget_layout = QVBoxLayout(central_widget)
        central_widget_layout.addWidget(self.tab_widget)
        
        # Create automation tab
        automation_tab = self.create_automation_tab()
        self.tab_widget.addTab(automation_tab, "🤖 Otomasyon")
        
        # Create database tab
        database_tab = self.create_database_tab()
        self.tab_widget.addTab(database_tab, "📊 Veritabanı")
        
        # Apply styles
        self.apply_styles()
        
    def create_automation_tab(self):
        """Create the automation tab"""
        automation_widget = QWidget()
        
        # Create main splitter for resizable layout
        main_splitter = QSplitter(Qt.Horizontal)
        automation_layout = QVBoxLayout(automation_widget)
        automation_layout.addWidget(main_splitter)
        
        # Create left panel for inputs and controls
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # Create right panel for status log
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)
        
        # Set splitter proportions (60% left, 40% right)
        main_splitter.setSizes([600, 400])
        
        return automation_widget
        
    def create_database_tab(self):
        """Create the database tab"""
        database_widget = QWidget()
        database_layout = QVBoxLayout(database_widget)
        
        # Control buttons for database
        db_controls_layout = QHBoxLayout()
        
        self.refresh_db_button = QPushButton("🔄 Verileri Yenile")
        self.refresh_db_button.setObjectName("secondary_button")
        db_controls_layout.addWidget(self.refresh_db_button)
        
        self.export_json_button = QPushButton("📤 JSON Dışa Aktar")
        self.export_json_button.setObjectName("secondary_button")
        db_controls_layout.addWidget(self.export_json_button)
        
        self.clear_db_button = QPushButton("🗑️ Veritabanını Temizle")
        self.clear_db_button.setObjectName("secondary_button")
        db_controls_layout.addWidget(self.clear_db_button)
        
        db_controls_layout.addStretch()
        database_layout.addLayout(db_controls_layout)
        
        # Create table for displaying videos
        self.videos_table = QTableWidget()
        self.videos_table.setColumnCount(8)
        self.videos_table.setHorizontalHeaderLabels([
            "ID", "URL", "Açıklama", "Hashtag'ler", "Yazar", "Durum", "İndirilen Dosya", "Tarih"
        ])
        
        # Configure table
        header = self.videos_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # URL
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Description
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Hashtags
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Author
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(6, QHeaderView.Stretch)  # Downloaded File
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Date
        
        self.videos_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.videos_table.setAlternatingRowColors(True)
        self.videos_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.videos_table.customContextMenuRequested.connect(self.show_video_context_menu)
        
        database_layout.addWidget(self.videos_table)
        
        # Connect database tab signals
        self.refresh_db_button.clicked.connect(self.refresh_database_table)
        self.export_json_button.clicked.connect(self.export_to_json)
        self.clear_db_button.clicked.connect(self.clear_database)
        
        # Load initial data
        self.refresh_database_table()
        
        return database_widget
        
    def show_video_context_menu(self, position):
        """Show context menu for video table"""
        if self.videos_table.itemAt(position) is None:
            return
            
        menu = QMenu()
        
        # Get selected row
        row = self.videos_table.rowAt(position.y())
        if row >= 0:
            # Get video info
            videos = self.data_manager.get_all_videos()
            if row < len(videos):
                video = videos[row]
                
                # Check if video file exists
                video_file = video.get('video_download_url', '')
                if video_file and os.path.exists(video_file):
                    upload_action = QAction("📘 Facebook'a Yükle", self)
                    upload_action.triggered.connect(lambda: self.upload_video_from_db(video))
                    menu.addAction(upload_action)
                
                # Add other actions
                view_action = QAction("👁️ Detayları Görüntüle", self)
                view_action.triggered.connect(lambda: self.view_video_details(video))
                menu.addAction(view_action)
                
                delete_action = QAction("🗑️ Sil", self)
                delete_action.triggered.connect(lambda: self.delete_video_from_db(video))
                menu.addAction(delete_action)
        
        menu.exec_(self.videos_table.mapToGlobal(position))
        
    def upload_video_from_db(self, video):
        """Upload video from database to Facebook"""
        video_file = video.get('video_download_url', '')
        if not video_file or not os.path.exists(video_file):
            self.add_log_message("❌ Video dosyası bulunamadı!", "error")
            return
            
        # Check if we have a saved session
        if not self.current_cookie_file:
            self.add_log_message("❌ Önce Facebook'a cookie ile giriş yapın!", "error")
            return
            
        # Set current video info for upload
        self.current_video_info = video
        self.current_video_id = video['id']
        self.downloaded_video_path = video_file
        
        # Start Facebook upload
        self.upload_to_facebook()
        
    def view_video_details(self, video):
        """Show video details in a dialog"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Video Detayları - ID: {video['id']}")
        dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Add video details
        details = f"""
URL: {video['url']}
Açıklama: {video['description'] or 'Yok'}
Hashtag'ler: {', '.join(video['hashtags']) if video['hashtags'] else 'Yok'}
Mention'lar: {', '.join(video['mentions']) if video['mentions'] else 'Yok'}
Yazar: {video['author'] or 'Bilinmiyor'}
Durum: {video['status'] or 'scraped'}
Oluşturma Tarihi: {video['created_at'] or 'Bilinmiyor'}
Video Dosyası: {video.get('video_download_url', 'Yok')}
Facebook Yüklendi: {'Evet' if video.get('facebook_uploaded') else 'Hayır'}
        """
        
        details_text = QTextEdit()
        details_text.setPlainText(details.strip())
        details_text.setReadOnly(True)
        layout.addWidget(details_text)
        
        dialog.exec_()
        
    def delete_video_from_db(self, video):
        """Delete video from database"""
        from PyQt5.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, 
            'Video Sil',
            f'Bu videoyu silmek istediğinizden emin misiniz?\n\nURL: {video["url"][:50]}...',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                conn = sqlite3.connect(self.data_manager.db_path)
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM processing_log WHERE video_id = ?', (video['id'],))
                cursor.execute('DELETE FROM videos WHERE id = ?', (video['id'],))
                
                conn.commit()
                conn.close()
                
                self.add_log_message(f"🗑️ Video silindi: ID {video['id']}", "success")
                self.refresh_database_table()
                
            except Exception as e:
                self.add_log_message(f"Video silme hatası: {str(e)}", "error")
                
    def browse_cookie_file(self):
        """Browse for cookie file"""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Cookie Dosyası Seç",
            "data/cookies",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            self.cookie_file_input.setText(file_path)
            self.add_log_message(f"📁 Cookie dosyası seçildi: {file_path}", "info")
            
    def login_with_cookie(self):
        """Login with cookie file"""
        cookie_file = self.cookie_file_input.text().strip()
        
        if not cookie_file:
            self.add_log_message("❌ Cookie dosyası seçin!", "error")
            return
            
        if not os.path.exists(cookie_file):
            self.add_log_message("❌ Cookie dosyası bulunamadı!", "error")
            return
            
        # Disable cookie login button and show progress
        self.cookie_login_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.add_log_message("🍪 Cookie ile giriş başlatılıyor...", "info")
        
        # Store cookie file for later use
        self.current_cookie_file = cookie_file
        
        user_inputs = {
            'cookie_file': cookie_file,
            'login_type': 'cookie'
        }
        
        self.worker = FacebookCookieLoginWorker(user_inputs)
        self.worker.progress_updated.connect(self.add_log_message)
        self.worker.progress_percentage.connect(self.progress_bar.setValue)
        self.worker.login_completed.connect(self.on_cookie_login_completed)
        self.worker.pages_discovered.connect(self.on_facebook_pages_discovered)
        
        self.worker.start()
        
    def on_cookie_login_completed(self, success, message):
        """Handle cookie login completion"""
        self.cookie_login_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.add_log_message(message, "success")
        else:
            self.add_log_message(message, "error")
            
        # Clean up worker
        if self.worker:
            self.worker = None
        
    def on_facebook_pages_discovered(self, pages):
        """Handle discovered Facebook pages"""
        self.discovered_pages = pages
        
        # Update pages table
        self.pages_table.setRowCount(len(pages))
        
        for row, page in enumerate(pages):
            self.pages_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.pages_table.setItem(row, 1, QTableWidgetItem(page['name']))
            self.pages_table.setItem(row, 2, QTableWidgetItem(page.get('id', 'N/A')))
            self.pages_table.setItem(row, 3, QTableWidgetItem(page.get('url', 'N/A')))
            
            # Default checkbox
            default_text = "✅ Evet" if page.get('type') == 'profile' else "❌ Hayır"
            self.pages_table.setItem(row, 4, QTableWidgetItem(default_text))
            
        self.add_log_message(f"📄 {len(pages)} sayfa keşfedildi ve tabloya eklendi", "success")
        
    def create_left_panel(self):
        """Create the left panel with input controls"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # TikTok URL Section
        tiktok_group = QGroupBox("TikTok Video Bilgileri")
        tiktok_layout = QFormLayout(tiktok_group)
        
        self.tiktok_url_input = QLineEdit()
        self.tiktok_url_input.setPlaceholderText("https://www.tiktok.com/@username/video/...")
        tiktok_layout.addRow("TikTok URL:", self.tiktok_url_input)
        
        left_layout.addWidget(tiktok_group)
        
        # Facebook Cookie Login Section
        facebook_group = QGroupBox("Facebook Cookie Girişi")
        facebook_layout = QVBoxLayout(facebook_group)
        
        # Cookie file selection
        cookie_file_layout = QHBoxLayout()
        
        self.cookie_file_input = QLineEdit()
        self.cookie_file_input.setPlaceholderText("Cookie dosya yolu...")
        self.cookie_file_input.setReadOnly(True)
        cookie_file_layout.addWidget(QLabel("Cookie Dosyası:"))
        cookie_file_layout.addWidget(self.cookie_file_input)
        
        self.browse_cookie_button = QPushButton("📁 Dosya Seç")
        self.browse_cookie_button.setObjectName("secondary_button")
        cookie_file_layout.addWidget(self.browse_cookie_button)
        
        facebook_layout.addLayout(cookie_file_layout)
        
        # Cookie login button
        cookie_login_layout = QHBoxLayout()
        self.cookie_login_button = QPushButton("🍪 Cookie ile Giriş")
        self.cookie_login_button.setObjectName("primary_button")
        cookie_login_layout.addWidget(self.cookie_login_button)
        cookie_login_layout.addStretch()
        
        facebook_layout.addLayout(cookie_login_layout)
        
        # Selected page info
        self.selected_page_label = QLabel("📄 Seçili sayfa: Henüz seçim yapılmadı")
        self.selected_page_label.setStyleSheet("font-weight: bold; color: #2196F3; padding: 5px;")
        facebook_layout.addWidget(self.selected_page_label)
        
        left_layout.addWidget(facebook_group)
        
        # Gemini API Section
        gemini_group = QGroupBox("Gemini AI Ayarları")
        gemini_layout = QFormLayout(gemini_group)
        
        self.gemini_api_key_input = QLineEdit()
        self.gemini_api_key_input.setEchoMode(QLineEdit.Password)
        self.gemini_api_key_input.setPlaceholderText("Gemini API anahtarınızı girin")
        gemini_layout.addRow("API Anahtarı:", self.gemini_api_key_input)
        
        self.enhance_content_checkbox = QCheckBox("İçeriği Gemini ile zenginleştir")
        self.enhance_content_checkbox.setChecked(True)
        gemini_layout.addRow("", self.enhance_content_checkbox)
        
        left_layout.addWidget(gemini_group)
        
        # Options Section
        options_group = QGroupBox("Seçenekler")
        options_layout = QFormLayout(options_group)
        
        self.headless_checkbox = QCheckBox("Tarayıcıyı gizli modda çalıştır")
        options_layout.addRow("", self.headless_checkbox)
        
        self.save_credentials_checkbox = QCheckBox("Giriş bilgilerini kaydet")
        options_layout.addRow("", self.save_credentials_checkbox)
        
        left_layout.addWidget(options_group)
        
        # Control Buttons Section
        buttons_frame = QFrame()
        buttons_layout = QVBoxLayout(buttons_frame)
        
        # Step-by-step buttons
        step_buttons_layout = QHBoxLayout()
        
        self.scrape_button = QPushButton("1. Verileri Çek")
        self.scrape_button.setObjectName("primary_button")
        step_buttons_layout.addWidget(self.scrape_button)
        
        self.download_button = QPushButton("2. Video İndir")
        self.download_button.setObjectName("secondary_button")
        self.download_button.setEnabled(False)
        step_buttons_layout.addWidget(self.download_button)
        
        self.facebook_button = QPushButton("3. Facebook'a Yükle")
        self.facebook_button.setObjectName("secondary_button")
        self.facebook_button.setEnabled(False)
        step_buttons_layout.addWidget(self.facebook_button)
        
        buttons_layout.addLayout(step_buttons_layout)
        
        # Full automation and control buttons
        control_buttons_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Tümünü Otomatik Yap")
        self.start_button.setObjectName("primary_button")
        control_buttons_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Durdur")
        self.stop_button.setObjectName("secondary_button")
        self.stop_button.setEnabled(False)
        control_buttons_layout.addWidget(self.stop_button)
        
        self.clear_log_button = QPushButton("Günlüğü Temizle")
        self.clear_log_button.setObjectName("secondary_button")
        control_buttons_layout.addWidget(self.clear_log_button)
        
        buttons_layout.addLayout(control_buttons_layout)
        
        left_layout.addWidget(buttons_frame)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        left_layout.addWidget(self.progress_bar)
        
        # Add stretch to push everything to top
        left_layout.addStretch()
        
        return left_widget
        
    def create_right_panel(self):
        """Create the right panel with status log"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Status Log Section
        log_label = QLabel("İşlem Durumu ve Günlük")
        log_label.setFont(QFont("Arial", 12, QFont.Bold))
        right_layout.addWidget(log_label)
        
        self.status_log = QTextEdit()
        self.status_log.setReadOnly(True)
        self.status_log.setFont(QFont("Consolas", 10))
        self.status_log.setPlaceholderText("İşlem günlüğü burada görünecek...")
        right_layout.addWidget(self.status_log)
        
        # Facebook Pages Section
        pages_label = QLabel("Facebook Sayfaları")
        pages_label.setFont(QFont("Arial", 12, QFont.Bold))
        right_layout.addWidget(pages_label)
        
        # Page selection info
        page_info_label = QLabel("💡 Reels yüklemek için bir sayfa seçin. Seçim yapmazsanız ana profil kullanılır.")
        page_info_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        page_info_label.setWordWrap(True)
        right_layout.addWidget(page_info_label)
        
        self.pages_table = QTableWidget()
        self.pages_table.setColumnCount(5)
        self.pages_table.setHorizontalHeaderLabels([
            "ID", "Sayfa Adı", "Sayfa ID", "URL", "Varsayılan"
        ])
        
        # Configure pages table
        pages_header = self.pages_table.horizontalHeader()
        pages_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        pages_header.setSectionResizeMode(1, QHeaderView.Stretch)
        pages_header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        pages_header.setSectionResizeMode(3, QHeaderView.Stretch)
        pages_header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.pages_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.pages_table.itemSelectionChanged.connect(self.on_page_selection_changed)
        right_layout.addWidget(self.pages_table)
        
        return right_widget
        
    def apply_styles(self):
        """Apply custom styles to the application"""
        # Set application style
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #f5f5f5;
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            
            QLineEdit {{
                border: 2px solid #ddd;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }}
            
            QLineEdit:focus {{
                border-color: #1877f2;
            }}
            
            QTextEdit {{
                border: 2px solid #ddd;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', monospace;
                background-color: #fafafa;
            }}
            
            QCheckBox {{
                font-size: 14px;
                spacing: 8px;
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            
            QProgressBar {{
                border: 2px solid #ddd;
                border-radius: 6px;
                text-align: center;
                font-weight: bold;
            }}
            
            QProgressBar::chunk {{
                background-color: #1877f2;
                border-radius: 4px;
            }}
            
            QPushButton[objectName="primary_button"] {BUTTON_STYLES["primary"]}
            QPushButton[objectName="secondary_button"] {BUTTON_STYLES["secondary"]}
        """)
        
    def setup_connections(self):
        """Setup signal-slot connections"""
        # Step-by-step buttons
        self.scrape_button.clicked.connect(self.scrape_tiktok_data)
        self.download_button.clicked.connect(self.download_video)
        self.facebook_button.clicked.connect(self.upload_to_facebook)
        
        # Cookie login connections
        self.browse_cookie_button.clicked.connect(self.browse_cookie_file)
        self.cookie_login_button.clicked.connect(self.login_with_cookie)
        
        # Full automation and control buttons
        self.start_button.clicked.connect(self.start_automation)
        self.stop_button.clicked.connect(self.stop_automation)
        self.clear_log_button.clicked.connect(self.clear_status_log)
        
    def start_automation(self):
        """Start the automation process"""
        # Validate inputs
        if not self.validate_inputs():
            return
            
        # Update UI state
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Add initial log message
        self.add_log_message("İşlem başlatılıyor...")
        
        # Get user inputs
        user_inputs = self.get_user_inputs()
        
        # Create and start worker thread
        self.worker = AutomationWorker(user_inputs)
        
        # Connect worker signals
        self.worker.progress_updated.connect(self.add_log_message)
        self.worker.progress_percentage.connect(self.progress_bar.setValue)
        self.worker.task_completed.connect(self.on_task_completed)
        
        # Start worker
        self.worker.start()
        
    def stop_automation(self):
        """Stop the automation process"""
        self.add_log_message("İşlem durduruluyor...")
        
        # Stop worker if running
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(5000)  # Wait up to 5 seconds for thread to finish
            
        # Update UI state
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        
    def validate_inputs(self):
        """Validate user inputs before starting automation"""
        tiktok_url = self.tiktok_url_input.text().strip()
        
        if not tiktok_url:
            self.add_log_message("HATA: TikTok URL'si gerekli!", "error")
            return False
            
        if not tiktok_url.startswith("https://www.tiktok.com/"):
            self.add_log_message("HATA: Geçerli bir TikTok URL'si girin!", "error")
            return False
            
        if not self.current_cookie_file:
            self.add_log_message("HATA: Önce Facebook'a cookie ile giriş yapın!", "error")
            return False
            
        if self.enhance_content_checkbox.isChecked():
            gemini_api_key = self.gemini_api_key_input.text().strip()
            if not gemini_api_key:
                self.add_log_message("HATA: Gemini API anahtarı gerekli!", "error")
                return False
                
        return True
        
    def add_log_message(self, message, level="info"):
        """Add a message to the status log"""
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Format message based on level
        if level == "error":
            formatted_message = f"[{timestamp}] ❌ {message}"
        elif level == "success":
            formatted_message = f"[{timestamp}] ✅ {message}"
        elif level == "warning":
            formatted_message = f"[{timestamp}] ⚠️ {message}"
        else:
            formatted_message = f"[{timestamp}] ℹ️ {message}"
            
        self.status_log.append(formatted_message)
        
        # Limit log lines
        if self.status_log.document().lineCount() > STATUS_LOG_MAX_LINES:
            cursor = self.status_log.textCursor()
            cursor.movePosition(cursor.Start)
            cursor.select(cursor.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()  # Remove the newline
            
        # Auto-scroll to bottom
        scrollbar = self.status_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def clear_status_log(self):
        """Clear the status log"""
        self.status_log.clear()
        self.add_log_message("Günlük temizlendi.")
        
    def on_task_completed(self, success, message):
        """Handle task completion"""
        if success:
            self.add_log_message(message, "success")
        else:
            self.add_log_message(message, "error")
            
        # Reset UI state
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        # Clean up worker
        if self.worker:
            self.worker = None
            
        # Refresh database table
        self.refresh_database_table()
            
    def refresh_database_table(self):
        """Refresh the database table with current data"""
        try:
            videos = self.data_manager.get_all_videos()
            
            self.videos_table.setRowCount(len(videos))
            
            for row, video in enumerate(videos):
                # ID
                self.videos_table.setItem(row, 0, QTableWidgetItem(str(video['id'])))
                
                # URL (truncated)
                url = video['url']
                if len(url) > 50:
                    url = url[:47] + "..."
                self.videos_table.setItem(row, 1, QTableWidgetItem(url))
                
                # Description (truncated)
                description = video['description'] or "Açıklama yok"
                if len(description) > 100:
                    description = description[:97] + "..."
                self.videos_table.setItem(row, 2, QTableWidgetItem(description))
                
                # Hashtags
                hashtags = ", ".join(video['hashtags'][:3])  # Show first 3 hashtags
                if len(video['hashtags']) > 3:
                    hashtags += f" (+{len(video['hashtags']) - 3})"
                self.videos_table.setItem(row, 3, QTableWidgetItem(hashtags))
                
                # Author
                author = video['author'] or "Bilinmiyor"
                self.videos_table.setItem(row, 4, QTableWidgetItem(author))
                
                # Status
                status = video['status'] or "scraped"
                status_emoji = {
                    'scraped': '📝',
                    'downloaded': '⬇️',
                    'processing': '⏳',
                    'completed': '✅',
                    'error': '❌'
                }.get(status, '❓')
                self.videos_table.setItem(row, 5, QTableWidgetItem(f"{status_emoji} {status}"))
                
                # Downloaded File
                video_file = video.get('video_download_url', '')
                if video_file and os.path.exists(video_file):
                    filename = os.path.basename(video_file)
                    if len(filename) > 30:
                        filename = filename[:27] + "..."
                    file_display = f"📁 {filename}"
                else:
                    file_display = "❌ Dosya yok"
                self.videos_table.setItem(row, 6, QTableWidgetItem(file_display))
                
                # Date
                created_at = video['created_at']
                if created_at:
                    # Format date
                    import datetime
                    try:
                        if isinstance(created_at, str):
                            date_obj = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        else:
                            date_obj = datetime.datetime.fromisoformat(created_at)
                        formatted_date = date_obj.strftime("%d.%m.%Y %H:%M")
                    except:
                        formatted_date = str(created_at)[:16]
                else:
                    formatted_date = "Bilinmiyor"
                self.videos_table.setItem(row, 7, QTableWidgetItem(formatted_date))
                
            self.add_log_message(f"📊 Veritabanından {len(videos)} video yüklendi", "info")
            
        except Exception as e:
            self.add_log_message(f"Veritabanı yenileme hatası: {str(e)}", "error")
            
    def export_to_json(self):
        """Export database to JSON file"""
        try:
            videos = self.data_manager.get_all_videos()
            
            import json
            import os
            from datetime import datetime
            
            # Create export filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tiktok_export_{timestamp}.json"
            filepath = os.path.join("data", filename)
            
            # Ensure data directory exists
            os.makedirs("data", exist_ok=True)
            
            # Export data
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(videos, f, ensure_ascii=False, indent=2, default=str)
                
            self.add_log_message(f"✅ Veriler JSON'a aktarıldı: {filepath}", "success")
            
        except Exception as e:
            self.add_log_message(f"JSON dışa aktarma hatası: {str(e)}", "error")
            
    def clear_database(self):
        """Clear all data from database (with confirmation)"""
        from PyQt5.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, 
            'Veritabanını Temizle',
            'Tüm video verilerini silmek istediğinizden emin misiniz?\n\nBu işlem geri alınamaz!',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Clear database tables
                import sqlite3
                conn = sqlite3.connect(self.data_manager.db_path)
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM processing_log')
                cursor.execute('DELETE FROM videos')
                
                conn.commit()
                conn.close()
                
                # Clear JSON file
                import json
                with open(self.data_manager.json_file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                
                self.add_log_message("🗑️ Veritabanı temizlendi", "success")
                self.refresh_database_table()
                
            except Exception as e:
                self.add_log_message(f"Veritabanı temizleme hatası: {str(e)}", "error")
                
    def on_facebook_upload_completed(self, success, message):
        """Handle Facebook upload completion"""
        self.facebook_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.add_log_message(message, "success")
            self.add_log_message("🎉 Tüm işlemler tamamlandı!", "success")
            
            # Reset for next video
            self.current_video_info = None
            self.current_video_id = None
            self.downloaded_video_path = None
            self.download_button.setEnabled(False)
            self.facebook_button.setEnabled(False)
        else:
            self.add_log_message(message, "error")
            
        # Clean up worker
        if self.worker:
            self.worker = None
            
        # Refresh database table
        self.refresh_database_table()
            
    def scrape_tiktok_data(self):
        """Step 1: Scrape TikTok data only"""
        # Validate TikTok URL
        tiktok_url = self.tiktok_url_input.text().strip()
        if not tiktok_url:
            self.add_log_message("HATA: TikTok URL'si gerekli!", "error")
            return
            
        if not tiktok_url.startswith("https://www.tiktok.com/"):
            self.add_log_message("HATA: Geçerli bir TikTok URL'si girin!", "error")
            return
            
        # Disable scrape button and show progress
        self.scrape_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Create worker for scraping only
        user_inputs = {
            'tiktok_url': tiktok_url,
            'headless_mode': self.headless_checkbox.isChecked()
        }
        
        self.worker = ScrapingWorker(user_inputs)
        self.worker.progress_updated.connect(self.add_log_message)
        self.worker.progress_percentage.connect(self.progress_bar.setValue)
        self.worker.scraping_completed.connect(self.on_scraping_completed)
        
        self.worker.start()
        
    def download_video(self):
        """Step 2: Download video using scraped data"""
        if not self.current_video_info:
            self.add_log_message("HATA: Önce video verilerini çekin!", "error")
            return
            
        # Disable download button and show progress
        self.download_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        user_inputs = {
            'tiktok_url': self.current_video_info['url'],
            'video_info': self.current_video_info,
            'video_id': self.current_video_id,
            'headless_mode': self.headless_checkbox.isChecked()
        }
        
        self.worker = DownloadWorker(user_inputs)
        self.worker.progress_updated.connect(self.add_log_message)
        self.worker.progress_percentage.connect(self.progress_bar.setValue)
        self.worker.download_completed.connect(self.on_download_completed)
        
        self.worker.start()
        
    def upload_to_facebook(self):
        """Step 3: Upload to Facebook with page selection"""
        if not self.downloaded_video_path:
            self.add_log_message("HATA: Önce videoyu indirin!", "error")
            return
            
        # Check if we have a saved session
        if not self.current_cookie_file:
            self.add_log_message("HATA: Önce Facebook'a giriş yapın!", "error")
            return
            
        # Get selected page from Facebook Management tab
        selected_page = self.get_selected_facebook_page()
        
        if not selected_page:
            self.add_log_message("HATA: Lütfen bir sayfa seçin!", "error")
            return
            
        # Disable Facebook button and show progress
        self.facebook_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Get session name from cookie file
        session_name = self.current_cookie_file.replace('facebook_cookies_', '').replace('.json', '') if self.current_cookie_file else 'default'
        
        user_inputs = {
            'session_name': session_name,
            'video_path': self.downloaded_video_path,
            'video_info': self.current_video_info,
            'video_id': self.current_video_id,
            'selected_page': selected_page,
            'enhance_with_gemini': self.enhance_content_checkbox.isChecked(),
            'headless_mode': self.headless_checkbox.isChecked()
        }
        
        self.add_log_message(f"🎬 Reels yükleme başlatılıyor: {selected_page['name']}", "info")
        
        self.worker = FacebookUploadWorker(user_inputs)
        self.worker.progress_updated.connect(self.add_log_message)
        self.worker.progress_percentage.connect(self.progress_bar.setValue)
        self.worker.upload_completed.connect(self.on_facebook_upload_completed)
        
        self.worker.start()
    
    def get_selected_facebook_page(self):
        """Get the currently selected Facebook page"""
        try:
            # Get selected row from pages table
            current_row = self.pages_table.currentRow()
            if current_row < 0:
                # If no selection, return default profile
                return {
                    'name': 'Ana Profil',
                    'type': 'profile',
                    'url': 'https://www.facebook.com/me'
                }
                
            # Get page info from table (columns: ID, Sayfa Adı, Sayfa ID, URL, Varsayılan)
            page_name = self.pages_table.item(current_row, 1).text()  # Sayfa Adı
            page_url = self.pages_table.item(current_row, 3).text()   # URL
            default_text = self.pages_table.item(current_row, 4).text()  # Varsayılan
            
            # Determine page type based on default status
            page_type = 'profile' if '✅' in default_text else 'page'
            
            return {
                'name': page_name,
                'type': page_type,
                'url': page_url
            }
            
        except Exception as e:
            self.add_log_message(f"Sayfa seçimi hatası: {str(e)}", "error")
            # Return default profile on error
            return {
                'name': 'Ana Profil',
                'type': 'profile',
                'url': 'https://www.facebook.com/me'
            }
    
    def on_page_selection_changed(self):
        """Handle page selection change"""
        try:
            selected_page = self.get_selected_facebook_page()
            if selected_page:
                page_type_text = "👤 Profil" if selected_page['type'] == 'profile' else "📄 Sayfa"
                self.selected_page_label.setText(f"📄 Seçili sayfa: {selected_page['name']} ({page_type_text})")
            else:
                self.selected_page_label.setText("📄 Seçili sayfa: Henüz seçim yapılmadı")
        except Exception as e:
            self.selected_page_label.setText("📄 Seçili sayfa: Hata oluştu")
        
    def on_scraping_completed(self, success, video_info, video_id):
        """Handle scraping completion"""
        self.scrape_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.current_video_info = video_info
            self.current_video_id = video_id
            self.download_button.setEnabled(True)
            
            self.add_log_message("✅ Video verileri başarıyla çekildi!", "success")
            self.add_log_message(f"📝 Açıklama: {video_info.get('description', 'N/A')}", "info")
            self.add_log_message(f"🏷️ Hashtag'ler: {', '.join(video_info.get('hashtags', []))}", "info")
            self.add_log_message(f"👤 Yazar: {video_info.get('author', 'N/A')}", "info")
            self.add_log_message(f"🆔 Video ID: {video_id}", "info")
        else:
            self.add_log_message("❌ Video verileri çekilemedi!", "error")
            
        # Clean up worker
        if self.worker:
            self.worker = None
            
    def on_download_completed(self, success, file_path):
        """Handle download completion"""
        self.download_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.downloaded_video_path = file_path
            self.facebook_button.setEnabled(True)
            
            self.add_log_message(f"✅ Video başarıyla indirildi: {file_path}", "success")
            
            # Show file size
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                size_mb = file_size / (1024 * 1024)
                self.add_log_message(f"📊 Dosya boyutu: {size_mb:.2f} MB", "info")
        else:
            self.add_log_message("❌ Video indirilemedi!", "error")
            
        # Clean up worker
        if self.worker:
            self.worker = None
        
    def get_user_inputs(self):
        """Get all user inputs as a dictionary"""
        return {
            'tiktok_url': self.tiktok_url_input.text().strip(),
            'cookie_file': self.current_cookie_file,
            'gemini_api_key': self.gemini_api_key_input.text().strip(),
            'enhance_content': self.enhance_content_checkbox.isChecked(),
            'headless_mode': self.headless_checkbox.isChecked(),
            'save_credentials': self.save_credentials_checkbox.isChecked()
        }


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName(APP_TITLE)
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("TikTok Automation")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()