#!/usr/bin/env python3
"""
Data Manager Module
Handles JSON data storage and retrieval for TikTok video information
"""

import json
import os
import sqlite3
import datetime
from typing import Dict, List, Optional
from config import DATA_DIR


class DataManager:
    """Manages data storage for TikTok video information"""
    
    def __init__(self):
        """Initialize data manager with database and JSON file paths"""
        self.json_file_path = os.path.join(DATA_DIR, "tiktok_videos.json")
        self.db_path = os.path.join(DATA_DIR, "tiktok_database.db")
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create videos table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    description TEXT,
                    hashtags TEXT,
                    mentions TEXT,
                    full_text TEXT,
                    video_download_url TEXT,
                    author TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'scraped',
                    facebook_uploaded BOOLEAN DEFAULT FALSE,
                    facebook_post_id TEXT,
                    notes TEXT
                )
            ''')
            
            # Create processing_log table for tracking operations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processing_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER,
                    operation TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (video_id) REFERENCES videos (id)
                )
            ''')
            
            # Create facebook_sessions table for session management
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS facebook_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT UNIQUE NOT NULL,
                    email TEXT NOT NULL,
                    cookie_file_path TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    last_login TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            ''')
            
            # Create facebook_pages table for page management
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS facebook_pages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    page_name TEXT NOT NULL,
                    page_id TEXT,
                    page_url TEXT,
                    is_default BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES facebook_sessions (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            print("Veritabanı başarıyla başlatıldı!")
            
        except Exception as e:
            print(f"Veritabanı başlatma hatası: {str(e)}")
            raise
            
    def save_video_info_json(self, video_info: Dict) -> bool:
        """
        Save video information to JSON file
        
        Args:
            video_info (dict): Video information dictionary
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load existing data
            existing_data = self.load_all_videos_json()
            
            # Add timestamp if not present
            if 'timestamp' not in video_info:
                video_info['timestamp'] = datetime.datetime.now().isoformat()
                
            # Add or update video info
            video_url = video_info.get('url', '')
            
            # Check if video already exists
            updated = False
            for i, existing_video in enumerate(existing_data):
                if existing_video.get('url') == video_url:
                    existing_data[i] = video_info
                    updated = True
                    break
                    
            if not updated:
                existing_data.append(video_info)
                
            # Save to JSON file
            with open(self.json_file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
                
            print(f"Video bilgileri JSON dosyasına kaydedildi: {self.json_file_path}")
            return True
            
        except Exception as e:
            print(f"JSON kaydetme hatası: {str(e)}")
            return False
            
    def save_video_info_db(self, video_info: Dict) -> Optional[int]:
        """
        Save video information to SQLite database
        
        Args:
            video_info (dict): Video information dictionary
            
        Returns:
            int: Video ID if successful, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert lists to JSON strings for storage
            hashtags_json = json.dumps(video_info.get('hashtags', []), ensure_ascii=False)
            mentions_json = json.dumps(video_info.get('mentions', []), ensure_ascii=False)
            
            # Check if video already exists
            cursor.execute('SELECT id FROM videos WHERE url = ?', (video_info.get('url', ''),))
            existing_video = cursor.fetchone()
            
            if existing_video:
                # Update existing video
                video_id = existing_video[0]
                cursor.execute('''
                    UPDATE videos SET 
                        description = ?, hashtags = ?, mentions = ?, full_text = ?,
                        video_download_url = ?, author = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (
                    video_info.get('description', ''),
                    hashtags_json,
                    mentions_json,
                    video_info.get('full_text', ''),
                    video_info.get('video_download_url', ''),
                    video_info.get('author', ''),
                    video_id
                ))
                print(f"Video bilgileri güncellendi (ID: {video_id})")
                
            else:
                # Insert new video
                cursor.execute('''
                    INSERT INTO videos (url, description, hashtags, mentions, full_text, 
                                      video_download_url, author, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    video_info.get('url', ''),
                    video_info.get('description', ''),
                    hashtags_json,
                    mentions_json,
                    video_info.get('full_text', ''),
                    video_info.get('video_download_url', ''),
                    video_info.get('author', ''),
                    'scraped'
                ))
                video_id = cursor.lastrowid
                print(f"Yeni video kaydedildi (ID: {video_id})")
                
            # Log the operation
            self.log_operation(cursor, video_id, 'scrape', 'success', 'Video bilgileri başarıyla kaydedildi')
            
            conn.commit()
            conn.close()
            
            return video_id
            
        except Exception as e:
            print(f"Veritabanı kaydetme hatası: {str(e)}")
            return None
            
    def load_all_videos_json(self) -> List[Dict]:
        """
        Load all video information from JSON file
        
        Returns:
            list: List of video information dictionaries
        """
        try:
            if os.path.exists(self.json_file_path):
                with open(self.json_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
            
        except Exception as e:
            print(f"JSON yükleme hatası: {str(e)}")
            return []
            
    def get_video_by_url(self, url: str) -> Optional[Dict]:
        """
        Get video information by URL from database
        
        Args:
            url (str): TikTok video URL
            
        Returns:
            dict: Video information or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, url, description, hashtags, mentions, full_text,
                       video_download_url, author, created_at, updated_at, status,
                       facebook_uploaded, facebook_post_id, notes
                FROM videos WHERE url = ?
            ''', (url,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'url': row[1],
                    'description': row[2],
                    'hashtags': json.loads(row[3]) if row[3] else [],
                    'mentions': json.loads(row[4]) if row[4] else [],
                    'full_text': row[5],
                    'video_download_url': row[6],
                    'author': row[7],
                    'created_at': row[8],
                    'updated_at': row[9],
                    'status': row[10],
                    'facebook_uploaded': bool(row[11]),
                    'facebook_post_id': row[12],
                    'notes': row[13]
                }
            return None
            
        except Exception as e:
            print(f"Video arama hatası: {str(e)}")
            return None
            
    def get_all_videos(self) -> List[Dict]:
        """
        Get all videos from database
        
        Returns:
            list: List of all video information dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, url, description, hashtags, mentions, full_text,
                       video_download_url, author, created_at, updated_at, status,
                       facebook_uploaded, facebook_post_id, notes
                FROM videos ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            videos = []
            for row in rows:
                videos.append({
                    'id': row[0],
                    'url': row[1],
                    'description': row[2],
                    'hashtags': json.loads(row[3]) if row[3] else [],
                    'mentions': json.loads(row[4]) if row[4] else [],
                    'full_text': row[5],
                    'video_download_url': row[6],
                    'author': row[7],
                    'created_at': row[8],
                    'updated_at': row[9],
                    'status': row[10],
                    'facebook_uploaded': bool(row[11]),
                    'facebook_post_id': row[12],
                    'notes': row[13]
                })
                
            return videos
            
        except Exception as e:
            print(f"Tüm videoları getirme hatası: {str(e)}")
            return []
            
    def update_video_status(self, video_id: int, status: str, notes: str = None) -> bool:
        """
        Update video processing status
        
        Args:
            video_id (int): Video ID
            status (str): New status
            notes (str): Optional notes
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE videos SET status = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, notes, video_id))
            
            # Log the operation
            self.log_operation(cursor, video_id, 'status_update', 'success', f'Status güncellendi: {status}')
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Status güncelleme hatası: {str(e)}")
            return False
            
    def update_video_file_path(self, video_id: int, file_path: str) -> bool:
        """
        Update video with downloaded file path
        
        Args:
            video_id (int): Video ID
            file_path (str): Path to downloaded video file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE videos SET video_download_url = ?, status = 'downloaded', 
                                updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (file_path, video_id))
            
            # Log the operation
            self.log_operation(cursor, video_id, 'download', 'success', f'Video indirildi: {file_path}')
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Video dosya yolu güncelleme hatası: {str(e)}")
            return False
            
    def mark_facebook_uploaded(self, video_id: int, facebook_post_id: str = None) -> bool:
        """
        Mark video as uploaded to Facebook
        
        Args:
            video_id (int): Video ID
            facebook_post_id (str): Facebook post ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE videos SET facebook_uploaded = TRUE, facebook_post_id = ?, 
                                status = 'completed', updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (facebook_post_id, video_id))
            
            # Log the operation
            self.log_operation(cursor, video_id, 'facebook_upload', 'success', 'Facebook\'a yüklendi')
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Facebook upload işaretleme hatası: {str(e)}")
            return False
            
    def log_operation(self, cursor, video_id: int, operation: str, status: str, message: str = None):
        """
        Log an operation to the processing log
        
        Args:
            cursor: Database cursor
            video_id (int): Video ID
            operation (str): Operation type
            status (str): Operation status
            message (str): Optional message
        """
        try:
            cursor.execute('''
                INSERT INTO processing_log (video_id, operation, status, message)
                VALUES (?, ?, ?, ?)
            ''', (video_id, operation, status, message))
            
        except Exception as e:
            print(f"Log kaydetme hatası: {str(e)}")
            
    def get_processing_logs(self, video_id: int = None) -> List[Dict]:
        """
        Get processing logs for a video or all videos
        
        Args:
            video_id (int): Optional video ID to filter logs
            
        Returns:
            list: List of log entries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if video_id:
                cursor.execute('''
                    SELECT id, video_id, operation, status, message, timestamp
                    FROM processing_log WHERE video_id = ?
                    ORDER BY timestamp DESC
                ''', (video_id,))
            else:
                cursor.execute('''
                    SELECT id, video_id, operation, status, message, timestamp
                    FROM processing_log ORDER BY timestamp DESC
                ''')
                
            rows = cursor.fetchall()
            conn.close()
            
            logs = []
            for row in rows:
                logs.append({
                    'id': row[0],
                    'video_id': row[1],
                    'operation': row[2],
                    'status': row[3],
                    'message': row[4],
                    'timestamp': row[5]
                })
                
            return logs
            
        except Exception as e:
            print(f"Log getirme hatası: {str(e)}")
            return []
            
    # Facebook Session Management Methods
    def save_facebook_session(self, session_name: str, email: str, cookie_file_path: str = None) -> Optional[int]:
        """Save Facebook session to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO facebook_sessions 
                (session_name, email, cookie_file_path, last_login, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (session_name, email, cookie_file_path))
            
            session_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return session_id
            
        except Exception as e:
            print(f"Facebook session kaydetme hatası: {str(e)}")
            return None
            
    def get_facebook_sessions(self) -> List[Dict]:
        """Get all Facebook sessions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, session_name, email, cookie_file_path, is_active, 
                       last_login, created_at, notes
                FROM facebook_sessions 
                ORDER BY last_login DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            sessions = []
            for row in rows:
                sessions.append({
                    'id': row[0],
                    'session_name': row[1],
                    'email': row[2],
                    'cookie_file_path': row[3],
                    'is_active': bool(row[4]),
                    'last_login': row[5],
                    'created_at': row[6],
                    'notes': row[7]
                })
                
            return sessions
            
        except Exception as e:
            print(f"Facebook session getirme hatası: {str(e)}")
            return []
            
    def save_facebook_page(self, session_id: int, page_name: str, page_id: str = None, 
                          page_url: str = None, is_default: bool = False) -> Optional[int]:
        """Save Facebook page to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # If this is set as default, unset other defaults for this session
            if is_default:
                cursor.execute('''
                    UPDATE facebook_pages SET is_default = FALSE 
                    WHERE session_id = ?
                ''', (session_id,))
            
            cursor.execute('''
                INSERT INTO facebook_pages 
                (session_id, page_name, page_id, page_url, is_default)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, page_name, page_id, page_url, is_default))
            
            page_db_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return page_db_id
            
        except Exception as e:
            print(f"Facebook sayfa kaydetme hatası: {str(e)}")
            return None
            
    def get_facebook_pages(self, session_id: int = None) -> List[Dict]:
        """Get Facebook pages for a session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if session_id:
                cursor.execute('''
                    SELECT id, session_id, page_name, page_id, page_url, is_default, created_at
                    FROM facebook_pages 
                    WHERE session_id = ?
                    ORDER BY is_default DESC, page_name ASC
                ''', (session_id,))
            else:
                cursor.execute('''
                    SELECT id, session_id, page_name, page_id, page_url, is_default, created_at
                    FROM facebook_pages 
                    ORDER BY session_id, is_default DESC, page_name ASC
                ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            pages = []
            for row in rows:
                pages.append({
                    'id': row[0],
                    'session_id': row[1],
                    'page_name': row[2],
                    'page_id': row[3],
                    'page_url': row[4],
                    'is_default': bool(row[5]),
                    'created_at': row[6]
                })
                
            return pages
            
        except Exception as e:
            print(f"Facebook sayfa getirme hatası: {str(e)}")
            return []


def test_data_manager():
    """Test function for the data manager"""
    dm = DataManager()
    
    # Test video info
    test_video = {
        'url': 'https://www.tiktok.com/@test/video/123456789',
        'description': 'Test video açıklaması',
        'hashtags': ['#test', '#example'],
        'mentions': ['@testuser'],
        'full_text': 'Test video açıklaması #test #example @testuser',
        'video_download_url': 'https://example.com/video.mp4',
        'author': '@testauthor'
    }
    
    # Test JSON save
    print("JSON kaydetme testi...")
    dm.save_video_info_json(test_video)
    
    # Test DB save
    print("Veritabanı kaydetme testi...")
    video_id = dm.save_video_info_db(test_video)
    
    if video_id:
        print(f"Video kaydedildi, ID: {video_id}")
        
        # Test retrieval
        retrieved_video = dm.get_video_by_url(test_video['url'])
        print("Geri alınan video:", retrieved_video)
        
        # Test status update
        dm.update_video_status(video_id, 'processing', 'Test işlemi')
        
        # Test logs
        logs = dm.get_processing_logs(video_id)
        print("İşlem logları:", logs)


if __name__ == "__main__":
    test_data_manager()