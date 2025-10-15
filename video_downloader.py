#!/usr/bin/env python3
"""
Video Downloader Module
Downloads TikTok videos using external download services
"""

import os
import time
import requests
from seleniumbase import SB
from urllib.parse import urlparse
from config import DOWNLOADS_DIR, BROWSER_HEADLESS, TIKTOK_DOWNLOAD_TIMEOUT


class VideoDownloader:
    """Downloads TikTok videos using external services"""
    
    def __init__(self, headless=BROWSER_HEADLESS):
        """Initialize the video downloader"""
        self.headless = headless
        self.driver = None
        self.download_services = [
            {
                'name': 'SnapTik',
                'url': 'https://snaptik.app/',
                'url_input_selector': 'input[name="url"]',
                'submit_button_selector': 'button[type="submit"]',
                'download_link_selector': 'a[download]',
                'wait_time': 5
            },
            {
                'name': 'SSSTikTok',
                'url': 'https://ssstik.io/tr',
                'url_input_selector': 'input#main_page_text',
                'submit_button_selector': 'button#submit',
                'download_link_selector': 'a.without_watermark',
                'wait_time': 8
            },
            {
                'name': 'TikDD',
                'url': 'https://tikdd.cc/',
                'url_input_selector': 'input[name="url"]',
                'submit_button_selector': 'button.btn-go',
                'download_link_selector': 'a.btn.btn-success',
                'wait_time': 6
            },
            {
                'name': 'SaveTT',
                'url': 'https://savett.cc/',
                'url_input_selector': 'input[name="q"]',
                'submit_button_selector': 'button[type="submit"]',
                'download_link_selector': 'a.btn-success',
                'wait_time': 7
            }
        ]
        
    def download_video(self, tiktok_url, output_filename=None):
        """
        Download TikTok video using external services
        
        Args:
            tiktok_url (str): TikTok video URL
            output_filename (str): Optional custom filename
            
        Returns:
            str: Path to downloaded video file or None if failed
        """
        print(f"Video indirme işlemi başlatılıyor: {tiktok_url}")
        
        # Try each download service
        for service in self.download_services:
            try:
                print(f"{service['name']} servisi deneniyor...")
                download_path = self._try_download_service(tiktok_url, service, output_filename)
                
                if download_path and os.path.exists(download_path):
                    print(f"Video başarıyla indirildi: {download_path}")
                    return download_path
                    
            except Exception as e:
                print(f"{service['name']} servisi hatası: {str(e)}")
                continue
                
        print("Tüm servisler denendi, video indirilemedi!")
        return None
        
    def _try_download_service(self, tiktok_url, service, output_filename=None):
        """
        Try to download video using a specific service
        
        Args:
            tiktok_url (str): TikTok video URL
            service (dict): Service configuration
            output_filename (str): Optional custom filename
            
        Returns:
            str: Path to downloaded video or None if failed
        """
        try:
            print(f"{service['name']} sayfası açılıyor...")
            
            # Special handling for SSSTikTok
            if service['name'] == 'SSSTikTok':
                return self._download_with_ssstik(tiktok_url, output_filename)
            
            # Use SB context manager for other services
            with SB(uc=True, headless=self.headless, test=True) as sb:
                # Open download service
                sb.open(service['url'])
                
                # Wait for page to load
                time.sleep(2)
                
                # Find and fill URL input
                sb.type(service['url_input_selector'], tiktok_url)
                
                print("TikTok URL'si yapıştırıldı, işlem başlatılıyor...")
                
                # Click submit button
                sb.click(service['submit_button_selector'])
                
                # Wait for processing (different wait times for different services)
                wait_time = service.get('wait_time', 5)
                print(f"İşlem bekleniyor ({wait_time} saniye)...")
                time.sleep(wait_time)
                
                # Look for download link
                download_url = None
                max_attempts = 10
                
                for attempt in range(max_attempts):
                    try:
                        if sb.is_element_visible(service['download_link_selector']):
                            download_url = sb.get_attribute(service['download_link_selector'], 'href')
                            if download_url:
                                break
                    except:
                        pass
                        
                    print(f"İndirme linki bekleniyor... ({attempt + 1}/{max_attempts})")
                    time.sleep(2)
                    
                if not download_url:
                    print(f"{service['name']} servisinde indirme linki bulunamadı!")
                    return None
                    
                print(f"İndirme URL'si bulundu: {download_url}")
                
                # Download the video file
                return self._download_file(download_url, output_filename)
            
        except Exception as e:
            print(f"Servis hatası: {str(e)}")
            return None
            
    def _download_with_ssstik(self, tiktok_url, output_filename=None):
        """
        Special method for downloading from SSSTik.io
        
        Args:
            tiktok_url (str): TikTok video URL
            output_filename (str): Optional custom filename
            
        Returns:
            str: Path to downloaded video or None if failed
        """
        try:
            print("SSSTik.io sayfası açılıyor...")
            
            with SB(uc=True, headless=self.headless, test=True) as sb:
                # Configure download directory
                download_dir = os.path.abspath(DOWNLOADS_DIR)
                
                # Set download preferences
                prefs = {
                    "download.default_directory": download_dir,
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "safebrowsing.enabled": True
                }
                
                # Open SSSTik.io
                sb.open("https://ssstik.io/tr")
                
                # Wait for page to load
                time.sleep(2)
                
                # Find and clear the input field
                input_selector = 'input#main_page_text'
                sb.wait_for_element(input_selector, timeout=10)
                sb.clear(input_selector)
                
                # Type the TikTok URL
                sb.type(input_selector, tiktok_url)
                print(f"TikTok URL'si yapıştırıldı: {tiktok_url}")
                
                # Wait 2 seconds as requested
                time.sleep(2)
                
                # Click the submit button
                submit_selector = 'button#submit'
                sb.click(submit_selector)
                print("Download butonuna basıldı, işlem başlatılıyor...")
                
                # Wait 3 seconds as requested
                time.sleep(3)
                
                # Look for the "Without watermark" download link
                download_selectors = [
                    'a.without_watermark',
                    'a[class*="without_watermark"]',
                    'a.download_link.without_watermark',
                    'a.pure-button.pure-button-primary.without_watermark'
                ]
                
                download_link_found = False
                download_url = None
                
                # Try to find download link with multiple attempts
                max_attempts = 15
                for attempt in range(max_attempts):
                    for selector in download_selectors:
                        try:
                            if sb.is_element_visible(selector):
                                download_url = sb.get_attribute(selector, 'href')
                                if download_url and download_url.startswith('http'):
                                    print(f"İndirme linki bulundu: {selector}")
                                    download_link_found = True
                                    break
                        except:
                            continue
                    
                    if download_link_found:
                        break
                        
                    print(f"İndirme linki aranıyor... ({attempt + 1}/{max_attempts})")
                    time.sleep(1)
                
                if not download_link_found or not download_url:
                    print("SSSTik.io'da indirme linki bulunamadı!")
                    return None
                
                print(f"İndirme URL'si bulundu: {download_url}")
                
                # Generate filename if not provided
                if not output_filename:
                    video_id = self._extract_video_id_from_url(tiktok_url)
                    output_filename = f"tiktok_{video_id}_{int(time.time())}.mp4"
                
                # Ensure filename has .mp4 extension
                if not output_filename.endswith('.mp4'):
                    output_filename += '.mp4'
                
                file_path = os.path.join(download_dir, output_filename)
                
                # Download the file using requests
                print("Video dosyası indiriliyor...")
                success = self._download_file_direct(download_url, file_path)
                
                if success and os.path.exists(file_path):
                    print(f"Video başarıyla indirildi: {file_path}")
                    return file_path
                else:
                    print("Video indirme başarısız!")
                    return None
                
        except Exception as e:
            print(f"SSSTik indirme hatası: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
            
    def _download_file_direct(self, download_url, file_path):
        """
        Download file directly using requests
        
        Args:
            download_url (str): Direct download URL
            file_path (str): Local file path to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(download_url, headers=headers, stream=True, timeout=60)
            response.raise_for_status()
            
            # Check if response is actually a video file
            content_type = response.headers.get('content-type', '')
            if 'video' not in content_type and 'octet-stream' not in content_type:
                print(f"Uyarı: Beklenen video dosyası değil, content-type: {content_type}")
            
            # Save file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Verify file was downloaded and has content
            if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:  # At least 1KB
                return True
            else:
                print("İndirilen dosya çok küçük veya boş!")
                return False
                
        except Exception as e:
            print(f"Direkt dosya indirme hatası: {str(e)}")
            return False
            
    def _extract_video_id_from_url(self, tiktok_url):
        """Extract video ID from TikTok URL"""
        import re
        match = re.search(r'/video/(\d+)', tiktok_url)
        if match:
            return match.group(1)
        return str(int(time.time()))
                
    def _download_file(self, download_url, output_filename=None):
        """
        Download file from URL
        
        Args:
            download_url (str): Direct download URL
            output_filename (str): Optional custom filename
            
        Returns:
            str: Path to downloaded file or None if failed
        """
        try:
            print("Dosya indiriliyor...")
            
            # Get filename from URL or use custom name
            if output_filename:
                filename = output_filename
                if not filename.endswith('.mp4'):
                    filename += '.mp4'
            else:
                parsed_url = urlparse(download_url)
                filename = os.path.basename(parsed_url.path)
                if not filename or not filename.endswith('.mp4'):
                    filename = f"tiktok_video_{int(time.time())}.mp4"
                    
            file_path = os.path.join(DOWNLOADS_DIR, filename)
            
            # Download with requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(download_url, headers=headers, stream=True, timeout=60)
            response.raise_for_status()
            
            # Save file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            # Verify file was downloaded
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                print(f"Dosya başarıyla indirildi: {file_path}")
                return file_path
            else:
                print("Dosya indirme başarısız!")
                return None
                
        except Exception as e:
            print(f"Dosya indirme hatası: {str(e)}")
            return None
            
    def get_video_filename(self, tiktok_url, video_info=None):
        """
        Generate a suitable filename for the video
        
        Args:
            tiktok_url (str): TikTok video URL
            video_info (dict): Optional video information
            
        Returns:
            str: Generated filename
        """
        try:
            # Extract video ID from URL
            import re
            video_id_match = re.search(r'/video/(\d+)', tiktok_url)
            video_id = video_id_match.group(1) if video_id_match else str(int(time.time()))
            
            # Use author name if available
            if video_info and video_info.get('author'):
                author = video_info['author'].replace('@', '').replace(' ', '_')
                filename = f"{author}_{video_id}.mp4"
            else:
                filename = f"tiktok_{video_id}.mp4"
                
            # Clean filename
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            
            return filename
            
        except Exception as e:
            print(f"Dosya adı oluşturma hatası: {str(e)}")
            return f"tiktok_video_{int(time.time())}.mp4"
            
    def cleanup_old_downloads(self, max_age_days=7):
        """
        Clean up old downloaded files
        
        Args:
            max_age_days (int): Maximum age of files to keep in days
        """
        try:
            current_time = time.time()
            max_age_seconds = max_age_days * 24 * 60 * 60
            
            for filename in os.listdir(DOWNLOADS_DIR):
                file_path = os.path.join(DOWNLOADS_DIR, filename)
                
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getctime(file_path)
                    
                    if file_age > max_age_seconds:
                        os.remove(file_path)
                        print(f"Eski dosya silindi: {filename}")
                        
        except Exception as e:
            print(f"Dosya temizleme hatası: {str(e)}")


def test_downloader():
    """Test function for the video downloader"""
    test_url = "https://www.tiktok.com/@username/video/1234567890"
    
    downloader = VideoDownloader(headless=False)
    
    try:
        downloaded_file = downloader.download_video(test_url)
        
        if downloaded_file:
            print(f"Test başarılı! İndirilen dosya: {downloaded_file}")
        else:
            print("Test başarısız!")
            
    except Exception as e:
        print(f"Test hatası: {str(e)}")


if __name__ == "__main__":
    test_downloader()