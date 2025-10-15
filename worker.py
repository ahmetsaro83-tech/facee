#!/usr/bin/env python3
"""
Worker Thread Module
Handles long-running automation tasks in background to prevent UI freezing
"""

from PyQt5.QtCore import QThread, pyqtSignal
import traceback
from tiktok_scraper import TikTokScraper
from video_downloader import VideoDownloader
from data_manager import DataManager
from facebook_uploader import FacebookUploader


class AutomationWorker(QThread):
    """Background worker for automation tasks"""
    
    # Signals for communication with main thread
    progress_updated = pyqtSignal(str, str)  # message, level
    progress_percentage = pyqtSignal(int)    # percentage (0-100)
    task_completed = pyqtSignal(bool, str)   # success, message
    
    def __init__(self, user_inputs):
        """
        Initialize worker with user inputs
        
        Args:
            user_inputs (dict): Dictionary containing all user inputs
        """
        super().__init__()
        self.user_inputs = user_inputs
        self.is_running = False
        self.should_stop = False
        
        # Initialize components
        self.data_manager = DataManager()
        self.tiktok_scraper = None
        self.video_downloader = None
        
    def run(self):
        """Main worker thread execution"""
        self.is_running = True
        self.should_stop = False
        
        try:
            self.progress_updated.emit("Otomasyon işlemi başlatılıyor...", "info")
            self.progress_percentage.emit(0)
            
            # Step 1: Validate TikTok URL
            if self.should_stop:
                return
                
            tiktok_url = self.user_inputs.get('tiktok_url', '').strip()
            if not self._validate_tiktok_url(tiktok_url):
                self.task_completed.emit(False, "Geçersiz TikTok URL'si!")
                return
                
            self.progress_percentage.emit(10)
            
            # Step 2: Scrape TikTok information
            if self.should_stop:
                return
                
            video_info = self._scrape_tiktok_info(tiktok_url)
            if not video_info:
                self.task_completed.emit(False, "TikTok video bilgileri alınamadı!")
                return
                
            self.progress_percentage.emit(30)
            
            # Step 3: Save video information
            if self.should_stop:
                return
                
            video_id = self._save_video_info(video_info)
            if not video_id:
                self.task_completed.emit(False, "Video bilgileri kaydedilemedi!")
                return
                
            self.progress_percentage.emit(40)
            
            # Step 4: Download video
            if self.should_stop:
                return
                
            downloaded_file = self._download_video(tiktok_url, video_info)
            if not downloaded_file:
                self.task_completed.emit(False, "Video indirilemedi!")
                return
                
            self.progress_percentage.emit(70)
            
            # Step 5: Update video status
            if self.should_stop:
                return
                
            self.data_manager.update_video_status(video_id, 'downloaded', f'Video indirildi: {downloaded_file}')
            self.progress_percentage.emit(80)
            
            # Step 6: Enhance content with Gemini (if enabled)
            enhanced_content = None
            if self.user_inputs.get('enhance_content', False):
                if self.should_stop:
                    return
                    
                enhanced_content = self._enhance_content_with_gemini(video_info)
                self.progress_percentage.emit(90)
            
            # Step 7: Prepare for Facebook upload (placeholder for now)
            if self.should_stop:
                return
                
            self.progress_updated.emit("Facebook yükleme hazırlığı tamamlandı", "success")
            self.progress_percentage.emit(100)
            
            # Complete
            success_message = f"İşlem başarıyla tamamlandı!\n"
            success_message += f"Video ID: {video_id}\n"
            success_message += f"İndirilen dosya: {downloaded_file}\n"
            if enhanced_content:
                success_message += f"İçerik Gemini ile zenginleştirildi"
                
            self.task_completed.emit(True, success_message)
            
        except Exception as e:
            error_message = f"İşlem sırasında hata oluştu: {str(e)}"
            self.progress_updated.emit(error_message, "error")
            self.progress_updated.emit(f"Hata detayı: {traceback.format_exc()}", "error")
            self.task_completed.emit(False, error_message)
            
        finally:
            self.is_running = False
            
    def stop(self):
        """Stop the worker thread"""
        self.should_stop = True
        self.progress_updated.emit("İşlem durduruluyor...", "warning")
        
        # Clean up resources
        if self.tiktok_scraper and hasattr(self.tiktok_scraper, 'driver') and self.tiktok_scraper.driver:
            try:
                self.tiktok_scraper.driver.quit()
            except:
                pass
                
        if self.video_downloader and hasattr(self.video_downloader, 'driver') and self.video_downloader.driver:
            try:
                self.video_downloader.driver.quit()
            except:
                pass
                
    def _validate_tiktok_url(self, url):
        """Validate TikTok URL"""
        try:
            self.progress_updated.emit("TikTok URL'si doğrulanıyor...", "info")
            
            self.tiktok_scraper = TikTokScraper(headless=self.user_inputs.get('headless_mode', False))
            
            if self.tiktok_scraper.is_valid_tiktok_url(url):
                self.progress_updated.emit("TikTok URL'si geçerli ✓", "success")
                return True
            else:
                self.progress_updated.emit("Geçersiz TikTok URL'si!", "error")
                return False
                
        except Exception as e:
            self.progress_updated.emit(f"URL doğrulama hatası: {str(e)}", "error")
            return False
            
    def _scrape_tiktok_info(self, tiktok_url):
        """Scrape TikTok video information"""
        try:
            self.progress_updated.emit("TikTok video bilgileri çekiliyor...", "info")
            
            if not self.tiktok_scraper:
                self.tiktok_scraper = TikTokScraper(headless=self.user_inputs.get('headless_mode', False))
                
            video_info = self.tiktok_scraper.scrape_tiktok_info(tiktok_url)
            
            if video_info:
                self.progress_updated.emit("Video bilgileri başarıyla çekildi ✓", "success")
                self.progress_updated.emit(f"Açıklama: {video_info.get('description', 'N/A')}", "info")
                self.progress_updated.emit(f"Hashtag'ler: {', '.join(video_info.get('hashtags', []))}", "info")
                self.progress_updated.emit(f"Yazar: {video_info.get('author', 'N/A')}", "info")
                return video_info
            else:
                self.progress_updated.emit("Video bilgileri çekilemedi!", "error")
                return None
                
        except Exception as e:
            self.progress_updated.emit(f"Video bilgisi çekme hatası: {str(e)}", "error")
            return None
            
    def _save_video_info(self, video_info):
        """Save video information to database and JSON"""
        try:
            self.progress_updated.emit("Video bilgileri kaydediliyor...", "info")
            
            # Save to JSON
            json_success = self.data_manager.save_video_info_json(video_info)
            if json_success:
                self.progress_updated.emit("JSON dosyasına kaydedildi ✓", "success")
            else:
                self.progress_updated.emit("JSON kaydetme başarısız!", "warning")
                
            # Save to database
            video_id = self.data_manager.save_video_info_db(video_info)
            if video_id:
                self.progress_updated.emit(f"Veritabanına kaydedildi (ID: {video_id}) ✓", "success")
                return video_id
            else:
                self.progress_updated.emit("Veritabanı kaydetme başarısız!", "error")
                return None
                
        except Exception as e:
            self.progress_updated.emit(f"Kaydetme hatası: {str(e)}", "error")
            return None
            
    def _download_video(self, tiktok_url, video_info):
        """Download TikTok video"""
        try:
            self.progress_updated.emit("Video indiriliyor...", "info")
            
            self.video_downloader = VideoDownloader(headless=self.user_inputs.get('headless_mode', False))
            
            # Generate filename
            filename = self.video_downloader.get_video_filename(tiktok_url, video_info)
            
            # Download video
            downloaded_file = self.video_downloader.download_video(tiktok_url, filename)
            
            if downloaded_file:
                self.progress_updated.emit(f"Video başarıyla indirildi: {downloaded_file} ✓", "success")
                return downloaded_file
            else:
                self.progress_updated.emit("Video indirilemedi!", "error")
                return None
                
        except Exception as e:
            self.progress_updated.emit(f"Video indirme hatası: {str(e)}", "error")
            return None
            
    def _enhance_content_with_gemini(self, video_info):
        """Enhance content using Gemini AI (placeholder for now)"""
        try:
            self.progress_updated.emit("İçerik Gemini AI ile zenginleştiriliyor...", "info")
            
            # TODO: Implement Gemini integration in Phase 2
            # For now, just return the original content
            
            self.progress_updated.emit("Gemini entegrasyonu henüz tamamlanmadı (placeholder)", "warning")
            return video_info.get('description', '')
            
        except Exception as e:
            self.progress_updated.emit(f"Gemini zenginleştirme hatası: {str(e)}", "error")
            return None


class ScrapingWorker(QThread):
    """Worker for TikTok data scraping only"""
    
    progress_updated = pyqtSignal(str, str)  # message, level
    progress_percentage = pyqtSignal(int)    # percentage (0-100)
    scraping_completed = pyqtSignal(bool, object, object)  # success, video_info, video_id
    
    def __init__(self, user_inputs):
        super().__init__()
        self.user_inputs = user_inputs
        self.data_manager = DataManager()
        
    def run(self):
        """Run scraping process"""
        try:
            self.progress_updated.emit("TikTok verileri çekiliyor...", "info")
            self.progress_percentage.emit(10)
            
            # Initialize scraper
            scraper = TikTokScraper(headless=self.user_inputs.get('headless_mode', False))
            
            # Validate URL
            tiktok_url = self.user_inputs['tiktok_url']
            if not scraper.is_valid_tiktok_url(tiktok_url):
                self.scraping_completed.emit(False, None, None)
                return
                
            self.progress_percentage.emit(30)
            
            # Scrape video info
            video_info = scraper.scrape_tiktok_info(tiktok_url)
            if not video_info:
                self.scraping_completed.emit(False, None, None)
                return
                
            self.progress_percentage.emit(70)
            
            # Save to database and JSON
            json_success = self.data_manager.save_video_info_json(video_info)
            video_id = self.data_manager.save_video_info_db(video_info)
            
            self.progress_percentage.emit(100)
            
            if video_id:
                self.scraping_completed.emit(True, video_info, video_id)
            else:
                self.scraping_completed.emit(False, None, None)
                
        except Exception as e:
            self.progress_updated.emit(f"Scraping hatası: {str(e)}", "error")
            self.scraping_completed.emit(False, None, None)


class DownloadWorker(QThread):
    """Worker for video downloading only"""
    
    progress_updated = pyqtSignal(str, str)  # message, level
    progress_percentage = pyqtSignal(int)    # percentage (0-100)
    download_completed = pyqtSignal(bool, str)  # success, file_path
    
    def __init__(self, user_inputs):
        super().__init__()
        self.user_inputs = user_inputs
        
    def run(self):
        """Run download process"""
        try:
            self.progress_updated.emit("Video indiriliyor...", "info")
            self.progress_percentage.emit(10)
            
            # Initialize downloader
            downloader = VideoDownloader(headless=self.user_inputs.get('headless_mode', False))
            
            tiktok_url = self.user_inputs['tiktok_url']
            video_info = self.user_inputs.get('video_info', {})
            
            self.progress_percentage.emit(30)
            
            # Generate filename
            filename = downloader.get_video_filename(tiktok_url, video_info)
            
            self.progress_percentage.emit(50)
            
            # Download video using SSSTik specifically
            self.progress_updated.emit("SSSTik.io kullanılarak video indiriliyor...", "info")
            downloaded_file = downloader._download_with_ssstik(tiktok_url, filename)
            
            self.progress_percentage.emit(90)
            
            if downloaded_file:
                # Update database with file path
                from data_manager import DataManager
                data_manager = DataManager()
                
                # Get video ID from video info if available
                video_id = self.user_inputs.get('video_id')
                if video_id:
                    data_manager.update_video_file_path(video_id, downloaded_file)
                    self.progress_updated.emit(f"Veritabanı güncellendi: {downloaded_file}", "success")
                
                self.progress_percentage.emit(100)
                self.download_completed.emit(True, downloaded_file)
            else:
                self.download_completed.emit(False, "")
                
        except Exception as e:
            self.progress_updated.emit(f"Download hatası: {str(e)}", "error")
            import traceback
            self.progress_updated.emit(f"Hata detayı: {traceback.format_exc()}", "error")
            self.download_completed.emit(False, "")


class FacebookUploadWorker(QThread):
    """Worker for Facebook Reels video uploading with page selection"""
    
    progress_updated = pyqtSignal(str, str)  # message, level
    progress_percentage = pyqtSignal(int)    # percentage (0-100)
    upload_completed = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, user_inputs):
        super().__init__()
        self.user_inputs = user_inputs
        self.sb_instance = None
        
    def run(self):
        """Run Facebook Reels upload process with page selection"""
        try:
            self.progress_updated.emit("🚀 Facebook Reels yükleme işlemi başlatılıyor...", "info")
            self.progress_percentage.emit(5)
            
            # Get user inputs
            session_name = self.user_inputs.get('session_name', 'default')
            video_path = self.user_inputs['video_path']
            video_info = self.user_inputs.get('video_info', {})
            selected_page = self.user_inputs.get('selected_page', None)
            enhance_with_gemini = self.user_inputs.get('enhance_with_gemini', False)
            
            # Import required modules
            from seleniumbase import SB
            import random
            import time
            import os
            
            # Use existing global browser session
            import global_browser
            
            sb = global_browser.get_browser()
            
            if sb:
                self.progress_updated.emit("🌐 Mevcut tarayıcı oturumu kullanılıyor", "success")
                self.sb_instance = sb
                
                try:
                    # Verify we're on Facebook
                    current_url = sb.get_current_url()
                    if "facebook.com" not in current_url:
                        self.progress_updated.emit("🌐 Facebook'a yönlendiriliyor...", "info")
                        sb.cdp.get("https://www.facebook.com/")
                        sb.sleep(3)
                    
                    self.progress_percentage.emit(15)
                    
                    # Step 2: Navigate to pages list
                    self.progress_updated.emit("📄 Facebook sayfalar listesine gidiliyor...", "info")
                    sb.cdp.open("https://www.facebook.com/pages/?category=your_pages&ref=bookmarks")
                    sb.sleep(5)
                    
                    self.progress_percentage.emit(25)
                    
                    # Step 3: Select page or use profile
                    if selected_page and selected_page.get('type') == 'page':
                        self.progress_updated.emit(f"📋 Sayfa seçiliyor: {selected_page['name']}", "info")
                        success = self._select_facebook_page(sb, selected_page)
                        if not success:
                            self.upload_completed.emit(False, f"Sayfa seçilemedi: {selected_page['name']}")
                            return
                    else:
                        self.progress_updated.emit("👤 Ana profil kullanılıyor", "info")
                        sb.cdp.open("https://www.facebook.com/")
                        sb.sleep(3)
                    
                    self.progress_percentage.emit(35)
                    
                    # Step 4: Start Reels creation process
                    self.progress_updated.emit("🎬 Reels oluşturma işlemi başlatılıyor...", "info")
                    success = self._create_reels_post(sb)
                    if not success:
                        self.upload_completed.emit(False, "Reels oluşturma başlatılamadı")
                        return
                    
                    self.progress_percentage.emit(50)
                    
                    # Step 5: Upload video file
                    self.progress_updated.emit("📹 Video dosyası yükleniyor...", "info")
                    success = self._upload_video_file(sb, video_path)
                    if not success:
                        self.upload_completed.emit(False, "Video dosyası yüklenemedi")
                        return
                    
                    self.progress_percentage.emit(70)
                    
                    # Step 6: Add description and hashtags
                    self.progress_updated.emit("📝 Açıklama ve etiketler ekleniyor...", "info")
                    description = self._prepare_description(video_info, enhance_with_gemini)
                    success = self._add_description_and_tags(sb, description)
                    if not success:
                        self.upload_completed.emit(False, "Açıklama eklenemedi")
                        return
                    
                    self.progress_percentage.emit(85)
                    
                    # Step 7: Publish the Reels
                    self.progress_updated.emit("🚀 Reels yayınlanıyor...", "info")
                    success = self._publish_reels(sb)
                    if not success:
                        self.upload_completed.emit(False, "Reels yayınlanamadı")
                        return
                    
                    self.progress_percentage.emit(95)
                    
                    # Step 8: Update database
                    self.progress_updated.emit("💾 Veritabanı güncelleniyor...", "info")
                    video_id = self.user_inputs.get('video_id')
                    if video_id:
                        from data_manager import DataManager
                        data_manager = DataManager()
                        data_manager.mark_facebook_uploaded(video_id, "facebook_reels_uploaded")
                    
                    self.progress_percentage.emit(100)
                    self.upload_completed.emit(True, "✅ Reels başarıyla Facebook'a yüklendi!")
                    
                    # Keep browser open for verification
                    self.progress_updated.emit("🌐 Tarayıcı doğrulama için açık bırakılıyor...", "info")
                    time.sleep(5)  # Use time.sleep instead of sb.sleep to avoid closing browser
                    
                except Exception as e:
                    error_msg = f"Reels yükleme hatası: {str(e)}"
                    self.progress_updated.emit(error_msg, "error")
                    import traceback
                    self.progress_updated.emit(f"Hata detayı: {traceback.format_exc()}", "error")
                    self.upload_completed.emit(False, error_msg)
            else:
                # No active browser session
                self.progress_updated.emit("❌ Aktif tarayıcı oturumu bulunamadı", "error")
                self.progress_updated.emit("💡 Önce Facebook Management sekmesinden giriş yapın", "info")
                self.upload_completed.emit(False, "Aktif tarayıcı oturumu yok. Önce Facebook Management sekmesinden giriş yapın.")
                    
        except Exception as e:
            error_msg = f"Facebook upload hatası: {str(e)}"
            self.progress_updated.emit(error_msg, "error")
            import traceback
            self.progress_updated.emit(f"Hata detayı: {traceback.format_exc()}", "error")
            self.upload_completed.emit(False, error_msg)
    
    def _load_cookies(self, sb, cookie_file):
        """Load saved cookies"""
        try:
            import json
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            for cookie in cookies:
                try:
                    sb.cdp.add_cookie(cookie)
                except:
                    continue
                    
            self.progress_updated.emit("✅ Cookie'ler yüklendi", "success")
            return True
        except Exception as e:
            self.progress_updated.emit(f"Cookie yükleme hatası: {str(e)}", "error")
            return False
    
    def _select_facebook_page(self, sb, page_info):
        """Select a specific Facebook page with exact selectors"""
        try:
            page_name = page_info['name']
            self.progress_updated.emit(f"📋 Sayfa seçiliyor: {page_name}", "info")
            
            # Step 1: Click on the page selection button (first div)
            page_selector = 'div[role="none"][class="x1ja2u2z x78zum5 x2lah0s x1n2onr6 xl56j7k x6s0dn4 xozqiw3 x1q0g3np x14ldlfn x1b1wa69 xws8118 x5fzff1 x972fbf x10w94by x1qhh985 x14e42zd x9f619 x1qhmfi1 x1fq8qgq x7at6mh xkde5i4"]'
            
            try:
                if sb.cdp.is_element_visible(page_selector):
                    sb.cdp.click(page_selector)
                    self.progress_updated.emit("✅ Sayfa seçim butonuna tıklandı", "success")
                else:
                    self.progress_updated.emit("⚠️ Sayfa seçim butonu bulunamadı", "warning")
                    return True  # Continue with profile
            except:
                self.progress_updated.emit("⚠️ Sayfa seçim butonu tıklanamadı", "warning")
                return True
            
            # Step 2: Wait 2 seconds and click "Şimdi Geçiş Yap"
            sb.sleep(2)
            switch_now_selector = 'span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.xudqn12.x3x7a5m.x1f6kntn.xvq8zen.xk50ysn.xzsf02u.x1yc453h:contains("Şimdi Geçiş Yap")'
            
            try:
                if sb.cdp.is_element_visible(switch_now_selector):
                    sb.cdp.click(switch_now_selector)
                    self.progress_updated.emit("✅ 'Şimdi Geçiş Yap' butonuna tıklandı", "success")
                else:
                    self.progress_updated.emit("⚠️ 'Şimdi Geçiş Yap' butonu bulunamadı", "warning")
            except:
                self.progress_updated.emit("⚠️ 'Şimdi Geçiş Yap' butonu tıklanamadı", "warning")
            
            # Step 3: Wait 3 seconds and click "Geçiş Yap"
            sb.sleep(3)
            switch_selector = 'span.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft:contains("Geçiş Yap")'
            
            try:
                if sb.cdp.is_element_visible(switch_selector):
                    sb.cdp.click(switch_selector)
                    self.progress_updated.emit("✅ 'Geçiş Yap' butonuna tıklandı", "success")
                else:
                    self.progress_updated.emit("⚠️ 'Geçiş Yap' butonu bulunamadı", "warning")
            except:
                self.progress_updated.emit("⚠️ 'Geçiş Yap' butonu tıklanamadı", "warning")
            
            # Step 4: Wait 5 seconds for page switch
            sb.sleep(5)
            self.progress_updated.emit("✅ Sayfa geçişi tamamlandı", "success")
            
            return True
            
        except Exception as e:
            self.progress_updated.emit(f"Sayfa seçme hatası: {str(e)}", "error")
            return False
    
    def _create_reels_post(self, sb):
        """Start creating a Reels post with exact selectors"""
        try:
            # Step 1: Click Reels tab
            reels_selector = 'span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.xudqn12.x3x7a5m.x1f6kntn.xvq8zen.x1s688f.xi81zsa:contains("Reels")'
            
            try:
                if sb.cdp.is_element_visible(reels_selector):
                    sb.cdp.click(reels_selector)
                    self.progress_updated.emit("✅ Reels sekmesine tıklandı", "success")
                else:
                    self.progress_updated.emit("❌ Reels sekmesi bulunamadı", "error")
                    return False
            except:
                self.progress_updated.emit("❌ Reels sekmesi tıklanamadı", "error")
                return False
            
            # Step 2: Wait 3 seconds and click "Reels Videosu Oluştur"
            sb.sleep(3)
            create_reels_selector = 'span.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft:contains("Reels Videosu Oluştur")'
            
            try:
                if sb.cdp.is_element_visible(create_reels_selector):
                    sb.cdp.click(create_reels_selector)
                    self.progress_updated.emit("✅ Reels Videosu Oluştur butonuna tıklandı", "success")
                else:
                    self.progress_updated.emit("❌ Reels Videosu Oluştur butonu bulunamadı", "error")
                    return False
            except:
                self.progress_updated.emit("❌ Reels Videosu Oluştur butonu tıklanamadı", "error")
                return False
            
            # Step 3: Wait 10 seconds for page to load
            sb.sleep(10)
            self.progress_updated.emit("✅ Reels oluşturma sayfası yüklendi", "success")
            
            return True
            
        except Exception as e:
            self.progress_updated.emit(f"Reels oluşturma hatası: {str(e)}", "error")
            return False
    
    def _upload_video_file(self, sb, video_path):
        """Upload the video file with exact selectors"""
        try:
            # Step 1: Click the video upload icon
            upload_icon_selector = 'i[data-visualcompletion="css-img"][style*="background-image: url(&quot;https://static.xx.fbcdn.net/rsrc.php/v4/y0/r/B8zgNAqJ0xA.png&quot;); background-position: 0px -209px; background-size: auto; width: 20px; height: 20px;"]'
            
            try:
                if sb.cdp.is_element_visible(upload_icon_selector):
                    sb.cdp.click(upload_icon_selector)
                    self.progress_updated.emit("✅ Video yükleme ikonuna tıklandı", "success")
                else:
                    self.progress_updated.emit("❌ Video yükleme ikonu bulunamadı", "error")
                    return False
            except:
                self.progress_updated.emit("❌ Video yükleme ikonu tıklanamadı", "error")
                return False
            
            # Step 2: Handle file upload dialog
            sb.sleep(2)
            
            # Find file input element
            file_input_selectors = [
                'input[type="file"]',
                'input[accept*="video"]'
            ]
            
            file_uploaded = False
            for selector in file_input_selectors:
                try:
                    if sb.cdp.is_element_present(selector):
                        sb.cdp.send_keys(selector, video_path)
                        self.progress_updated.emit(f"✅ Video dosyası seçildi: {video_path}", "success")
                        file_uploaded = True
                        break
                except:
                    continue
            
            if not file_uploaded:
                self.progress_updated.emit("❌ Video dosyası yüklenemedi", "error")
                return False
            
            # Step 3: Wait 10 seconds for video processing
            sb.sleep(10)
            self.progress_updated.emit("✅ Video işleniyor...", "info")
            
            return True
            
            # Handle file dialog with PyAutoGUI
            try:
                import pyautogui
                
                # Dosya yolunu Windows formatına çevir
                windows_path = video_path.replace('/', '\\')
                
                # Dosya adı alanına odaklan
                pyautogui.hotkey('alt', 'n')
                time.sleep(0.8)
                
                # Mevcut metni temizle
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.5)
                pyautogui.press('delete')
                time.sleep(0.5)
                
                # Dosya yolunu yaz
                pyautogui.write(windows_path, interval=0.02)
                time.sleep(1)
                
                # Enter'a bas
                pyautogui.press('enter')
                
                self.progress_updated.emit(f"✅ Video dosyası seçildi: {video_path}", "success")
                time.sleep(10)  # 10 saniye video işlenmesi için bekle
                
            except Exception as e:
                self.progress_updated.emit(f"Dosya seçme hatası: {str(e)}", "error")
                return False
                
            # Look for "İleri" button after video upload with exact class
            next_selectors = [
                'div.html-div.xdj266r.xat24cr.xexx8yu.xyri2b.x18d9i69.x1c1uobl.x6s0dn4.x78zum5.xl56j7k.x14ayic.xwyz465.x1e0frkt span.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft.x1j85h84:contains("İleri")',
                'span:contains("İleri")'
            ]
            
            next_clicked = False
            for selector in next_selectors:
                try:
                    if sb.cdp.is_element_visible(selector):
                        sb.cdp.click(selector)
                        self.progress_updated.emit("✅ İleri butonuna tıklandı", "success")
                        time.sleep(5)  # 5 saniye bekle
                        next_clicked = True
                        break
                except:
                    continue
            
            if not next_clicked:
                self.progress_updated.emit("❌ İleri butonu bulunamadı", "error")
                return False
                
            return True
            
        except Exception as e:
            self.progress_updated.emit(f"Video ekleme hatası: {str(e)}", "error")
            return False
    
    def _prepare_description(self, video_info, enhance_with_gemini):
        """Prepare description with optional Gemini enhancement"""
        try:
            original_description = video_info.get('description', '')
            hashtags = video_info.get('hashtags', [])
            
            if enhance_with_gemini:
                # TODO: Implement Gemini API integration
                self.progress_updated.emit("🤖 Gemini ile içerik zenginleştirme (placeholder)", "info")
                enhanced_description = f"🎬 {original_description}\n\n"
                enhanced_description += "✨ Bu içerik AI ile zenginleştirildi\n\n"
            else:
                enhanced_description = original_description
            
            # Add hashtags
            if hashtags:
                hashtag_text = " ".join([f"#{tag}" for tag in hashtags])
                enhanced_description += f"\n\n{hashtag_text}"
            
            return enhanced_description
            
        except Exception as e:
            self.progress_updated.emit(f"Açıklama hazırlama hatası: {str(e)}", "error")
            return video_info.get('description', '')
    
    def _add_description_and_tags(self, sb, description):
        """Add description and tags to the Reels with exact selectors"""
        try:
            # Step 1: Click first "İleri" button
            first_next_selector = 'span.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft.x1j85h84:contains("İleri")'
            
            try:
                if sb.cdp.is_element_visible(first_next_selector):
                    sb.cdp.click(first_next_selector)
                    self.progress_updated.emit("✅ İlk İleri butonuna tıklandı", "success")
                else:
                    self.progress_updated.emit("❌ İlk İleri butonu bulunamadı", "error")
                    return False
            except:
                self.progress_updated.emit("❌ İlk İleri butonu tıklanamadı", "error")
                return False
            
            sb.sleep(3)
            
            # Step 2: Add description to the text area
            description_selector = 'p.xdj266r.x14z9mp.xat24cr.x1lziwak.x16tdsg8[dir="auto"]'
            
            try:
                if sb.cdp.is_element_visible(description_selector):
                    sb.cdp.click(description_selector)
                    sb.cdp.clear(description_selector)
                    if description:
                        sb.cdp.type(description_selector, description)
                        self.progress_updated.emit("✅ Açıklama eklendi", "success")
                    else:
                        self.progress_updated.emit("⚠️ Açıklama boş bırakıldı", "warning")
                else:
                    self.progress_updated.emit("⚠️ Açıklama alanı bulunamadı", "warning")
            except:
                self.progress_updated.emit("⚠️ Açıklama eklenemedi", "warning")
            
            sb.sleep(2)
            
            # Step 3: Click second "İleri" button
            second_next_selector = 'div.html-div.xdj266r.xat24cr.xexx8yu.xyri2b.x18d9i69.x1c1uobl.x6s0dn4.x78zum5.xl56j7k.x14ayic.xwyz465.x1e0frkt span.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft.x1j85h84:contains("İleri")'
            
            try:
                if sb.cdp.is_element_visible(second_next_selector):
                    sb.cdp.click(second_next_selector)
                    self.progress_updated.emit("✅ İkinci İleri butonuna tıklandı", "success")
                else:
                    self.progress_updated.emit("❌ İkinci İleri butonu bulunamadı", "error")
                    return False
            except:
                self.progress_updated.emit("❌ İkinci İleri butonu tıklanamadı", "error")
                return False
            
            # Step 4: Wait 5 seconds
            sb.sleep(5)
            
            return True
            
        except Exception as e:
            self.progress_updated.emit(f"Açıklama ekleme hatası: {str(e)}", "error")
            return False
    
    def _publish_reels(self, sb):
        """Publish the Reels with exact selector"""
        try:
            # Click "Paylaş" button
            share_selector = 'span.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft:contains("Paylaş")'
            
            try:
                if sb.cdp.is_element_visible(share_selector):
                    sb.cdp.click(share_selector)
                    self.progress_updated.emit("✅ Paylaş butonuna tıklandı", "success")
                else:
                    self.progress_updated.emit("❌ Paylaş butonu bulunamadı", "error")
                    return False
            except:
                self.progress_updated.emit("❌ Paylaş butonu tıklanamadı", "error")
                return False
            
            # Wait for publishing
            sb.sleep(5)
            self.progress_updated.emit("✅ Reels yayınlandı!", "success")
            
            return True
            
        except Exception as e:
            self.progress_updated.emit(f"Yayınlama hatası: {str(e)}", "error")
            return False


class FacebookLoginTestWorker(QThread):
    """Facebook login test worker"""
    
    progress_updated = pyqtSignal(str, str)  # message, level
    progress_percentage = pyqtSignal(int)    # percentage (0-100)
    login_completed = pyqtSignal(bool, str, str)  # success, message, cookie_file_path
    pages_discovered = pyqtSignal(list)  # discovered pages
    
    def __init__(self, user_inputs):
        super().__init__()
        self.user_inputs = user_inputs
        self.sb_instance = None
        
    def run(self):
        """Run Facebook login test"""
        try:
            session_name = self.user_inputs['session_name']
            email = self.user_inputs['email']
            password = self.user_inputs['password']
            
            self.progress_updated.emit("🚀 Facebook giriş testi başlatılıyor...", "info")
            self.progress_percentage.emit(10)
            
            # Import SeleniumBase and global_browser
            from seleniumbase import SB
            import random
            import time
            import global_browser
            
            # Check if browser is already open
            sb = global_browser.get_browser()
            if sb:
                self.progress_updated.emit("🌐 Mevcut tarayıcı oturumu kapatılıyor...", "info")
                try:
                    sb.quit()
                except:
                    pass
                global_browser.clear_browser()
            
            # Initialize browser WITHOUT context manager (we want to keep it alive)
            sb = SB(uc=True, test=True, locale="tr", ad_block=True, headless=False, maximize=True)
            sb.open("about:blank")
            self.sb_instance = sb
            
            try:
                # Facebook ana sayfasına git
                self.progress_updated.emit("🌐 Facebook.com'a gidiliyor...", "info")
                sb.activate_cdp_mode("https://www.facebook.com/")
                self.progress_percentage.emit(20)
                
                # Sayfanın yüklenmesini bekle
                self.progress_updated.emit("⏳ Sayfa yükleniyor...", "info")
                sb.sleep(random.uniform(3, 5))
                self.progress_percentage.emit(30)
                
                # Debug bilgilerini logla
                self._debug_page_info(sb)
                
                # Cookie banner'ını kapat (varsa)
                try:
                    sb.cdp.click_if_visible('button[data-cookiebanner="accept_button"]')
                    sb.sleep(1)
                except:
                    pass
                
                # Email alanını bul ve doldur
                self.progress_updated.emit("📧 Email giriliyor...", "info")
                email_selectors = [
                    'input[name="email"]',
                    'input[data-testid="royal-email"]',
                    'input#email',
                    'input[type="text"][placeholder*="mail"]',
                    'input[type="email"]'
                ]
                
                email_selector = None
                for selector in email_selectors:
                    try:
                        if sb.cdp.is_element_visible(selector):
                            email_selector = selector
                            self.progress_updated.emit(f"✅ Email alanı bulundu: {selector}", "success")
                            break
                    except:
                        continue
                
                if not email_selector:
                    raise Exception("Email alanı bulunamadı!")
                
                sb.cdp.wait_for_element_visible(email_selector, timeout=10)
                
                # Alanı temizle ve focus yap
                sb.cdp.click(email_selector)
                sb.cdp.select_all(email_selector)
                sb.sleep(random.uniform(0.3, 0.7))
                
                # İnsan gibi yazma simülasyonu
                sb.cdp.press_keys(email_selector, email)
                sb.sleep(random.uniform(0.5, 1.0))
                
                self.progress_percentage.emit(50)
                
                # Şifre alanını bul ve doldur
                self.progress_updated.emit("🔐 Şifre giriliyor...", "info")
                password_selectors = [
                    'input[name="pass"]',
                    'input[data-testid="royal-pass"]',
                    'input#pass',
                    'input[type="password"]'
                ]
                
                password_selector = None
                for selector in password_selectors:
                    try:
                        if sb.cdp.is_element_visible(selector):
                            password_selector = selector
                            self.progress_updated.emit(f"✅ Şifre alanı bulundu: {selector}", "success")
                            break
                    except:
                        continue
                
                if not password_selector:
                    raise Exception("Şifre alanı bulunamadı!")
                
                # Şifre alanına focus yap ve temizle
                sb.cdp.click(password_selector)
                sb.cdp.select_all(password_selector)
                sb.sleep(random.uniform(0.3, 0.7))
                
                # İnsan gibi şifre yazma
                sb.cdp.press_keys(password_selector, password)
                sb.sleep(random.uniform(0.5, 1.0))
                
                self.progress_percentage.emit(70)
                
                # Giriş butonuna tıkla
                self.progress_updated.emit("🔘 Giriş butonuna tıklanıyor...", "info")
                login_selectors = [
                    'button[name="login"]',
                    'button[data-testid="royal-login-button"]',
                    'button[type="submit"]',
                    'input[type="submit"][value*="Giriş"]',
                    'button:contains("Giriş")',
                    'div[role="button"]:contains("Giriş")'
                ]
                
                login_button = None
                for selector in login_selectors:
                    try:
                        if sb.cdp.is_element_visible(selector):
                            login_button = selector
                            self.progress_updated.emit(f"✅ Giriş butonu bulundu: {selector}", "success")
                            break
                    except:
                        continue
                
                if not login_button:
                    raise Exception("Giriş butonu bulunamadı!")
                
                sb.cdp.click(login_button)
                
                # Manuel doğrulama için uzun bekleme süresi
                wait_time = 30  # 30 saniye bekleme
                self.progress_updated.emit("⏳ Giriş butonuna tıklandı, manuel doğrulama bekleniyor...", "info")
                self.progress_updated.emit("🔐 2FA/CAPTCHA/Güvenlik kontrolü varsa lütfen manuel olarak tamamlayın...", "warning")
                self.progress_updated.emit(f"⏰ {wait_time} saniye bekleme süresi başladı...", "info")
                self.progress_updated.emit("💡 Bu süre içinde tarayıcıda gerekli doğrulamaları yapabilirsiniz", "info")
                
                # Belirlenen süre boyunca her saniye güncelleme
                for i in range(wait_time):
                    remaining = wait_time - i
                    if remaining > 0:
                        self.progress_updated.emit(f"⏳ Kalan süre: {remaining} saniye...", "info")
                        # Progress bar'ı 70'den 85'e kadar güncelle
                        progress = 70 + int((i / wait_time) * 15)
                        self.progress_percentage.emit(progress)
                    sb.sleep(1)
                
                self.progress_updated.emit("✅ Bekleme süresi tamamlandı, giriş durumu kontrol ediliyor...", "info")
                self.progress_percentage.emit(85)
                
                # Giriş başarılı mı kontrol et
                current_url = sb.get_current_url()
                self.progress_updated.emit(f"🔍 Giriş sonrası URL: {current_url}", "info")
                
                # Birden fazla başarı kriteri kontrol et
                success_indicators = [
                    "facebook.com" in current_url and "login" not in current_url,
                    "facebook.com" in current_url and ("home" in current_url or "feed" in current_url),
                    current_url == "https://www.facebook.com/" or current_url == "https://facebook.com/"
                ]
                
                # Sayfa elementlerini de kontrol et
                try:
                    # Ana sayfa elementlerini ara
                    home_elements = [
                        '[data-testid="Keycommand_wrapper_ModalLayer"]',
                        '[role="main"]',
                        '[data-testid="newsfeed"]',
                        'div[role="banner"]',
                        'nav[role="navigation"]'
                    ]
                    
                    element_found = False
                    for element in home_elements:
                        try:
                            if sb.cdp.is_element_visible(element):
                                self.progress_updated.emit(f"✅ Ana sayfa elementi bulundu: {element}", "success")
                                element_found = True
                                break
                        except:
                            continue
                    
                    success_indicators.append(element_found)
                except:
                    pass
                
                if any(success_indicators):
                    self.progress_updated.emit("✅ Giriş başarılı!", "success")
                    
                    # Cookie'leri kaydet
                    cookie_file_path = self._save_cookies(sb, session_name, email)
                    self.progress_percentage.emit(90)
                    
                    # Sayfaları keşfet
                    self.progress_updated.emit("🔍 Facebook sayfaları keşfediliyor...", "info")
                    discovered_pages = self._discover_facebook_pages(sb)
                    
                    if discovered_pages:
                        self.pages_discovered.emit(discovered_pages)
                        self.progress_updated.emit(f"✅ {len(discovered_pages)} sayfa keşfedildi!", "success")
                    
                    self.progress_percentage.emit(100)
                    
                    # Tarayıcıyı global olarak sakla
                    import global_browser
                    global_browser.set_browser(sb)
                    
                    self.login_completed.emit(True, "Giriş başarılı ve cookie'ler kaydedildi!", cookie_file_path)
                    
                    # Tarayıcıyı açık bırak - thread dönsün, browser global_browser'da tutulsun
                    self.progress_updated.emit("🌐 Tarayıcı açık bırakıldı - Tüm Facebook işlemleri bu tarayıcıyı kullanacak!", "success")
                    
                    # Thread returns, browser stays alive managed by global_browser
                else:
                    self.progress_updated.emit("❌ Giriş başarısız - Kontroller başarısız", "error")
                    # Debug için daha fazla bilgi
                    self._debug_page_info(sb)
                    self.login_completed.emit(False, "Giriş başarısız - Lütfen bilgilerinizi kontrol edin", "")
                    try:
                        sb.quit()
                    except:
                        pass
                        
            except Exception as e:
                self.progress_updated.emit(f"❌ Giriş hatası: {str(e)}", "error")
                self.login_completed.emit(False, str(e), "")
                try:
                    if 'sb' in locals():
                        sb.quit()
                except:
                    pass
                    
        except Exception as e:
            self.progress_updated.emit(f"❌ Genel hata: {str(e)}", "error")
            import traceback
            self.progress_updated.emit(f"Hata detayı: {traceback.format_exc()}", "error")
            self.login_completed.emit(False, f"Giriş testi hatası: {str(e)}", "")
            try:
                if 'sb' in locals():
                    sb.quit()
            except:
                pass
            
    def _debug_page_info(self, sb):
        """Debug page information"""
        try:
            current_url = sb.get_current_url()
            page_title = sb.get_title()
            self.progress_updated.emit(f"🔍 Debug - URL: {current_url}", "info")
            self.progress_updated.emit(f"🔍 Debug - Başlık: {page_title}", "info")
        except Exception as e:
            self.progress_updated.emit(f"⚠️ Debug bilgisi alınamadı: {str(e)}", "warning")
            
    def _save_cookies(self, sb, session_name, email):
        """Save cookies to file with enhanced validation"""
        try:
            import json
            import time
            import os
            
            # Get all cookies
            all_cookies = sb.cdp.get_all_cookies()
            
            # Filter only Facebook cookies
            facebook_cookies = []
            critical_cookies = ['c_user', 'xs', 'datr', 'sb', 'fr']
            found_critical = []
            
            for cookie in all_cookies:
                if isinstance(cookie, dict) and 'facebook.com' in cookie.get('domain', ''):
                    facebook_cookies.append(cookie)
                    if cookie.get('name') in critical_cookies:
                        found_critical.append(cookie['name'])
            
            self.progress_updated.emit(f"🔍 {len(facebook_cookies)} Facebook cookie'si bulundu", "info")
            self.progress_updated.emit(f"🔑 Kritik cookie'ler: {found_critical}", "info")
            
            if len(found_critical) < 3:
                self.progress_updated.emit("⚠️ Kritik cookie'ler eksik, giriş sorunları yaşanabilir", "warning")
            
            # Create safe filename
            timestamp = int(time.time())
            safe_session_name = "".join(c for c in session_name if c.isalnum() or c in "._-")
            safe_email = "".join(c for c in email.split('@')[0] if c.isalnum() or c in "._-")
            filename = f"facebook_cookies_{safe_session_name}_{safe_email}_{timestamp}.json"
            
            # Ensure cookies directory exists
            cookies_dir = os.path.join("data", "cookies")
            os.makedirs(cookies_dir, exist_ok=True)
            
            filepath = os.path.join(cookies_dir, filename)
            
            # Save with metadata
            cookie_data = {
                'session_name': session_name,
                'email': email,
                'saved_at': timestamp,
                'critical_cookies': found_critical,
                'total_cookies': len(facebook_cookies),
                'cookies': facebook_cookies
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cookie_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.progress_updated.emit(f"✅ Cookie'ler kaydedildi: {filepath}", "success")
            self.progress_updated.emit(f"📊 Toplam: {len(facebook_cookies)} cookie, Kritik: {len(found_critical)} cookie", "info")
            
            return filepath
            
        except Exception as e:
            self.progress_updated.emit(f"❌ Cookie kaydetme hatası: {str(e)}", "error")
            return ""
            
    def _discover_facebook_pages(self, sb):
        """Discover Facebook pages user can manage"""
        try:
            from facebook_uploader import FacebookUploader
            
            uploader = FacebookUploader()
            pages = uploader.get_facebook_pages(sb)
            
            self.progress_updated.emit(f"✅ {len(pages)} sayfa keşfedildi", "success")
            
            for page in pages:
                self.progress_updated.emit(f"📄 Sayfa: {page['name']} - {page['type']}", "info")
            
            return pages
            
        except Exception as e:
            self.progress_updated.emit(f"❌ Sayfa keşfi hatası: {str(e)}", "error")
            return []


class FacebookCookieLoginWorker(QThread):
    """Worker for Facebook cookie login"""
    
    progress_updated = pyqtSignal(str, str)  # message, level
    progress_percentage = pyqtSignal(int)    # percentage (0-100)
    login_completed = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, user_inputs):
        super().__init__()
        self.user_inputs = user_inputs
        
    def run(self):
        """Run cookie login process"""
        try:
            cookie_file = self.user_inputs['cookie_file']
            
            self.progress_updated.emit("🍪 Cookie dosyası ile giriş başlatılıyor...", "info")
            self.progress_percentage.emit(10)
            
            # Import required modules
            from seleniumbase import SB
            import json
            import os
            import time
            import global_browser
            
            if not os.path.exists(cookie_file):
                self.login_completed.emit(False, "Cookie dosyası bulunamadı!")
                return
            
            # Check if browser is already open
            sb = global_browser.get_browser()
            if sb:
                self.progress_updated.emit("🌐 Mevcut tarayıcı oturumu kapatılıyor...", "info")
                try:
                    sb.quit()
                except:
                    pass
                global_browser.clear_browser()
                
            # Initialize browser WITHOUT context manager (we want to keep it alive)
            sb = SB(uc=True, test=True, locale="tr", ad_block=True, headless=False, maximize=True)
            sb.open("about:blank")
            try:
                # Facebook'a git
                self.progress_updated.emit("🌐 Facebook.com'a gidiliyor...", "info")
                sb.activate_cdp_mode("https://www.facebook.com/")
                self.progress_percentage.emit(30)
                
                # Cookie'leri yükle
                self.progress_updated.emit("🍪 Cookie'ler yükleniyor...", "info")
                with open(cookie_file, 'r', encoding='utf-8') as f:
                    cookie_data = json.load(f)
                
                # Yeni format kontrolü
                if isinstance(cookie_data, dict) and 'cookies' in cookie_data:
                    # Yeni format (metadata ile)
                    cookies = cookie_data['cookies']
                    session_name = cookie_data.get('session_name', 'Bilinmiyor')
                    email = cookie_data.get('email', 'Bilinmiyor')
                    saved_at = cookie_data.get('saved_at', 0)
                    critical_cookies = cookie_data.get('critical_cookies', [])
                    
                    self.progress_updated.emit(f"📋 Session: {session_name} ({email})", "info")
                    self.progress_updated.emit(f"🔑 Kritik cookie'ler: {critical_cookies}", "info")
                    
                    # Cookie yaşını kontrol et
                    if saved_at > 0:
                        age_days = (time.time() - saved_at) / (24 * 3600)
                        self.progress_updated.emit(f"📅 Cookie yaşı: {age_days:.1f} gün", "info")
                        if age_days > 30:
                            self.progress_updated.emit("⚠️ Cookie'ler 30 günden eski, sorun yaşanabilir", "warning")
                else:
                    # Eski format (sadece cookie listesi)
                    cookies = cookie_data
                    self.progress_updated.emit("📋 Eski format cookie dosyası tespit edildi", "warning")
                
                # Cookie'leri tarayıcıya ekle
                self.progress_updated.emit(f"🍪 {len(cookies)} cookie yükleniyor...", "info")
                success_count = 0
                facebook_cookies = 0
                
                # Önce Facebook'a git (cookie yüklemek için)
                self.progress_updated.emit("🌐 Facebook domain'ine gidiliyor...", "info")
                sb.cdp.get("https://www.facebook.com/")
                sb.sleep(2)
                
                # Gelişmiş cookie yükleme sistemi (ornekfacebok.py'den)
                current_time = time.time()
                
                for i, cookie in enumerate(cookies):
                    try:
                        if isinstance(cookie, dict) and cookie.get('name') and cookie.get('value'):
                            # Facebook cookie'si kontrolü
                            domain = cookie.get('domain', '')
                            if 'facebook.com' not in domain:
                                continue
                            
                            # Cookie süresini kontrol et
                            expires = cookie.get('expires', 0)
                            if expires != 0 and expires < current_time:
                                self.progress_updated.emit(f"⚠️ Cookie süresi dolmuş: {cookie['name']}", "warning")
                                continue
                            
                            facebook_cookies += 1
                            
                            # Yöntem 1: CDP ile yükle (daha güvenli)
                            try:
                                clean_cookie = {
                                    'name': cookie['name'],
                                    'value': cookie['value'],
                                    'domain': cookie.get('domain', '.facebook.com'),
                                    'path': cookie.get('path', '/'),
                                    'secure': cookie.get('secure', True),
                                    'httpOnly': cookie.get('httpOnly', False),
                                    'sameSite': cookie.get('sameSite', 'Lax')
                                }
                                
                                if 'expires' in cookie and cookie['expires'] != 0:
                                    clean_cookie['expires'] = cookie['expires']
                                
                                sb.cdp.set_all_cookies([clean_cookie])
                                
                            except Exception as cdp_error:
                                self.progress_updated.emit(f"⚠️ CDP cookie yükleme hatası: {cookie['name']} - {str(cdp_error)}", "warning")
                            
                            # Yöntem 2: JavaScript ile direkt yükle (daha etkili)
                            try:
                                # Cookie string'i güvenli şekilde oluştur
                                cookie_value = cookie['value'].replace("'", "\\'").replace('"', '\\"')
                                cookie_string = f"{cookie['name']}={cookie_value}"
                                
                                # Domain ekle
                                if cookie.get('domain'):
                                    cookie_string += f"; domain={cookie['domain']}"
                                
                                # Path ekle
                                if cookie.get('path'):
                                    cookie_string += f"; path={cookie['path']}"
                                
                                # Secure flag
                                if cookie.get('secure'):
                                    cookie_string += "; secure"
                                
                                # SameSite
                                if cookie.get('sameSite'):
                                    cookie_string += f"; samesite={cookie['sameSite']}"
                                
                                # HttpOnly (JavaScript ile set edilemez ama deneyebiliriz)
                                js_code = f"document.cookie = '{cookie_string}'"
                                sb.execute_script(js_code)
                                
                            except Exception as js_error:
                                self.progress_updated.emit(f"⚠️ JS cookie yükleme hatası: {cookie['name']} - {str(js_error)}", "warning")
                            
                            success_count += 1
                            status = "🔑" if cookie['name'] in ['c_user', 'xs', 'datr', 'sb', 'fr'] else "✅"
                            self.progress_updated.emit(f"{status} Cookie {i+1}: {cookie['name']}", "info")
                            
                    except Exception as cookie_error:
                        self.progress_updated.emit(f"❌ Cookie {i+1} genel hatası: {str(cookie_error)}", "error")
                        continue
                
                self.progress_updated.emit(f"✅ {success_count}/{len(cookies)} cookie yüklendi ({facebook_cookies} Facebook cookie'si)", "success")
                
                if facebook_cookies == 0:
                    self.login_completed.emit(False, "Facebook cookie'si bulunamadı")
                    return
                elif facebook_cookies < 4:
                    self.progress_updated.emit("⚠️ Az sayıda Facebook cookie'si var, giriş başarısız olabilir", "warning")
                
                # Kritik cookie'lerin varlığını kontrol et
                critical_cookies = ['c_user', 'xs', 'datr']
                loaded_critical = []
                
                for cookie in cookies:
                    if cookie.get('name') in critical_cookies and 'facebook.com' in cookie.get('domain', ''):
                        loaded_critical.append(cookie['name'])
                
                self.progress_updated.emit(f"🔑 Kritik cookie'ler: {loaded_critical}", "info")
                
                if len(loaded_critical) < 2:
                    self.progress_updated.emit("⚠️ Kritik cookie'ler eksik, giriş başarısız olabilir", "warning")
                
                self.progress_percentage.emit(60)
                
                # Cookie'ler yüklendikten sonra sayfa yenileme
                self.progress_updated.emit("🔄 Cookie'ler yüklendi, sayfa yenileniyor...", "info")
                sb.cdp.reload()
                sb.sleep(4)
                
                # Cookie'lerin işlenmesi için bekleme
                self.progress_updated.emit("⏳ Cookie'lerin işlenmesi bekleniyor...", "info")
                sb.sleep(3)
                
                self.progress_percentage.emit(80)
                
                # Giriş kontrolü
                current_url = sb.get_current_url()
                page_title = sb.get_title()
                self.progress_updated.emit(f"🔍 Cookie giriş sonrası URL: {current_url}", "info")
                self.progress_updated.emit(f"🔍 Sayfa başlığı: {page_title}", "info")
                
                # Giriş başarı kontrolü
                success_indicators = [
                    "facebook.com" in current_url and "login" not in current_url,
                    "facebook.com" in current_url and ("home" in current_url or "feed" in current_url),
                    current_url == "https://www.facebook.com/" or current_url == "https://facebook.com/"
                ]
                
                # Sayfa elementlerini kontrol et
                try:
                    home_elements = [
                        '[role="main"]',
                        '[data-testid="newsfeed"]',
                        'div[role="banner"]',
                        'nav[role="navigation"]'
                    ]
                    
                    element_found = False
                    for element in home_elements:
                        try:
                            if sb.cdp.is_element_visible(element):
                                self.progress_updated.emit(f"✅ Ana sayfa elementi bulundu: {element}", "success")
                                element_found = True
                                break
                        except:
                            continue
                    
                    success_indicators.append(element_found)
                except:
                    pass
                
                self.progress_percentage.emit(100)
                
                if any(success_indicators):
                    # Store browser in global_browser for reuse
                    global_browser.set_browser(sb)
                    
                    self.progress_updated.emit("✅ Cookie ile giriş başarılı!", "success")
                    self.progress_updated.emit("🌐 Tarayıcı açık bırakıldı - Tüm Facebook işlemleri bu tarayıcıyı kullanacak", "info")
                    self.login_completed.emit(True, "Cookie ile giriş başarılı! Tarayıcı açık bırakıldı.")
                    
                    # Keep thread alive but don't block (browser will stay open)
                    # The browser will be managed by global_browser module
                else:
                    self.progress_updated.emit("❌ Cookie ile giriş başarısız", "error")
                    self.login_completed.emit(False, "Cookie ile giriş başarısız - Cookie'ler geçersiz olabilir")
                    try:
                        sb.quit()
                    except:
                        pass
                        
            except Exception as e:
                self.progress_updated.emit(f"❌ Cookie giriş hatası: {str(e)}", "error")
                self.login_completed.emit(False, str(e))
                try:
                    if 'sb' in locals():
                        sb.quit()
                except:
                    pass
                    
        except Exception as e:
            self.progress_updated.emit(f"❌ Genel hata: {str(e)}", "error")
            import traceback
            self.progress_updated.emit(f"Hata detayı: {traceback.format_exc()}", "error")
            self.login_completed.emit(False, f"Cookie giriş hatası: {str(e)}")
            try:
                if 'sb' in locals():
                    sb.quit()
            except:
                pass