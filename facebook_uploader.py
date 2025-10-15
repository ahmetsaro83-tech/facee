#!/usr/bin/env python3
"""
Facebook Uploader Module
Handles Facebook login, cookie management, and video uploading
"""

import os
import json
import time
import random
from seleniumbase import SB
from config import DOWNLOADS_DIR, BROWSER_HEADLESS


class FacebookUploader:
    """Facebook video uploader with cookie management"""
    
    def __init__(self, headless=BROWSER_HEADLESS):
        """Initialize Facebook uploader"""
        self.headless = headless
        self.cookies_dir = os.path.join("data", "cookies")
        os.makedirs(self.cookies_dir, exist_ok=True)
        self.current_sb_instance = None
        
    def login_to_facebook(self, email, password, save_cookies=True):
        """
        Login to Facebook with credentials
        
        Args:
            email (str): Facebook email
            password (str): Facebook password
            save_cookies (bool): Whether to save cookies after login
            
        Returns:
            tuple: (success, sb_instance, message)
        """
        try:
            print("Facebook'a giriş yapılıyor...")
            
            # Initialize browser with CDP mode
            sb = SB(uc=True, headless=self.headless, test=True, locale="tr", ad_block=True)
            sb.open("about:blank")
            sb.activate_cdp_mode("https://www.facebook.com/")
            
            # Wait for page to load
            time.sleep(3)
            
            # Check if already logged in by trying to load existing cookies
            if self._try_load_existing_cookies(sb):
                if self._check_login_success(sb):
                    print("✅ Mevcut çerezlerle giriş başarılı!")
                    return True, sb, "Mevcut çerezlerle giriş yapıldı"
            
            # If not logged in, proceed with manual login
            print("Manuel giriş yapılıyor...")
            
            # Find email input field
            email_selectors = [
                'input[name="email"]',
                'input[data-testid="royal-email"]',
                'input#email',
                'input[type="email"]'
            ]
            
            email_found = False
            for selector in email_selectors:
                try:
                    if sb.cdp.is_element_visible(selector):
                        sb.cdp.click(selector)
                        sb.cdp.type(selector, email)
                        email_found = True
                        print(f"✅ Email alanı bulundu: {selector}")
                        break
                except:
                    continue
                    
            if not email_found:
                return False, None, "Email alanı bulunamadı!"
            
            # Find password input field
            password_selectors = [
                'input[name="pass"]',
                'input[data-testid="royal-pass"]',
                'input#pass',
                'input[type="password"]'
            ]
            
            password_found = False
            for selector in password_selectors:
                try:
                    if sb.cdp.is_element_visible(selector):
                        sb.cdp.click(selector)
                        sb.cdp.type(selector, password)
                        password_found = True
                        print(f"✅ Şifre alanı bulundu: {selector}")
                        break
                except:
                    continue
                    
            if not password_found:
                return False, None, "Şifre alanı bulunamadı!"
            
            # Find and click login button
            login_selectors = [
                'button[name="login"]',
                'button[data-testid="royal-login-button"]',
                'button[type="submit"]',
                'input[type="submit"][value*="Giriş"]'
            ]
            
            login_clicked = False
            for selector in login_selectors:
                try:
                    if sb.cdp.is_element_visible(selector):
                        sb.cdp.click(selector)
                        login_clicked = True
                        print(f"✅ Giriş butonuna basıldı: {selector}")
                        break
                except:
                    continue
                    
            if not login_clicked:
                return False, None, "Giriş butonu bulunamadı!"
            
            # Wait for login to complete
            print("Giriş işlemi bekleniyor...")
            time.sleep(5)
            
            # Check login success
            if self._check_login_success(sb):
                print("✅ Facebook girişi başarılı!")
                
                if save_cookies:
                    cookie_file = self._save_cookies(sb, email)
                    if cookie_file:
                        print(f"✅ Çerezler kaydedildi: {cookie_file}")
                
                return True, sb, "Facebook girişi başarılı"
            else:
                return False, None, "Giriş başarısız - kimlik bilgilerini kontrol edin"
                
        except Exception as e:
            print(f"Facebook giriş hatası: {str(e)}")
            return False, None, f"Giriş hatası: {str(e)}"
            
    def upload_video_to_facebook(self, sb_instance, video_path, description="", hashtags=None):
        """
        Upload video to Facebook
        
        Args:
            sb_instance: SeleniumBase instance
            video_path (str): Path to video file
            description (str): Video description
            hashtags (list): List of hashtags
            
        Returns:
            tuple: (success, message)
        """
        try:
            if not os.path.exists(video_path):
                return False, f"Video dosyası bulunamadı: {video_path}"
                
            print("Facebook'a video yükleniyor...")
            
            # Go to Facebook home page
            sb_instance.cdp.get("https://www.facebook.com/")
            time.sleep(3)
            
            # Look for "What's on your mind?" or post creation area
            post_selectors = [
                'span:contains("Aklından geçenleri paylaş")',
                'span:contains("What\'s on your mind")',
                'div[role="textbox"][aria-placeholder*="paylaş"]',
                'div[contenteditable="true"][role="textbox"]',
                'div[data-testid="status-attachment-mentions-input"]'
            ]
            
            post_area_found = False
            for selector in post_selectors:
                try:
                    if sb_instance.cdp.is_element_visible(selector):
                        sb_instance.cdp.click(selector)
                        post_area_found = True
                        print(f"✅ Paylaşım alanı bulundu: {selector}")
                        break
                except:
                    continue
                    
            if not post_area_found:
                return False, "Paylaşım alanı bulunamadı!"
            
            # Wait for post dialog to open
            time.sleep(2)
            
            # Look for photo/video upload button
            upload_selectors = [
                'div[aria-label*="Fotoğraf"]',
                'div[aria-label*="Video"]',
                'div[data-testid="media-sprout"]',
                'input[type="file"][accept*="video"]',
                'div:contains("Fotoğraf/video ekle")'
            ]
            
            upload_found = False
            for selector in upload_selectors:
                try:
                    if sb_instance.cdp.is_element_visible(selector):
                        sb_instance.cdp.click(selector)
                        upload_found = True
                        print(f"✅ Yükleme butonu bulundu: {selector}")
                        break
                except:
                    continue
                    
            if not upload_found:
                return False, "Video yükleme butonu bulunamadı!"
            
            # Wait for file dialog
            time.sleep(2)
            
            # Use PyAutoGUI to handle file dialog
            try:
                import pyautogui
                
                # Wait a bit for file dialog to appear
                time.sleep(1)
                
                # Type the file path
                pyautogui.write(video_path, interval=0.02)
                time.sleep(0.5)
                
                # Press Enter to select file
                pyautogui.press('enter')
                
                print(f"✅ Dosya seçildi: {video_path}")
                
            except Exception as e:
                print(f"Dosya seçme hatası: {str(e)}")
                return False, f"Dosya seçme hatası: {str(e)}"
            
            # Wait for video to upload
            print("Video yükleniyor, lütfen bekleyin...")
            time.sleep(10)  # Give time for video to upload
            
            # Add description if provided
            if description or hashtags:
                description_text = description
                if hashtags:
                    hashtag_text = " ".join([f"#{tag.strip('#')}" for tag in hashtags])
                    description_text = f"{description}\n\n{hashtag_text}"
                
                # Find description text area
                desc_selectors = [
                    'div[contenteditable="true"][role="textbox"]',
                    'div[data-testid="status-attachment-mentions-input"]',
                    'div[aria-label*="açıklama"]'
                ]
                
                for selector in desc_selectors:
                    try:
                        if sb_instance.cdp.is_element_visible(selector):
                            sb_instance.cdp.click(selector)
                            sb_instance.cdp.type(selector, description_text)
                            print("✅ Açıklama eklendi")
                            break
                    except:
                        continue
            
            # Wait a bit more for processing
            time.sleep(3)
            
            # Find and click publish button
            publish_selectors = [
                'div[aria-label="Paylaş"][role="button"]',
                'div:contains("Paylaş")[role="button"]',
                'button:contains("Paylaş")',
                'div[data-testid="react-composer-post-button"]'
            ]
            
            publish_clicked = False
            for selector in publish_selectors:
                try:
                    if sb_instance.cdp.is_element_visible(selector):
                        sb_instance.cdp.click(selector)
                        publish_clicked = True
                        print(f"✅ Paylaş butonuna basıldı: {selector}")
                        break
                except:
                    continue
                    
            if not publish_clicked:
                return False, "Paylaş butonu bulunamadı!"
            
            # Wait for post to be published
            time.sleep(5)
            
            print("✅ Video Facebook'a başarıyla yüklendi!")
            return True, "Video başarıyla yüklendi"
            
        except Exception as e:
            print(f"Video yükleme hatası: {str(e)}")
            return False, f"Video yükleme hatası: {str(e)}"
            
    def _check_login_success(self, sb_instance):
        """Check if login was successful"""
        try:
            current_url = sb_instance.cdp.get_current_url()
            page_title = sb_instance.cdp.get_title()
            
            # Check if we're on login page
            login_indicators = ['giriş', 'login', 'kaydol', 'sign up']
            if any(indicator in page_title.lower() for indicator in login_indicators):
                return False
            
            # Check for home page elements
            home_elements = [
                '[data-testid="newsfeed"]',
                '[data-testid="left_nav_menu_list"]',
                'div[data-pagelet="LeftRail"]',
                'div[role="main"]'
            ]
            
            for selector in home_elements:
                try:
                    if sb_instance.cdp.is_element_visible(selector):
                        return True
                except:
                    continue
            
            # Check URL patterns
            if 'facebook.com' in current_url and 'login' not in current_url:
                return True
                
            return False
            
        except Exception as e:
            print(f"Giriş kontrol hatası: {str(e)}")
            return False
            
    def _save_cookies(self, sb_instance, user_identifier):
        """Save cookies to file"""
        try:
            cookies = sb_instance.cdp.get_all_cookies()
            timestamp = int(time.time())
            
            # Create safe filename
            safe_identifier = "".join(c for c in user_identifier if c.isalnum() or c in "._-")
            filename = f"facebook_cookies_{safe_identifier}_{timestamp}.json"
            filepath = os.path.join(self.cookies_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False, default=str)
            
            return filepath
            
        except Exception as e:
            print(f"Çerez kaydetme hatası: {str(e)}")
            return None
            
    def _try_load_existing_cookies(self, sb_instance):
        """Try to load existing cookies"""
        try:
            # Find the most recent cookie file
            cookie_files = []
            if os.path.exists(self.cookies_dir):
                for filename in os.listdir(self.cookies_dir):
                    if filename.startswith("facebook_cookies_") and filename.endswith(".json"):
                        filepath = os.path.join(self.cookies_dir, filename)
                        mtime = os.path.getmtime(filepath)
                        cookie_files.append((mtime, filepath))
            
            if not cookie_files:
                return False
                
            # Sort by modification time (newest first)
            cookie_files.sort(reverse=True)
            latest_cookie_file = cookie_files[0][1]
            
            print(f"Mevcut çerezler yükleniyor: {latest_cookie_file}")
            
            with open(latest_cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            # Load cookies
            current_time = time.time()
            valid_cookies = []
            
            for cookie in cookies:
                if isinstance(cookie, dict):
                    # Check if cookie is still valid
                    expires = cookie.get('expires', 0)
                    if expires == 0 or expires > current_time:
                        if 'facebook.com' in cookie.get('domain', ''):
                            valid_cookies.append(cookie)
            
            if valid_cookies:
                sb_instance.cdp.set_all_cookies(valid_cookies)
                print(f"✅ {len(valid_cookies)} geçerli çerez yüklendi")
                return True
            
            return False
            
        except Exception as e:
            print(f"Çerez yükleme hatası: {str(e)}")
            return False
            
    def get_facebook_pages(self, sb_instance):
        """
        Get list of Facebook pages/accounts user can post to
        
        Args:
            sb_instance: SeleniumBase instance (must be logged in)
            
        Returns:
            list: List of pages with their info
        """
        try:
            print("Facebook sayfaları alınıyor...")
            
            # Go to Facebook pages management URL
            pages_url = "https://www.facebook.com/pages/?category=your_pages&ref=bookmarks"
            sb_instance.cdp.get(pages_url)
            time.sleep(5)
            
            print("Sayfalar yükleniyor...")
            
            # Wait for pages to load
            time.sleep(3)
            
            pages = []
            
            # Ana profil her zaman mevcut
            pages.append({
                'name': 'Ana Profil',
                'id': 'main_profile',
                'url': 'https://www.facebook.com/me',
                'type': 'profile'
            })
            
            # Facebook sayfalarını bul
            try:
                # Sayfa container'larını bul
                page_containers = sb_instance.cdp.evaluate('''
                    (function() {
                        const results = [];
                        
                        // Sayfa container'larını bul
                        const containers = document.querySelectorAll('div.x9f619.x1ja2u2z.x78zum5.x1n2onr6.x1r8uery.x1iyjqo2.xs83m0k.xeuugli.x1nhvcw1.x1qjc9v5.xozqiw3.x1q0g3np.xyamay9.x1ws5yxj.xw01apr.x4cne27.xifccgj');
                        
                        for (const container of containers) {
                            try {
                                // Sayfa adını bul
                                const nameElement = container.querySelector('span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.xtoi2st.x3x7a5m.x1603h9y.x1u7k74.x1xlr1w8.xzsf02u');
                                
                                if (nameElement) {
                                    const pageName = nameElement.textContent.trim();
                                    
                                    // Sayfa linkini bul
                                    const linkElement = container.querySelector('a[href*="facebook.com/"]');
                                    let pageUrl = '';
                                    let pageId = '';
                                    
                                    if (linkElement) {
                                        pageUrl = linkElement.href;
                                        // URL'den sayfa ID'sini çıkar
                                        const urlMatch = pageUrl.match(/facebook\\.com\\/([^/?]+)/);
                                        if (urlMatch) {
                                            pageId = urlMatch[1];
                                        }
                                    }
                                    
                                    if (pageName && pageUrl) {
                                        results.push({
                                            name: pageName,
                                            id: pageId,
                                            url: pageUrl,
                                            type: 'page'
                                        });
                                    }
                                }
                            } catch (e) {
                                console.log('Sayfa parse hatası:', e);
                            }
                        }
                        
                        return results;
                    })();
                ''')
                
                if page_containers and len(page_containers) > 0:
                    pages.extend(page_containers)
                    print(f"✅ {len(page_containers)} Facebook sayfası bulundu")
                else:
                    print("⚠️ Hiç Facebook sayfası bulunamadı")
                    
            except Exception as e:
                print(f"Sayfa arama hatası: {str(e)}")
            
            print(f"Toplam {len(pages)} sayfa/profil bulundu")
            return pages
            
        except Exception as e:
            print(f"Sayfa listesi alma hatası: {str(e)}")
            return []
            
    def switch_to_page(self, sb_instance, page_info):
        """
        Switch to a specific Facebook page for posting
        
        Args:
            sb_instance: SeleniumBase instance
            page_info: Page information dict
            
        Returns:
            bool: True if successful
        """
        try:
            print(f"Sayfaya geçiliyor: {page_info['name']}")
            
            # TODO: Implement page switching logic
            # This will involve:
            # 1. Finding the page switcher
            # 2. Clicking on the desired page
            # 3. Verifying the switch was successful
            
            if page_info['type'] == 'profile':
                # Already on main profile, no need to switch
                return True
            
            # For actual pages, implement switching logic here
            return True
            
        except Exception as e:
            print(f"Sayfa değiştirme hatası: {str(e)}")
            return False
            
    def upload_reels_video(self, sb_instance, page_info, video_path, description="", hashtags=None, enhance_with_gemini=False):
        """
        Upload video as Facebook Reels to a specific page
        
        Args:
            sb_instance: SeleniumBase instance
            page_info: Page information dict
            video_path: Path to video file
            description: Video description
            hashtags: List of hashtags
            enhance_with_gemini: Whether to enhance content with Gemini
            
        Returns:
            tuple: (success, message)
        """
        try:
            if not os.path.exists(video_path):
                return False, f"Video dosyası bulunamadı: {video_path}"
                
            print(f"Facebook Reels video yükleniyor: {page_info['name']}")
            
            # 1. Sayfaya git
            if page_info['type'] != 'profile':
                print(f"Sayfaya geçiliyor: {page_info['name']}")
                sb_instance.cdp.get(page_info['url'])
                time.sleep(3)
                
                # "Gönderi oluştur" linkini bul ve tıkla
                create_post_selectors = [
                    'span.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft.x1j85h84:contains("Gönderi oluştur")',
                    'span:contains("Gönderi oluştur")',
                    'div:contains("Gönderi oluştur")'
                ]
                
                create_post_clicked = False
                for selector in create_post_selectors:
                    try:
                        if sb_instance.cdp.is_element_visible(selector):
                            sb_instance.cdp.click(selector)
                            create_post_clicked = True
                            print("✅ Gönderi oluştur tıklandı")
                            break
                    except:
                        continue
                
                if create_post_clicked:
                    time.sleep(2)
                    
                    # "Geçiş Yap" butonunu bul ve tıkla
                    switch_selectors = [
                        'span.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft:contains("Geçiş Yap")',
                        'span:contains("Geçiş Yap")'
                    ]
                    
                    for selector in switch_selectors:
                        try:
                            if sb_instance.cdp.is_element_visible(selector):
                                sb_instance.cdp.click(selector)
                                print("✅ Geçiş Yap tıklandı")
                                break
                        except:
                            continue
                    
                    # Geçiş işlemini bekle
                    time.sleep(7)
                    print("Sayfa geçişi bekleniyor...")
            
            # 2. Gönderi Oluştur popup'ını kapat (varsa)
            try:
                close_selectors = [
                    'div[aria-label="Kapat"]',
                    'div[aria-label="Close"]',
                    'i[style*="background-image: url(\\"https://static.xx.fbcdn.net/rsrc.php/v4/y-/r/9s_C2pDGDPC.png\\")"]'
                ]
                
                for selector in close_selectors:
                    try:
                        if sb_instance.cdp.is_element_visible(selector):
                            sb_instance.cdp.click(selector)
                            print("✅ Popup kapatıldı")
                            break
                    except:
                        continue
            except:
                pass
            
            # 3. Reels sekmesine git
            print("Reels sekmesine gidiliyor...")
            reels_selectors = [
                'span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.xudqn12.x3x7a5m.x1f6kntn.xvq8zen.x1s688f.xi81zsa:contains("Reels")',
                'span:contains("Reels")'
            ]
            
            reels_clicked = False
            for selector in reels_selectors:
                try:
                    if sb_instance.cdp.is_element_visible(selector):
                        sb_instance.cdp.click(selector)
                        reels_clicked = True
                        print("✅ Reels sekmesi tıklandı")
                        break
                except:
                    continue
            
            if not reels_clicked:
                return False, "Reels sekmesi bulunamadı!"
            
            time.sleep(3)
            
            # 4. "Reels Videosu Oluştur" butonuna tıkla
            print("Reels Videosu Oluştur butonuna tıklanıyor...")
            create_reels_selectors = [
                'span.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft:contains("Reels Videosu Oluştur")',
                'span:contains("Reels Videosu Oluştur")'
            ]
            
            create_reels_clicked = False
            for selector in create_reels_selectors:
                try:
                    if sb_instance.cdp.is_element_visible(selector):
                        sb_instance.cdp.click(selector)
                        create_reels_clicked = True
                        print("✅ Reels Videosu Oluştur tıklandı")
                        break
                except:
                    continue
            
            if not create_reels_clicked:
                return False, "Reels Videosu Oluştur butonu bulunamadı!"
            
            time.sleep(8)
            
            # 5. "Video ekle" butonuna tıkla
            print("Video ekle butonuna tıklanıyor...")
            add_video_selectors = [
                'span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.xudqn12.x676frb.x1jchvi3.x1lbecb7.x1s688f.xzsf02u.x2b8uid:contains("Video ekle")',
                'span:contains("Video ekle")'
            ]
            
            add_video_clicked = False
            for selector in add_video_selectors:
                try:
                    if sb_instance.cdp.is_element_visible(selector):
                        sb_instance.cdp.click(selector)
                        add_video_clicked = True
                        print("✅ Video ekle tıklandı")
                        break
                except:
                    continue
            
            if not add_video_clicked:
                return False, "Video ekle butonu bulunamadı!"
            
            # 6. Dosya seçimi için PyAutoGUI kullan
            print(f"Video dosyası seçiliyor: {video_path}")
            time.sleep(2)
            
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
                time.sleep(2)
                
                print("✅ Video dosyası seçildi")
                
            except Exception as e:
                print(f"Dosya seçme hatası: {str(e)}")
                return False, f"Dosya seçme hatası: {str(e)}"
            
            # Video yüklenmesini bekle
            time.sleep(10)
            
            # 7. İleri butonuna tıkla
            print("İleri butonuna tıklanıyor...")
            next_selectors = [
                'span.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft.x1j85h84:contains("İleri")',
                'span:contains("İleri")'
            ]
            
            next_clicked = False
            for selector in next_selectors:
                try:
                    if sb_instance.cdp.is_element_visible(selector):
                        sb_instance.cdp.click(selector)
                        next_clicked = True
                        print("✅ İleri butonu tıklandı")
                        break
                except:
                    continue
            
            if not next_clicked:
                return False, "İleri butonu bulunamadı!"
            
            time.sleep(5)
            
            # 8. Açıklama ve hashtag'leri ekle
            print("Açıklama ve hashtag'ler ekleniyor...")
            
            # Gemini ile içerik zenginleştirme (isteğe bağlı)
            final_description = description
            if enhance_with_gemini and description:
                try:
                    # TODO: Gemini API entegrasyonu
                    print("⚠️ Gemini entegrasyonu henüz implement edilmedi")
                    # enhanced_description = self._enhance_with_gemini(description, hashtags)
                    # if enhanced_description:
                    #     final_description = enhanced_description
                except Exception as e:
                    print(f"Gemini zenginleştirme hatası: {str(e)}")
            
            # Hashtag'leri açıklamaya ekle
            if hashtags:
                hashtag_text = " ".join([f"#{tag.strip('#')}" for tag in hashtags])
                final_description = f"{final_description}\n\n{hashtag_text}"
            
            # Açıklama alanını bul ve doldur
            description_selectors = [
                'div.xzsf02u.x1a2a7pz.x1n2onr6.x14wi4xw.x9f619.x1lliihq.x5yr21d.xh8yej3.notranslate[contenteditable="true"][role="textbox"]',
                'div[contenteditable="true"][role="textbox"][aria-placeholder*="açıkla"]'
            ]
            
            description_added = False
            for selector in description_selectors:
                try:
                    if sb_instance.cdp.is_element_visible(selector):
                        sb_instance.cdp.click(selector)
                        sb_instance.cdp.type(selector, final_description)
                        description_added = True
                        print("✅ Açıklama eklendi")
                        break
                except:
                    continue
            
            if not description_added:
                print("⚠️ Açıklama alanı bulunamadı")
            
            time.sleep(3)
            
            # 9. İkinci İleri butonuna tıkla
            print("İkinci İleri butonuna tıklanıyor...")
            for selector in next_selectors:
                try:
                    if sb_instance.cdp.is_element_visible(selector):
                        sb_instance.cdp.click(selector)
                        print("✅ İkinci İleri butonu tıklandı")
                        break
                except:
                    continue
            
            time.sleep(5)
            
            # 10. Paylaş butonuna tıkla
            print("Paylaş butonuna tıklanıyor...")
            share_selectors = [
                'span.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft:contains("Paylaş")',
                'span:contains("Paylaş")'
            ]
            
            share_clicked = False
            for selector in share_selectors:
                try:
                    if sb_instance.cdp.is_element_visible(selector):
                        sb_instance.cdp.click(selector)
                        share_clicked = True
                        print("✅ Paylaş butonu tıklandı")
                        break
                except:
                    continue
            
            if not share_clicked:
                return False, "Paylaş butonu bulunamadı!"
            
            # Paylaşım işleminin tamamlanmasını bekle
            time.sleep(8)
            
            print("✅ Facebook Reels video başarıyla yüklendi!")
            return True, "Facebook Reels video başarıyla yüklendi!"
            
        except Exception as e:
            print(f"Reels video yükleme hatası: {str(e)}")
            return False, f"Reels video yükleme hatası: {str(e)}"
            
    def close_browser(self, sb_instance):
        """Close browser instance"""
        try:
            if sb_instance:
                sb_instance.quit()
        except:
            pass


def test_facebook_uploader():
    """Test function for Facebook uploader"""
    uploader = FacebookUploader(headless=False)
    
    # Test credentials (use your own)
    email = input("Facebook email: ")
    password = input("Facebook password: ")
    
    # Test login
    success, sb, message = uploader.login_to_facebook(email, password)
    
    if success:
        print(f"✅ Giriş başarılı: {message}")
        
        # Test video upload (optional)
        video_path = input("Video dosya yolu (boş bırakabilirsiniz): ").strip()
        if video_path and os.path.exists(video_path):
            upload_success, upload_message = uploader.upload_video_to_facebook(
                sb, video_path, "Test video yüklemesi", ["test", "seleniumbase"]
            )
            print(f"Video yükleme: {upload_message}")
        
        # Keep browser open for testing
        input("Tarayıcıyı kapatmak için Enter'a basın...")
        uploader.close_browser(sb)
    else:
        print(f"❌ Giriş başarısız: {message}")


if __name__ == "__main__":
    test_facebook_uploader()