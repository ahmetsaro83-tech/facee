#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook Login GUI with SeleniumBase CDP Mode
PyQt5 arayüzlü Facebook giriş sistemi - Cookie desteği ile
"""

import sys
import os
import json
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLineEdit, QLabel, QTextEdit, 
                            QFileDialog, QMessageBox, QTabWidget, QGroupBox,
                            QProgressBar, QCheckBox, QListWidget, QListWidgetItem, 
                            QSplitter, QAbstractItemView, QSpinBox, QFrame)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QIcon
from seleniumbase import SB
import random

class GroupSharingThread(QThread):
    """Grup paylaşım işlemlerini arka planda çalıştıran thread"""
    
    # Sinyaller
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, sb_instance, selected_groups, sharing_text, image_path=None, delay_seconds=30):
        super().__init__()
        self.sb = sb_instance
        self.selected_groups = selected_groups
        self.sharing_text = sharing_text
        self.image_path = image_path
        self.delay_seconds = delay_seconds
    
    def check_browser_alive(self):
        """Tarayıcının hala çalışıp çalışmadığını kontrol et"""
        try:
            # 1. Önce SeleniumBase instance'ının varlığını kontrol et
            if not hasattr(self, 'sb') or not self.sb:
                self.log_signal.emit("❌ SeleniumBase instance bulunamadı")
                return False
            
            # 2. CDP bağlantısını kontrol et
            if not hasattr(self.sb, 'cdp') or not self.sb.cdp:
                self.log_signal.emit("❌ CDP bağlantısı bulunamadı")
                return False
            
            # 3. Mevcut URL'yi alma denemesi yap (timeout ile)
            try:
                current_url = self.sb.cdp.get_current_url()
                
                # URL boşsa veya geçersizse tarayıcı kapanmış olabilir
                if not current_url or current_url == "data:," or current_url == "about:blank":
                    self.log_signal.emit(f"❌ Geçersiz URL tespit edildi: {current_url}")
                    return False
                
                # 4. Basit bir JavaScript komutu çalıştırarak tarayıcının yanıt verip vermediğini test et
                try:
                    test_result = self.sb.cdp.evaluate("return 'browser_alive';")
                    if test_result != 'browser_alive':
                        self.log_signal.emit("❌ JavaScript test başarısız")
                        return False
                except Exception as js_error:
                    self.log_signal.emit(f"❌ JavaScript test hatası: {str(js_error)}")
                    return False
                
                # 5. Sayfa başlığını kontrol et (ek güvenlik)
                try:
                    page_title = self.sb.cdp.get_title()
                    if not page_title:
                        self.log_signal.emit("⚠️ Sayfa başlığı boş")
                        # Başlık boş olsa bile tarayıcı çalışıyor olabilir, False döndürme
                except Exception as title_error:
                    self.log_signal.emit(f"⚠️ Başlık kontrolü hatası: {str(title_error)}")
                    # Başlık hatası kritik değil, devam et
                
                return True
                
            except Exception as url_error:
                error_str = str(url_error).lower()
                self.log_signal.emit(f"❌ URL alma hatası: {str(url_error)}")
                
                # Tarayıcı kapanma ile ilgili hata mesajları
                browser_closed_errors = [
                    "no such window",
                    "target window already closed", 
                    "connection refused",
                    "connection reset",
                    "chrome not reachable",
                    "session deleted",
                    "invalid session id",
                    "chrome driver stopped",
                    "browser closed",
                    "websocket",
                    "disconnected",
                    "timeout"
                ]
                
                for error_keyword in browser_closed_errors:
                    if error_keyword in error_str:
                        self.log_signal.emit(f"🔴 Tarayıcı kapanma hatası tespit edildi: {error_keyword}")
                        return False
                
                # Bilinmeyen URL hatası da kritik olabilir
                return False
                
        except Exception as e:
            error_str = str(e).lower()
            self.log_signal.emit(f"❌ Tarayıcı kontrol genel hatası: {str(e)}")
            
            # Genel tarayıcı kapanma hataları
            critical_errors = [
                "no such window",
                "target window already closed", 
                "connection",
                "chrome not reachable",
                "session deleted",
                "invalid session id",
                "chrome driver stopped",
                "browser closed",
                "websocket",
                "disconnected"
            ]
            
            for error_keyword in critical_errors:
                if error_keyword in error_str:
                    self.log_signal.emit(f"🔴 Kritik tarayıcı hatası: {error_keyword}")
                    return False
                    
            # Bilinmeyen hata, güvenli olmak için False döndür
            self.log_signal.emit("❌ Bilinmeyen hata - tarayıcı durumu belirsiz")
            return False
    
    def handle_browser_confirmation(self):
        """Paylaş butonuna bastıktan sonra çıkan tarayıcı onay penceresini işle"""
        try:
            self.log_signal.emit("🔍 Tarayıcı onay penceresi aranıyor...")
            
            # Sayfa içeriğini kontrol et - Paylaşım başarılı mesajı var mı?
            try:
                page_source = self.sb.get_page_source()
                success_indicators = [
                    "paylaşıldı", "shared", "success", "başarılı",
                    "paylaşım tamamlandı", "gönderi paylaşıldı", "paylaşıldı",
                    "gönderildi", "posted", "published"
                ]
                
                for indicator in success_indicators:
                    if indicator.lower() in page_source.lower():
                        self.log_signal.emit(f"✅ Paylaşım başarı göstergesi bulundu: '{indicator}'")
                        return True
            except Exception as source_error:
                self.log_signal.emit(f"⚠️ Sayfa içeriği kontrolü hatası: {str(source_error)}")
            
            # 1. Yöntem: JavaScript alert/confirm penceresini işle
            try:
                # JavaScript alert varsa kabul et
                alert_text = self.sb.cdp.evaluate("return window.alert ? 'alert_exists' : 'no_alert'")
                if alert_text == 'alert_exists':
                    self.log_signal.emit("✅ JavaScript alert bulundu, kabul ediliyor...")
                    self.sb.cdp.evaluate("window.alert = function() { return true; }")
                    self.sb.sleep(0.5)  # Kısa bekleme
                    
                # JavaScript confirm varsa kabul et
                confirm_text = self.sb.cdp.evaluate("return window.confirm ? 'confirm_exists' : 'no_confirm'")
                if confirm_text == 'confirm_exists':
                    self.log_signal.emit("✅ JavaScript confirm bulundu, kabul ediliyor...")
                    self.sb.cdp.evaluate("window.confirm = function() { return true; }")
                    self.sb.sleep(0.5)  # Kısa bekleme
            except Exception as js_error:
                self.log_signal.emit(f"⚠️ JavaScript alert/confirm kontrolü hatası: {str(js_error)}")
            
            # 2. Yöntem: Tarayıcı onay butonlarını ara ve tıkla
            confirm_buttons = [
                'button:contains("Tamam")',
                'button:contains("OK")',
                'button:contains("Allow")',
                'button:contains("İzin Ver")',
                'button:contains("Paylaş")',
                'button:contains("Share")',
                'button[id*="confirm"]',
                'button[class*="confirm"]',
                'input[type="submit"][value*="Tamam"]',
                'input[type="submit"][value*="OK"]',
                'div[role="button"]:contains("Tamam")',
                'div[role="button"]:contains("OK")',
                'div[role="button"]:contains("Paylaş")',
                'div[role="button"]:contains("Share")',
                'div[aria-label="Paylaş"][role="button"]',
                'div[aria-label="Share"][role="button"]',
                'div[aria-label*="Paylaş"]',
                'div[aria-label*="Share"]',
                'span:contains("Paylaş")',
                'span:contains("Share")',
                'a[role="button"]:contains("Paylaş")',
                'a[role="button"]:contains("Share")'
            ]
            
            # Önce bilinen seçicileri dene
            for selector in confirm_buttons:
                try:
                    if self.sb.is_element_present(selector) and self.sb.is_element_visible(selector):
                        self.log_signal.emit(f"✅ Onay butonu bulundu: {selector}")
                        self.sb.click(selector)
                        self.sb.sleep(1)  # Tıklama sonrası kısa bekleme
                        return True
                except Exception as button_error:
                    continue
            
            # Tüm onay butonlarını bul ve bilgilerini al
            try:
                all_buttons = self.sb.cdp.evaluate('''
                    (function() {
                        const results = [];
                        const selectors = [
                            'button', 'div[role="button"]', 'a[role="button"]',
                            'input[type="submit"]', 'input[type="button"]', 'span[role="button"]'
                        ];
                        
                        // Tüm potansiyel butonları bul
                        const elements = [];
                        for (const selector of selectors) {
                            elements.push(...document.querySelectorAll(selector));
                        }
                        
                        // Butonları filtrele ve bilgilerini al
                        for (const el of elements) {
                            const text = el.innerText || el.textContent || '';
                            const value = el.value || '';
                            const ariaLabel = el.getAttribute('aria-label') || '';
                            const id = el.id || '';
                            const className = el.className || '';
                            
                            // Onay butonu olabilecek kelimeleri içeriyor mu?
                            const keywords = ['tamam', 'ok', 'allow', 'izin ver', 'paylaş', 'share', 'confirm', 'yes', 'evet', 'gönder', 'post'];
                            const hasKeyword = keywords.some(keyword => 
                                text.toLowerCase().includes(keyword) || 
                                value.toLowerCase().includes(keyword) || 
                                ariaLabel.toLowerCase().includes(keyword) || 
                                id.toLowerCase().includes(keyword) || 
                                className.toLowerCase().includes(keyword)
                            );
                            
                            if (hasKeyword) {
                                // Butonu tıkla
                                try {
                                    el.click();
                                    return { clicked: true, element: {
                                        tag: el.tagName,
                                        text: text,
                                        value: value,
                                        ariaLabel: ariaLabel
                                    }};
                                } catch (e) {
                                    // Tıklama başarısız olursa devam et
                                }
                                
                                results.push({
                                    tag: el.tagName,
                                    text: text,
                                    value: value,
                                    ariaLabel: ariaLabel,
                                    id: id,
                                    className: className,
                                    position: {
                                        x: el.getBoundingClientRect().left,
                                        y: el.getBoundingClientRect().top
                                    },
                                    size: {
                                        width: el.offsetWidth,
                                        height: el.offsetHeight
                                    },
                                    isVisible: el.offsetWidth > 0 && el.offsetHeight > 0 && 
                                              window.getComputedStyle(el).visibility !== 'hidden' && 
                                              window.getComputedStyle(el).display !== 'none'
                                });
                            }
                        }
                        return { clicked: false, elements: results };
                    })();
                ''')
                
                # JavaScript ile bulunan butonları kontrol et
                if all_buttons and isinstance(all_buttons, dict):
                    if all_buttons.get('clicked', False):
                        self.log_signal.emit(f"✅ JavaScript ile onay butonu tıklandı: {all_buttons.get('element', {})}")
                        self.sb.sleep(1)  # Tıklama sonrası kısa bekleme
                        return True
                    
                    # Görünür butonları tıklamayı dene
                    visible_buttons = [btn for btn in all_buttons.get('elements', []) if btn.get('isVisible', False)]
                    if visible_buttons:
                        for btn in visible_buttons:
                            try:
                                x = btn['position']['x'] + (btn['size']['width'] / 2)
                                y = btn['position']['y'] + (btn['size']['height'] / 2)
                                
                                # Koordinat ile tıkla
                                self.sb.cdp.evaluate(f'''
                                    (function() {{
                                        const evt = new MouseEvent('click', {{
                                            bubbles: true,
                                            cancelable: true,
                                            view: window,
                                            clientX: {x},
                                            clientY: {y}
                                        }});
                                        document.elementFromPoint({x}, {y}).dispatchEvent(evt);
                                    }})();
                                ''')
                                self.log_signal.emit(f"✅ Onay butonu koordinat ile tıklandı: {btn['text'] or btn['ariaLabel']}")
                                self.sb.sleep(1)  # Tıklama sonrası kısa bekleme
                                return True
                            except Exception as coord_error:
                                continue
                
                if all_buttons and len(all_buttons) > 0:
                    self.log_signal.emit(f"🔍 {len(all_buttons)} potansiyel onay butonu bulundu")
                    for btn in all_buttons:
                        self.log_signal.emit(f"🔍 Buton: {btn}")
            except Exception as btn_scan_error:
                self.log_signal.emit(f"⚠️ Buton tarama hatası: {str(btn_scan_error)}")
            
            button_clicked = False
            for selector in confirm_buttons:
                try:
                    if self.sb.is_element_present(selector) and self.sb.is_element_visible(selector):
                        self.log_signal.emit(f"✅ Onay butonu bulundu: {selector}")
                        self.sb.click(selector)
                        self.sb.sleep(1)  # Tıklama sonrası kısa bekleme
                        button_clicked = True
                        self.log_signal.emit("✅ Onay butonuna tıklandı")
                        break
                except Exception as btn_error:
                    continue
            
            # JavaScript ile tüm görünür onay butonlarına tıklamayı dene
            if not button_clicked:
                try:
                    clicked = self.sb.cdp.evaluate('''
                        (function() {
                            const keywords = ['tamam', 'ok', 'allow', 'izin ver', 'paylaş', 'share', 'confirm', 'yes', 'evet'];
                            const selectors = [
                                'button', 'div[role="button"]', 'a[role="button"]',
                                'input[type="submit"]', 'input[type="button"]'
                            ];
                            
                            // Tüm potansiyel butonları bul
                            const elements = [];
                            for (const selector of selectors) {
                                elements.push(...document.querySelectorAll(selector));
                            }
                            
                            // Görünür ve anahtar kelime içeren ilk butonu tıkla
                            for (const el of elements) {
                                const text = el.innerText || el.textContent || '';
                                const value = el.value || '';
                                const ariaLabel = el.getAttribute('aria-label') || '';
                                const id = el.id || '';
                                const className = el.className || '';
                                
                                const hasKeyword = keywords.some(keyword => 
                                    text.toLowerCase().includes(keyword) || 
                                    value.toLowerCase().includes(keyword) || 
                                    ariaLabel.toLowerCase().includes(keyword) || 
                                    id.toLowerCase().includes(keyword) || 
                                    className.toLowerCase().includes(keyword)
                                );
                                
                                const isVisible = el.offsetWidth > 0 && el.offsetHeight > 0 && 
                                                window.getComputedStyle(el).visibility !== 'hidden' && 
                                                window.getComputedStyle(el).display !== 'none';
                                
                                if (hasKeyword && isVisible) {
                                    el.click();
                                    return { clicked: true, element: { tag: el.tagName, text: text } };
                                }
                            }
                            return { clicked: false };
                        })();
                    ''')
                    
                    if clicked and clicked.get('clicked', False):
                        button_clicked = True
                        self.log_signal.emit(f"✅ JavaScript ile onay butonuna tıklandı: {clicked.get('element', {})}")
                except Exception as js_click_error:
                    self.log_signal.emit(f"⚠️ JavaScript buton tıklama hatası: {str(js_click_error)}")
            
            # 3. Yöntem: Klavye ile Enter tuşuna bas
            if not button_clicked:
                self.log_signal.emit("🔄 Onay butonu bulunamadı, Enter tuşu deneniyor...")
                try:
                    import pyautogui
                    pyautogui.press('enter')
                    self.sb.sleep(1)  # Tuşa bastıktan sonra kısa bekleme
                    self.log_signal.emit("✅ Enter tuşuna basıldı")
                    button_clicked = True
                except Exception as key_error:
                    self.log_signal.emit(f"⚠️ Enter tuşu hatası: {str(key_error)}")
            
            # 4. Yöntem: Escape tuşu ile iptal et (son çare)
            if not button_clicked:
                self.log_signal.emit("🔄 Escape tuşu ile iptal deneniyor...")
                try:
                    import pyautogui
                    pyautogui.press('escape')
                    self.log_signal.emit("✅ Escape tuşuna basıldı (iptal)")
                except Exception as esc_error:
                    self.log_signal.emit(f"⚠️ Escape tuşu hatası: {str(esc_error)}")
            
            # Onay işleminin tamamlanmasını bekle
            self.sb.sleep(random.uniform(1, 2))
            self.log_signal.emit("✅ Tarayıcı onay işlemi tamamlandı")
            
        except Exception as e:
            self.log_signal.emit(f"❌ Tarayıcı onay işleme hatası: {str(e)}")
            # Hata olsa bile devam et
            pass
    
    def run(self):
        """Ana paylaşım işlemi"""
        try:
            self.log_signal.emit("🚀 Grup paylaşımı başlatılıyor...")
            
            successful_shares = 0
            failed_shares = 0
            
            for i, group in enumerate(self.selected_groups):
                try:
                    self.status_signal.emit(f"Grup {i+1}/{len(self.selected_groups)}: {group['name']}")
                    self.log_signal.emit(f"📍 Grup {i+1}: {group['name']} - {group['url']}")
                    
                    # Gruba git
                    self.log_signal.emit(f"🌐 Gruba gidiliyor: {group['url']}")
                    try:
                        self.sb.cdp.get(group['url'])
                        self.sb.sleep(random.uniform(3, 5))
                        # Sayfa yüklendikten sonra tarayıcı durumunu kontrol et
                        if not self.check_browser_alive():
                            self.log_signal.emit("⚠️ Tarayıcı bağlantısı zayıf, yeniden bağlanmaya çalışılıyor...")
                            self.sb.sleep(3)
                    except Exception as e:
                        self.log_signal.emit(f"⚠️ Gruba gitme hatası: {str(e)}, devam ediliyor...")
                    
                    # Paylaşım alanını bul ve tıkla
                    self.log_signal.emit("🔍 Paylaşım alanı aranıyor...")
                    
                    # Farklı seçicileri dene
                    post_selectors = [
                        'span:contains("Bir şeyler yaz...")',
                        'div[role="textbox"][aria-placeholder*="gönderi"]',
                        'div[contenteditable="true"][role="textbox"]',
                        'div[data-lexical-editor="true"]'
                    ]
                    
                    post_area_found = False
                    for selector in post_selectors:
                        try:
                            if self.sb.cdp.is_element_visible(selector):
                                self.log_signal.emit(f"✅ Paylaşım alanı bulundu: {selector}")
                                self.sb.cdp.click(selector)
                                post_area_found = True
                                break
                        except:
                            continue
                    
                    if not post_area_found:
                        self.log_signal.emit("❌ Paylaşım alanı bulunamadı, alternatif yöntem deneniyor...")
                        # JavaScript ile tıklamayı dene
                        try:
                            self.sb.cdp.evaluate("""
                                var elements = document.querySelectorAll('span');
                                for (var i = 0; i < elements.length; i++) {
                                    if (elements[i].textContent.includes('Bir şeyler yaz') || 
                                        elements[i].textContent.includes('gönderi oluştur')) {
                                        elements[i].click();
                                        break;
                                    }
                                }
                            """)
                            post_area_found = True
                            self.log_signal.emit("✅ JavaScript ile paylaşım alanı tıklandı")
                        except:
                            pass
                    
                    if not post_area_found:
                        self.log_signal.emit("❌ Paylaşım alanı bulunamadı, grup atlanıyor")
                        failed_shares += 1
                        continue
                    
                    # Paylaşım alanına tıklama sonrası tarayıcı kontrolü
                    if not self.check_browser_alive():
                        self.log_signal.emit("⚠️ Tarayıcı bağlantısı zayıf, devam ediliyor...")
                        self.sb.sleep(2)  # Kısa bekleme
                    
                    # Paylaşım alanının açılmasını bekle
                    self.sb.sleep(random.uniform(3, 5))
                    
                    # Paylaşım alanı açılma sonrası tekrar tarayıcı kontrolü
                    if not self.check_browser_alive():
                        self.log_signal.emit("⚠️ Tarayıcı bağlantısı zayıf, devam ediliyor...")
                        self.sb.sleep(2)  # Kısa bekleme
                    
                    # Önce "Gönderi Oluştur" penceresinde olduğundan emin ol
                    self.log_signal.emit("🔍 Gönderi Oluştur penceresi kontrol ediliyor...")
                    
                    try:
                        # "Gönderi Oluştur" başlığını ara
                        create_post_found = self.sb.cdp.evaluate("""
                            (function() {
                                var elements = document.querySelectorAll('span');
                                for (var i = 0; i < elements.length; i++) {
                                    if (elements[i].textContent.includes('Gönderi Oluştur')) {
                                        return true;
                                    }
                                }
                                return false;
                            })()
                        """)
                        
                        if create_post_found:
                            self.log_signal.emit("✅ Gönderi Oluştur penceresi bulundu")
                        else:
                            self.log_signal.emit("⚠️ Gönderi Oluştur penceresi bulunamadı, devam ediliyor...")
                    except:
                        self.log_signal.emit("⚠️ Pencere kontrolü yapılamadı, devam ediliyor...")
                    
                    # Tarayıcı bağlantısını kontrol et
                    try:
                        current_url = self.sb.cdp.get_current_url()
                        self.log_signal.emit(f"🔍 Tarayıcı kontrolü: {current_url[:50]}...")
                    except Exception as e:
                        self.log_signal.emit(f"⚠️ Tarayıcı bağlantısı hatası: {str(e)}, devam ediliyor...")
                        self.sb.sleep(2)  # Kısa bekleme
                    
                    # Metin kutusunu bul ve metni yaz
                    if self.sharing_text:
                        self.log_signal.emit("📝 Paylaşım metni yazılıyor...")
                        
                        # Önce tarayıcı kontrolü yap
                        if not self.check_browser_alive():
                            self.log_signal.emit("❌ Tarayıcı bağlantısı kayboldu - grup atlanıyor")
                            failed_shares += 1
                            continue
                        
                        # Spesifik metin kutusu seçicileri (belirtilen div)
                        specific_selectors = [
                            'div.xzsf02u.x1a2a7pz.x1n2onr6.x14wi4xw.x9f619.x1lliihq.x5yr21d.xh8yej3.notranslate[contenteditable="true"][role="textbox"]',
                            'div[contenteditable="true"][role="textbox"][aria-placeholder*="Bir şeyler yaz"]',
                            'div[data-lexical-editor="true"][contenteditable="true"]'
                        ]
                        
                        # Genel seçiciler (yedek)
                        general_selectors = [
                            'div[contenteditable="true"][role="textbox"]',
                            'div[data-lexical-editor="true"]',
                            'div[aria-placeholder*="gönderi"]',
                            'div[aria-placeholder*="yaz"]'
                        ]
                        
                        all_selectors = specific_selectors + general_selectors
                        
                        text_written = False
                        for selector in all_selectors:
                            try:
                                # Her adımda tarayıcı kontrolü yap
                                if not self.check_browser_alive():
                                    self.log_signal.emit("⚠️ Tarayıcı bağlantısı zayıf, devam ediliyor...")
                                    self.sb.sleep(1)  # Kısa bekleme
                                    text_written = False  # Başarısız olarak işaretle
                                    break
                                
                                if self.sb.cdp.is_element_visible(selector):
                                    self.log_signal.emit(f"✅ Metin kutusu bulundu: {selector}")
                                    
                                    # Güvenli şekilde kutuya tıkla
                                    try:
                                        self.sb.cdp.click(selector)
                                        self.sb.sleep(random.uniform(1, 2))  # Daha uzun bekleme
                                        
                                        # Tarayıcı hala çalışıyor mu kontrol et
                                        if not self.check_browser_alive():
                                            self.log_signal.emit("❌ Tarayıcı tıklama sonrası kapandı")
                                            failed_shares += 1
                                            break
                                        
                                        # Mevcut içeriği temizle (güvenli şekilde)
                                        try:
                                            self.sb.cdp.evaluate(f"""
                                                var element = document.querySelector('{selector}');
                                                if (element) {{
                                                    element.focus();
                                                    element.innerHTML = '';
                                                }}
                                            """)
                                            self.sb.sleep(0.5)
                                        except Exception as clear_error:
                                            self.log_signal.emit(f"⚠️ İçerik temizleme hatası: {str(clear_error)}")
                                        
                                        # Son kontrol
                                        if not self.check_browser_alive():
                                            self.log_signal.emit("❌ Tarayıcı temizleme sonrası kapandı")
                                            failed_shares += 1
                                            break
                                        
                                        # Metni yavaş yavaş yaz
                                        self.log_signal.emit("⌨️ Metin yavaşça yazılıyor...")
                                        self.sb.cdp.press_keys(selector, self.sharing_text)
                                        
                                        # Yazma sonrası kontrol
                                        if not self.check_browser_alive():
                                            self.log_signal.emit("❌ Tarayıcı metin yazma sonrası kapandı")
                                            failed_shares += 1
                                            break
                                        
                                        text_written = True
                                        self.log_signal.emit("✅ Metin başarıyla yazıldı")
                                        break
                                        
                                    except Exception as click_error:
                                        self.log_signal.emit(f"⚠️ Tıklama/yazma hatası: {str(click_error)}")
                                        # Tarayıcı kapanma kontrolü
                                        if "no such window" in str(click_error).lower() or "target window already closed" in str(click_error).lower():
                                            self.log_signal.emit("❌ Tarayıcı penceresi beklenmedik şekilde kapatıldı")
                                            failed_shares += 1
                                            break
                                        continue
                                        
                            except Exception as e:
                                self.log_signal.emit(f"⚠️ Genel metin yazma hatası: {selector} - {str(e)}")
                                # Tarayıcı bağlantısı kontrolü
                                if "no such window" in str(e).lower() or "target window already closed" in str(e).lower():
                                    self.log_signal.emit("❌ Tarayıcı penceresi kapatıldı")
                                    failed_shares += 1
                                    break
                                continue
                        
                        # Metin yazma sonrası tarayıcı kontrolü
                        if not self.check_browser_alive():
                            self.log_signal.emit("⚠️ Tarayıcı bağlantısı zayıf, devam ediliyor...")
                            self.sb.sleep(2)  # Kısa bekleme
                        
                        if not text_written:
                            # JavaScript ile daha kapsamlı metin yazma
                            self.log_signal.emit("🔄 JavaScript ile metin yazma deneniyor...")
                            try:
                                # Metni escape et (özel karakterler için)
                                escaped_text = self.sharing_text.replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
                                
                                js_code = f"""
                                (function() {{
                                    // Önce spesifik div'i bul
                                    var specificDiv = document.querySelector('div.xzsf02u.x1a2a7pz.x1n2onr6.x14wi4xw.x9f619.x1lliihq.x5yr21d.xh8yej3.notranslate[contenteditable="true"][role="textbox"]');
                                    
                                    if (specificDiv) {{
                                        specificDiv.focus();
                                        specificDiv.innerHTML = '<p>{escaped_text}</p>';
                                        return 'Spesifik div bulundu';
                                    }}
                                    
                                    // Alternatif: Tüm contenteditable div'leri kontrol et
                                    var textBoxes = document.querySelectorAll('div[contenteditable="true"]');
                                    for (var i = 0; i < textBoxes.length; i++) {{
                                        var element = textBoxes[i];
                                        var role = element.getAttribute('role');
                                        var placeholder = element.getAttribute('aria-placeholder') || '';
                                        
                                        if (role === 'textbox' || placeholder.includes('yaz') || placeholder.includes('gönderi')) {{
                                            element.focus();
                                            element.innerHTML = '<p>{escaped_text}</p>';
                                            return 'Alternatif div bulundu: ' + placeholder;
                                        }}
                                    }}
                                    
                                    return 'Hiç uygun div bulunamadı';
                                }})()
                                """
                                
                                result = self.sb.cdp.evaluate(js_code)
                                self.log_signal.emit(f"✅ JavaScript ile metin yazıldı: {result}")
                                text_written = True
                                
                                # JavaScript metin yazma sonrası browser kontrolü
                                if not self.check_browser_alive():
                                    self.log_signal.emit("❌ Tarayıcı bağlantısı JavaScript metin yazma sonrası koptu")
                                    failed_shares += 1
                                    continue
                                
                            except Exception as e:
                                self.log_signal.emit(f"❌ JavaScript metin yazma hatası: {str(e)}")
                                # Tarayıcı kapanma kontrolü
                                if "no such window" in str(e).lower() or "target window already closed" in str(e).lower():
                                    self.log_signal.emit("❌ Tarayıcı JavaScript metin yazma sırasında kapandı")
                                    failed_shares += 1
                                    continue
                        
                        if not text_written:
                            self.log_signal.emit("❌ Metin yazılamadı")
                    
                    # Resim ekleme
                    if self.image_path and os.path.exists(self.image_path):
                        self.log_signal.emit("🖼️ Resim ekleniyor...")
                        
                        # Resim ekleme öncesi browser kontrolü
                        if not self.check_browser_alive():
                            self.log_signal.emit("❌ Tarayıcı bağlantısı resim ekleme öncesi koptu")
                            failed_shares += 1
                            continue
                        
                        try:
                            # Resim ekleme butonunu bul ve tıkla
                            image_selectors = [
                                'img[src*="Ivw7nhRtXyo.png"]',  # Belirtilen resim ikonu
                                'div[aria-label*="Fotoğraf"]',
                                'div[aria-label*="Photo"]',
                                'svg[aria-label*="Fotoğraf"]',
                                'i[data-visualcompletion="css-img"]'
                            ]
                            
                            image_button_clicked = False
                            for selector in image_selectors:
                                try:
                                    if self.sb.cdp.is_element_visible(selector):
                                        self.log_signal.emit(f"✅ Resim butonu bulundu: {selector}")
                                        self.sb.cdp.click(selector)
                                        image_button_clicked = True
                                        break
                                except Exception as e:
                                    self.log_signal.emit(f"⚠️ Resim butonu tıklama hatası: {selector} - {str(e)}")
                                    continue
                            
                            if not image_button_clicked:
                                # JavaScript ile resim butonunu bul
                                self.log_signal.emit("🔍 JavaScript ile resim butonu aranıyor...")
                                try:
                                    self.sb.cdp.evaluate("""
                                        // Resim ekleme butonunu bul
                                        var imageButtons = document.querySelectorAll('img, div, svg, i');
                                        for (var i = 0; i < imageButtons.length; i++) {
                                            var element = imageButtons[i];
                                            var src = element.getAttribute('src') || '';
                                            var ariaLabel = element.getAttribute('aria-label') || '';
                                            
                                            if (src.includes('Ivw7nhRtXyo.png') || 
                                                ariaLabel.includes('Fotoğraf') || 
                                                ariaLabel.includes('Photo')) {
                                                element.click();
                                                break;
                                            }
                                        }
                                    """)
                                    image_button_clicked = True
                                    self.log_signal.emit("✅ JavaScript ile resim butonu tıklandı")
                                except Exception as e:
                                    self.log_signal.emit(f"❌ JavaScript resim butonu hatası: {str(e)}")
                            
                            if image_button_clicked:
                                # Resim butonu tıklandıktan sonra tarayıcı bağlantısını kontrol et
                                if not self.check_browser_alive():
                                    self.log_signal.emit("⚠️ Tarayıcı bağlantısı zayıf - resim butonu sonrası, devam ediliyor...")
                                    self.sb.sleep(2)  # Kısa bekleme
                                
                                # Windows Explorer'ın açılmasını bekle
                                self.log_signal.emit("⏳ Windows Explorer açılması bekleniyor...")
                                self.sb.sleep(3)
                                
                                # pyautogui işlemleri öncesi tarayıcı bağlantısını kontrol et
                                if not self.check_browser_alive():
                                    self.log_signal.emit("⚠️ Tarayıcı bağlantısı zayıf - Windows Explorer sırasında, devam ediliyor...")
                                    self.sb.sleep(2)  # Kısa bekleme
                                
                                # Windows Explorer'da dosya yolunu yaz ve Enter'a bas
                                self.log_signal.emit(f"📁 Dosya yolu yazılıyor: {self.image_path}")
                                
                                try:
                                    import pyautogui
                                    
                                    # Güvenlik için pyautogui ayarları
                                    pyautogui.FAILSAFE = True
                                    pyautogui.PAUSE = 0.3
                                    
                                    self.log_signal.emit("🖱️ Windows Explorer'da dosya seçimi başlatılıyor...")
                                    
                                    # Ana yöntem: Dosya adı alanına tam yol yazma
                                    self.log_signal.emit("📝 Dosya adı alanına tam yol yazılıyor...")
                                    
                                    # Dosya adı alanına odaklan (Alt+N)
                                    pyautogui.hotkey('alt', 'n')
                                    self.sb.sleep(0.8)
                                    
                                    # Mevcut metni tamamen temizle
                                    pyautogui.hotkey('ctrl', 'a')
                                    self.sb.sleep(0.5)
                                    pyautogui.press('delete')
                                    self.sb.sleep(0.5)
                                    pyautogui.press('backspace')
                                    self.sb.sleep(0.5)
                                    
                                    # Tam dosya yolunu yaz (Windows formatında backslash ile)
                                    windows_path = self.image_path.replace('/', '\\')
                                    self.log_signal.emit(f"📝 Yazılıyor: {windows_path}")
                                    
                                    # Çok yavaş yazma ile tarayıcı çökmesini önle
                                    self.sb.sleep(2)  # Yazma öncesi ek bekleme
                                    
                                    # Karakter karakter yaz (hızlandırılmış)
                                    try:
                                        for i, char in enumerate(windows_path):
                                            # Tarayıcı durumunu kontrol et
                                            if not self.check_browser_alive():
                                                self.log_signal.emit("❌ Tarayıcı çöktü, dosya yazma işlemi durduruluyor")
                                                return False
                                            
                                            pyautogui.write(char)
                                            self.sb.sleep(0.01)  # Her karakter sonrası kısa bekleme
                                            if i % 10 == 0:  # Her 10 karakterde bir kısa bekleme
                                                self.sb.sleep(0.05)
                                                self.log_signal.emit(f"📝 Yazılan: {i+1}/{len(windows_path)} karakter")
                                    except Exception as e:
                                        self.log_signal.emit(f"❌ Dosya yolu yazma hatası: {str(e)}")
                                        return False
                                    
                                    self.sb.sleep(2)  # Yazma sonrası ek bekleme
                                    
                                    # Enter'a bas (Aç butonuna basma)
                                    self.log_signal.emit("⌨️ Enter'a basılıyor...")
                                    pyautogui.press('enter')
                                    self.sb.sleep(3)
                                    
                                    # Eğer hala açıksa alternatif yöntem
                                    self.log_signal.emit("🔄 Alternatif yöntem deneniyor...")
                                    
   
                                    
                                    self.log_signal.emit("✅ Dosya seçimi tamamlandı")
                                    
                                    # Dosya seçimi sonrası tarayıcı bağlantısını kontrol et
                                    if not self.check_browser_alive():
                                        self.log_signal.emit("⚠️ Tarayıcı bağlantısı zayıf - dosya seçimi sonrası, devam ediliyor...")
                                        self.sb.sleep(2)  # Kısa bekleme
                                    
                                except ImportError:
                                    self.log_signal.emit("❌ pyautogui modülü bulunamadı!")
                                    self.log_signal.emit("💡 Kurulum: pip install pyautogui")
                                    self.log_signal.emit("⚠️ Manuel olarak dosyayı seçin")
                                except Exception as e:
                                    self.log_signal.emit(f"❌ Otomatik dosya seçme hatası: {str(e)}")
                                    self.log_signal.emit("⚠️ Manuel olarak dosyayı seçin")
                                
                                # Resim yüklenmesini bekle - kısa aralıklarla kontrol et
                                self.log_signal.emit("⏳ Resim yüklenmesi bekleniyor...")
                                total_wait = random.uniform(5, 8)
                                wait_intervals = 4  # 4 parçaya böl
                                interval_time = total_wait / wait_intervals
                                
                                for i in range(wait_intervals):
                                    self.sb.sleep(interval_time)
                                    # Her aralıkta tarayıcı bağlantısını kontrol et
                                    if not self.check_browser_alive():
                                        self.log_signal.emit(f"🔴 Tarayıcı bağlantısı kesildi - resim yükleme bekleme sırasında ({i+1}/{wait_intervals})")
                                        failed_shares += 1
                                        break
                                else:
                                    # Tüm aralıklar başarıyla tamamlandı
                                    self.log_signal.emit("✅ Resim yükleme bekleme süresi tamamlandı")

                                # Paylaş butonuna tıklama
                                self.log_signal.emit("⏳ 5 saniye bekleniyor...")
                                self.sb.sleep(5)
                                try:
                                    # Kullanıcının verdiği spesifik paylaş butonu seçicisi
                                    share_button_xpath = '//div[@role="button" and @aria-label="Paylaş" and not(.//i)]'
                                    self.log_signal.emit("🎯 Paylaş butonuna tıklanıyor (Kullanıcı Seçicisi)...")
                                    self.sb.click(share_button_xpath)
                                    self.log_signal.emit("✅ Paylaş butonuna tıklandı (Kullanıcı Seçicisi)!")
                                    # Paylaşımın tamamlanması için bekleme
                                    self.log_signal.emit("⏳ Paylaşımın tamamlanması bekleniyor...")
                                    self.sb.sleep(8)  # Paylaşım işleminin tamamlanması için bekleme
                                except Exception as e:
                                    self.log_signal.emit(f"⚠️ Spesifik seçici ile tıklama başarısız: {str(e)}")
                                    try:
                                        # Genel paylaş butonu seçicisi
                                        general_selector = 'div[aria-label="Paylaş"][role="button"]'
                                        self.log_signal.emit("🎯 Paylaş butonuna tıklanıyor (Genel Seçici)...")
                                        self.sb.click(general_selector)
                                        self.log_signal.emit("✅ Paylaş butonuna tıklandı (Genel Seçici)!")
                                        # Paylaşımın tamamlanması için bekleme
                                        self.log_signal.emit("⏳ Paylaşımın tamamlanması bekleniyor...")
                                        self.sb.sleep(8)  # Paylaşım işleminin tamamlanması için bekleme
                                    except Exception as e2:
                                        self.log_signal.emit(f"⚠️ Genel seçici ile tıklama başarısız: {str(e2)}")
                                        try:
                                            # XPath ile son deneme
                                            xpath = '//*[@id="mount_0_0_p9"]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/form/div/div[1]/div/div/div/div[3]/div[3]/div/div'
                                            self.log_signal.emit("🎯 Paylaş butonuna tıklanıyor (XPath)...")
                                            self.sb.click(xpath)
                                            self.log_signal.emit("✅ Paylaş butonuna tıklandı (XPath)!")
                                            # Paylaşımın tamamlanması için bekleme
                                            self.log_signal.emit("⏳ Paylaşımın tamamlanması bekleniyor...")
                                            self.sb.sleep(8)  # Paylaşım işleminin tamamlanması için bekleme
                                        except Exception as e3:
                                            self.log_signal.emit(f"❌ Paylaş butonuna tıklanamadı (Tüm yöntemler başarısız): {str(e3)}")
                                            # Paylaş butonu başarısız olsa bile devam et
                                            self.log_signal.emit("⚠️ Paylaş butonu tıklanamadı, bir sonraki gruba geçiliyor...")
                                
                                # Paylaşım tamamlandı, bir sonraki gruba geç
                                self.log_signal.emit("✅ Bu grup için işlem tamamlandı, bir sonraki gruba geçiliyor...")
                                
                            else:
                                self.log_signal.emit("❌ Resim ekleme butonu bulunamadı")
                        
                        except Exception as e:
                            self.log_signal.emit(f"❌ Resim ekleme hatası: {str(e)}")
                            # Resim ekleme hatası sonrası tarayıcı kontrolü
                            if not self.check_browser_alive():
                                self.log_signal.emit("❌ Tarayıcı bağlantısı resim ekleme hatası sonrası koptu")
                                failed_shares += 1
                                continue
                    
                    # Paylaş butonu aramadan önce tarayıcı bağlantısını kontrol et
                    if not self.check_browser_alive():
                        self.log_signal.emit("❌ Tarayıcı bağlantısı paylaş butonu arama öncesi koptu")
                        failed_shares += 1
                        continue
                    
                   
                    
                    # SeleniumBase ile Paylaş butonuna tıklama
                    self.log_signal.emit("🎯 Paylaş butonu aranıyor...")
                    shared = False
                    button_found = False
                    button_clicked = False
                    
                    # Resim yükleme sonrası kısa bir bekleme ekle
                    self.sb.sleep(3)
                    self.log_signal.emit("⏳ Paylaş butonu için ek bekleme süresi tamamlandı")
                    
                    try:
                        # Paylaş butonu seçicileri - genişletilmiş liste
                        share_selectors = [
                            'div[aria-label="Paylaş"][class="x1i10hfl xjbqb8w x1ejq31n x18oe1m7 x1sy0etr xstzfhl x972fbf x10w94by x1qhh985 x14e42zd x1ypdohk x3ct3a4 xdj266r x14z9mp xat24cr x1lziwak xexx8yu xyri2b x18d9i69 x1c1uobl x16tdsg8 x1hl2dhg xggy1nq x1fmog5m xu25z0z x140muxe xo1y3bh x87ps6o x1lku1pv x1a2a7pz x9f619 x3nfvp2 xdt5ytf xl56j7k x1n2onr6 xh8yej3"][role="button"]',
                            'div[aria-label="Paylaş"][role="button"]',
                            'div[role="button"]:contains("Paylaş")',
                            'button:contains("Paylaş")',
                            '[aria-label*="Paylaş"]',
                            'span:contains("Paylaş")',
                            'div[aria-label="Paylaş"]',
                            'div[role="button"][aria-label="Paylaş"]',
                            'div.x1i10hfl[aria-label="Paylaş"]',
                            # İngilizce seçiciler
                            'div[aria-label="Share"][role="button"]',
                            'div[role="button"]:contains("Share")',
                            'button:contains("Share")',
                            '[aria-label*="Share"]',
                            'span:contains("Share")',
                            'div[aria-label="Share"]',
                            'div[role="button"][aria-label="Share"]',
                            # Genel buton seçiciler
                            'button.share-button',
                            'button.post-button',
                            'button.submit-button',
                            'div.share-button',
                            'a.share-button'
                        ]
                        
                        # Seçicileri dene - Önce görünür elementleri kontrol et
                        for selector in share_selectors:
                            try:
                                if self.sb.is_element_present(selector) and self.sb.is_element_visible(selector):
                                    # Element hakkında bilgi al
                                    element_info = self.sb.cdp.evaluate(f'''
                                        (function() {{
                                            const el = document.querySelector('{selector}');
                                            if (!el) return 'Element bulunamadı';
                                            
                                            return {{
                                                tag: el.tagName,
                                                text: el.innerText || el.textContent,
                                                position: {{
                                                    x: el.getBoundingClientRect().left,
                                                    y: el.getBoundingClientRect().top
                                                }},
                                                size: {{
                                                    width: el.offsetWidth,
                                                    height: el.offsetHeight
                                                }},
                                                isVisible: el.offsetWidth > 0 && el.offsetHeight > 0
                                            }};
                                        }})();
                                    ''')
                                    
                                    self.log_signal.emit(f"🔍 Paylaş butonu bulundu: {element_info}")
                                    button_found = True
                                    
                                    # Farklı tıklama yöntemlerini dene
                                    try:
                                        # 1. Yöntem: Normal tıklama
                                        self.sb.click(selector)
                                        self.sb.sleep(0.5)  # Kısa bekleme
                                        shared = True
                                        button_clicked = True
                                        self.log_signal.emit("✅ GERÇEK PAYLAŞ BUTONU TIKLANDI!")
                                        break
                                    except Exception as click_error:
                                        self.log_signal.emit(f"⚠️ Normal tıklama başarısız: {str(click_error)}")
                                        
                                        try:
                                            # 2. Yöntem: JavaScript ile tıklama
                                            self.sb.cdp.evaluate(f'''
                                                (function() {{
                                                    const el = document.querySelector('{selector}');
                                                    if (el) {{
                                                        el.click();
                                                        return true;
                                                    }}
                                                    return false;
                                                }})();
                                            ''')
                                            self.sb.sleep(0.5)  # Kısa bekleme
                                            shared = True
                                            button_clicked = True
                                            self.log_signal.emit("✅ GERÇEK PAYLAŞ BUTONU JavaScript ile TIKLANDI!")
                                            break
                                        except Exception as js_click_error:
                                            self.log_signal.emit(f"⚠️ JavaScript tıklama başarısız: {str(js_click_error)}")
                                            
                                            try:
                                                # 3. Yöntem: Koordinat ile tıklama
                                                if isinstance(element_info, dict) and 'position' in element_info:
                                                    x = element_info['position']['x'] + (element_info['size']['width'] / 2)
                                                    y = element_info['position']['y'] + (element_info['size']['height'] / 2)
                                                    self.sb.cdp.evaluate(f'''
                                                        (function() {{
                                                            const evt = new MouseEvent('click', {{
                                                                bubbles: true,
                                                                cancelable: true,
                                                                view: window,
                                                                clientX: {x},
                                                                clientY: {y}
                                                            }});
                                                            document.elementFromPoint({x}, {y}).dispatchEvent(evt);
                                                        }})();
                                                    ''')
                                                    self.sb.sleep(0.5)  # Kısa bekleme
                                                    shared = True
                                                    button_clicked = True
                                                    self.log_signal.emit(f"✅ GERÇEK PAYLAŞ BUTONU koordinat ile TIKLANDI! ({x}, {y})")
                                                    break
                                            except Exception as coord_click_error:
                                                self.log_signal.emit(f"⚠️ Koordinat tıklama başarısız: {str(coord_click_error)}")
                            except Exception as selector_error:
                                self.log_signal.emit(f"⚠️ Seçici hatası ({selector}): {str(selector_error)}")
                                continue
                        
                        # Eğer hala tıklanamadıysa, görünmez elementleri de dene
                        if not shared:
                            self.log_signal.emit("🔄 Görünür olmayan paylaş butonları aranıyor...")
                            for selector in share_selectors:
                                try:
                                    if self.sb.is_element_present(selector):
                                        # Elementi görünür yap ve tıkla
                                        self.sb.cdp.evaluate(f'''
                                            (function() {{
                                                const el = document.querySelector('{selector}');
                                                if (el) {{
                                                    el.style.opacity = '1';
                                                    el.style.visibility = 'visible';
                                                    el.style.display = 'block';
                                                    el.style.pointerEvents = 'auto';
                                                    el.click();
                                                    return true;
                                                }}
                                                return false;
                                            }})();
                                        ''')
                                        self.sb.sleep(0.5)  # Kısa bekleme
                                        shared = True
                                        self.log_signal.emit("✅ Gizli paylaş butonuna tıklandı!")
                                        break
                                except Exception:
                                    continue
                        
                        if not shared:
                            if button_found:
                                self.log_signal.emit("❌ BUTON BULUNDU AMA TIKLANAMADI - Tüm tıklama yöntemleri başarısız")
                            else:
                                self.log_signal.emit("❌ HİÇBİR PAYLAŞ BUTONU BULUNAMADI - Tüm seçiciler denendi")
                            
                            # Son çare: Tüm potansiyel butonları bul ve tıkla
                            try:
                                self.log_signal.emit("🔄 Tüm potansiyel paylaş butonları aranıyor...")
                                potential_buttons = self.sb.cdp.evaluate('''
                                    (function() {
                                        const results = [];
                                        // Tüm butonları ve button rolü olan elementleri bul
                                        const elements = [...document.querySelectorAll('button, div[role="button"], a[role="button"], span[role="button"], input[type="submit"], input[type="button"]')];
                                        
                                        // Paylaş/Share ile ilgili kelimeleri içeren elementleri filtrele
                                        const keywords = ['paylaş', 'share', 'post', 'gönder', 'yayınla', 'publish'];
                                        
                                        for (const el of elements) {
                                            const text = (el.innerText || el.textContent || '').toLowerCase();
                                            const ariaLabel = (el.getAttribute('aria-label') || '').toLowerCase();
                                            const value = (el.value || '').toLowerCase();
                                            const id = (el.id || '').toLowerCase();
                                            const className = (el.className || '').toLowerCase();
                                            
                                            // Herhangi bir anahtar kelime içeriyor mu kontrol et
                                            const hasKeyword = keywords.some(keyword => 
                                                text.includes(keyword) || 
                                                ariaLabel.includes(keyword) || 
                                                value.includes(keyword) || 
                                                id.includes(keyword) || 
                                                className.includes(keyword)
                                            );
                                            
                                            if (hasKeyword) {
                                                results.push({
                                                    tag: el.tagName,
                                                    text: text,
                                                    ariaLabel: ariaLabel,
                                                    value: value,
                                                    position: {
                                                        x: el.getBoundingClientRect().left,
                                                        y: el.getBoundingClientRect().top
                                                    },
                                                    size: {
                                                        width: el.offsetWidth,
                                                        height: el.offsetHeight
                                                    },
                                                    isVisible: el.offsetWidth > 0 && el.offsetHeight > 0 && 
                                                              window.getComputedStyle(el).visibility !== 'hidden' && 
                                                              window.getComputedStyle(el).display !== 'none'
                                                });
                                                
                                                // Elementi tıkla
                                                try {
                                                    el.click();
                                        return { clicked: true, element: results[results.length-1] };
                                                } catch (e) {
                                                    // Tıklama başarısız olursa, event oluştur
                                                    try {
                                                        const evt = new MouseEvent('click', {
                                                            bubbles: true,
                                                            cancelable: true,
                                                            view: window
                                                        });
                                                        el.dispatchEvent(evt);
                                                        return { clicked: true, element: results[results.length-1], method: 'event' };
                                                    } catch (eventError) {
                                                        // Event de başarısız olursa devam et
                                                    }
                                                }
                                            }
                                        }
                                        
                                        // Hiçbir buton tıklanamadıysa, tüm sonuçları döndür
                                        return { clicked: false, elements: results };
                                    })();
                                ''')
                                
                                if potential_buttons and potential_buttons.get('clicked', False):
                                    shared = True
                                    button_clicked = True
                                    self.log_signal.emit("✅ SON ÇARE - POTANSİYEL PAYLAŞ BUTONU TIKLANDI!")
                                    self.log_signal.emit(f"📍 Tıklanan element: {potential_buttons.get('element', {})}")
                                else:
                                    self.log_signal.emit("❌ SON ÇARE DE BAŞARISIZ - Hiçbir potansiyel buton tıklanamadı")
                                    self.log_signal.emit(f"📊 Bulunan potansiyel buton sayısı: {len(potential_buttons.get('elements', []))}")
                            except Exception as potential_error:
                                self.log_signal.emit(f"⚠️ Potansiyel buton arama hatası: {str(potential_error)}")
                            
                    except Exception as e:
                        self.log_signal.emit(f"❌ Paylaş butonu arama hatası: {str(e)}")
                            
                    except Exception as e:
                        self.log_signal.emit(f"❌ Paylaş butonu tıklama hatası: {str(e)}")
                    
                    # Button arama sonucu özet
                    if shared:
                        self.log_signal.emit("🎉 BUTON BAŞARIYLA TIKLANDI - Paylaşım doğrulaması başlatılıyor...")
                    else:
                        self.log_signal.emit("❌ BUTON TIKLANAMADI - Paylaşım başarısız olarak işaretlenecek")
                    
                    # Paylaş işlemi sonrası onay penceresi - SADECE GERÇEK TIKLAMA SONRASI
                    if shared:
                        self.sb.sleep(3)  # Facebook'un işlem yapması için daha uzun bekle
                        confirmation_result = self.handle_browser_confirmation()
                        
                        # Paylaşımın gerçekten tamamlandığını doğrula
                        try:
                            # Paylaşım sonrası URL veya sayfa içeriği kontrolü
                            current_url = self.sb.get_current_url()
                            page_text = self.sb.get_page_source()
                            
                            # Paylaşım başarılı olduğunu gösteren belirtiler
                            success_indicators = [
                                "paylaşıldı", "shared", "success", "başarılı",
                                "paylaşım tamamlandı", "gönderi paylaşıldı", "gönderildi", "posted"
                            ]
                            
                            # Paylaşım başarısız olduğunu gösteren belirtiler
                            failure_indicators = [
                                "hata", "error", "failed", "başarısız", 
                                "paylaşılamadı", "tekrar deneyin"
                            ]
                            
                            # Başarı belirtileri kontrolü
                            success_found = any(indicator.lower() in page_text.lower() for indicator in success_indicators)
                            failure_found = any(indicator.lower() in page_text.lower() for indicator in failure_indicators)
                            
                            # Paylaşım başarılı mı kontrol et
                            if success_found and not failure_found:
                                successful_shares += 1
                                self.log_signal.emit(f"✅ Grup {i+1} paylaşımı başarılı: {group['name']}")
                            else:
                                # Paylaşım doğrulanamadı - başarısız olarak işaretle
                                failed_shares += 1
                                self.log_signal.emit(f"❌ Grup {i+1} paylaşımı başarısız: {group['name']} - Paylaşım doğrulanamadı")
                        except Exception as verify_error:
                            self.log_signal.emit(f"⚠️ Paylaşım doğrulama hatası: {str(verify_error)}")
                            # Doğrulama hatası durumunda paylaşımı başarısız say
                            failed_shares += 1
                            self.log_signal.emit(f"❌ Grup {i+1} paylaşımı başarısız (doğrulama hatası): {group['name']}")
                    else:
                        # Butona tıklanamadıysa doğrudan başarısız olarak işaretle
                        failed_shares += 1
                        self.log_signal.emit(f"❌ Grup {i+1} paylaşımı başarısız: {group['name']} - Paylaş butonu bulunamadı veya tıklanamadı")
                    
                    # Progress güncelle
                    self.progress_signal.emit(i + 1)
                    
                    # Son grup değilse bekleme süresi
                    if i < len(self.selected_groups) - 1:
                        self.log_signal.emit(f"⏳ Sonraki grup için {self.delay_seconds} saniye bekleniyor...")
                        self.sb.sleep(self.delay_seconds)
                
                except Exception as e:
                    failed_shares += 1
                    self.log_signal.emit(f"❌ Grup {i+1} ({group['name']}) paylaşım hatası: {str(e)}")
                    self.progress_signal.emit(i + 1)
                    continue
            
            # Sonuç raporu
            total_groups = len(self.selected_groups)
            success_message = f"Paylaşım tamamlandı!\n\nBaşarılı: {successful_shares}/{total_groups}\nBaşarısız: {failed_shares}/{total_groups}"
            
            self.log_signal.emit(f"🏁 Paylaşım raporu: {successful_shares} başarılı, {failed_shares} başarısız")
            self.finished_signal.emit(True, success_message)
            
        except Exception as e:
            self.log_signal.emit(f"❌ Genel hata: {str(e)}")
            self.finished_signal.emit(False, f"Paylaşım hatası: {str(e)}")


class FacebookLoginThread(QThread):
    """Facebook giriş işlemlerini arka planda çalıştıran thread"""
    
    # Sinyaller
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)
    groups_signal = pyqtSignal(list)  # Grup linklerini göndermek için
    
    def __init__(self, login_type, email=None, password=None, cookie_file=None, wait_time=15, collect_groups=False):
        super().__init__()
        self.login_type = login_type  # "credentials" veya "cookies"
        self.email = email
        self.password = password
        self.cookie_file = cookie_file
        self.cookies_saved = False
        self.wait_time = wait_time  # Manuel doğrulama bekleme süresi
        self.collect_groups = collect_groups  # Grup toplama özelliği
        self.sb_instance = None  # SeleniumBase instance'ını saklamak için
        
    def run(self):
        """Ana giriş işlemi"""
        try:
            if self.login_type == "credentials":
                self.login_with_credentials()
            elif self.login_type == "cookies":
                self.login_with_cookies()
        except Exception as e:
            self.log_signal.emit(f"❌ Hata: {str(e)}")
            self.finished_signal.emit(False, str(e))
    
    def login_with_credentials(self):
        """Email ve şifre ile giriş"""
        self.log_signal.emit("🚀 Facebook'a email/şifre ile giriş başlatılıyor...")
        self.progress_signal.emit(10)
        
        with SB(uc=True, test=True, locale="tr", ad_block=True, headless=False, maximize=True) as sb:
            try:
                # Facebook ana sayfasına git
                self.log_signal.emit("🌐 Facebook.com'a gidiliyor...")
                sb.activate_cdp_mode("https://www.facebook.com/")
                self.progress_signal.emit(20)
                
                # Sayfanın yüklenmesini bekle
                self.log_signal.emit("⏳ Sayfa yükleniyor...")
                sb.sleep(random.uniform(3, 5))
                self.progress_signal.emit(30)
                
                # Debug bilgilerini logla
                self.debug_page_info(sb)
                
                # Tam ekran modu ve sayfa dışı tıklamaları engelle
                self.log_signal.emit("🖥️ Tam ekran modu etkinleştiriliyor...")
                try:
                    # Tam ekran modu
                    sb.cdp.evaluate("""
                        // Tam ekran modu
                        if (document.documentElement.requestFullscreen) {
                            document.documentElement.requestFullscreen();
                        } else if (document.documentElement.webkitRequestFullscreen) {
                            document.documentElement.webkitRequestFullscreen();
                        } else if (document.documentElement.msRequestFullscreen) {
                            document.documentElement.msRequestFullscreen();
                        }
                        
                        // Sayfa dışı tıklamaları engelle
                        document.addEventListener('click', function(e) {
                            // Sadece Facebook içeriği alanında tıklamaya izin ver
                            const facebookContent = document.querySelector('#mount_0_0, [role="main"], [data-pagelet]');
                            if (facebookContent && !facebookContent.contains(e.target)) {
                                e.preventDefault();
                                e.stopPropagation();
                                console.log('Sayfa dışı tıklama engellendi');
                                return false;
                            }
                        }, true);
                        
                        // Adres çubuğu ve tarayıcı UI'sine tıklamayı engelle
                        document.addEventListener('mousedown', function(e) {
                            if (e.clientY < 0 || e.clientX < 0) {
                                e.preventDefault();
                                e.stopPropagation();
                                return false;
                            }
                        }, true);
                    """)
                    sb.sleep(2)
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Tam ekran ayarları uygulanamadı: {str(e)}")
                
                # Cookie banner'ını kapat (varsa)
                try:
                    sb.cdp.click_if_visible('button[data-cookiebanner="accept_button"]')
                    sb.sleep(1)
                except:
                    pass
                
                # Email alanını bul ve doldur
                self.log_signal.emit("📧 Email giriliyor...")
                # Birden fazla seçici dene
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
                            self.log_signal.emit(f"✅ Email alanı bulundu: {selector}")
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
                sb.cdp.press_keys(email_selector, self.email)
                sb.sleep(random.uniform(0.5, 1.0))
                
                self.progress_signal.emit(50)
                
                # Şifre alanını bul ve doldur
                self.log_signal.emit("🔐 Şifre giriliyor...")
                # Birden fazla şifre seçici dene
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
                            self.log_signal.emit(f"✅ Şifre alanı bulundu: {selector}")
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
                sb.cdp.press_keys(password_selector, self.password)
                sb.sleep(random.uniform(0.5, 1.0))
                
                self.progress_signal.emit(70)
                
                # Giriş butonuna tıkla
                self.log_signal.emit("🔘 Giriş butonuna tıklanıyor...")
                # Birden fazla giriş butonu seçici dene
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
                            self.log_signal.emit(f"✅ Giriş butonu bulundu: {selector}")
                            break
                    except:
                        continue
                
                if not login_button:
                    raise Exception("Giriş butonu bulunamadı!")
                
                sb.cdp.click(login_button)
                
                # Manuel doğrulama için bekleme süresi
                self.log_signal.emit("⏳ Giriş butonuna tıklandı, manuel doğrulama bekleniyor...")
                self.log_signal.emit("🔐 2FA/CAPTCHA/Güvenlik kontrolü varsa lütfen manuel olarak tamamlayın...")
                self.log_signal.emit(f"⏰ {self.wait_time} saniye bekleme süresi başladı...")
                self.log_signal.emit("💡 Bu süre içinde tarayıcıda gerekli doğrulamaları yapabilirsiniz")
                
                # Belirlenen süre boyunca her saniye güncelleme
                for i in range(self.wait_time):
                    remaining = self.wait_time - i
                    if remaining > 0:
                        self.log_signal.emit(f"⏳ Kalan süre: {remaining} saniye...")
                        # Progress bar'ı 70'den 85'e kadar güncelle
                        progress = 70 + int((i / self.wait_time) * 15)
                        self.progress_signal.emit(progress)
                    sb.sleep(1)
                
                self.log_signal.emit("✅ Bekleme süresi tamamlandı, giriş durumu kontrol ediliyor...")
                self.progress_signal.emit(85)
                
                # Giriş başarılı mı kontrol et
                current_url = sb.cdp.get_current_url()
                self.log_signal.emit(f"🔍 Giriş sonrası URL: {current_url}")
                
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
                                self.log_signal.emit(f"✅ Ana sayfa elementi bulundu: {element}")
                                element_found = True
                                break
                        except:
                            continue
                    
                    success_indicators.append(element_found)
                except:
                    pass
                
                if any(success_indicators):
                    self.log_signal.emit("✅ Giriş başarılı!")
                    
                    # Cookie'leri kaydet
                    self.save_cookies(sb)
                    self.progress_signal.emit(85)
                    
                    # Grup toplama özelliği aktifse grupları topla
                    if self.collect_groups:
                        self.log_signal.emit("🔍 Grup toplama başlatılıyor...")
                        collected_groups = self.collect_facebook_groups(sb)
                        self.log_signal.emit(f"✅ {len(collected_groups)} grup toplandı!")
                    
                    self.progress_signal.emit(100)
                    
                    # Tarayıcıyı açık bırak
                    self.sb_instance = sb
                    self.log_signal.emit("🌐 Tarayıcı açık bırakıldı - Manuel olarak kapatabilirsiniz")
                    self.finished_signal.emit(True, "Giriş başarılı ve cookie'ler kaydedildi!")
                    
                    # Tarayıcının kapanmaması için sonsuz döngü
                    self.log_signal.emit("⏳ Tarayıcı açık tutuluyor... (Kapatmak için uygulamayı kapatın)")
                    while True:
                        sb.sleep(10)  # 10 saniye bekle
                        try:
                            # Tarayıcının hala açık olup olmadığını kontrol et
                            sb.cdp.get_current_url()
                        except:
                            # Tarayıcı kapatıldıysa döngüden çık
                            self.log_signal.emit("🔴 Tarayıcı kapatıldı")
                            break
                else:
                    self.log_signal.emit("❌ Giriş başarısız - Kontroller başarısız")
                    # Debug için daha fazla bilgi
                    self.debug_page_info(sb)
                    self.finished_signal.emit(False, "Giriş başarısız - Lütfen bilgilerinizi kontrol edin")
                    
            except Exception as e:
                self.log_signal.emit(f"❌ Giriş hatası: {str(e)}")
                self.finished_signal.emit(False, str(e))
    
    def login_with_cookies(self):
        """Cookie dosyası ile giriş"""
        self.log_signal.emit("🍪 Cookie dosyası ile giriş başlatılıyor...")
        self.progress_signal.emit(10)
        
        if not os.path.exists(self.cookie_file):
            self.finished_signal.emit(False, "Cookie dosyası bulunamadı!")
            return
        
        with SB(uc=True, test=True, locale="tr", ad_block=True, headless=False, maximize=True) as sb:
            try:
                # Facebook'a git
                self.log_signal.emit("🌐 Facebook.com'a gidiliyor...")
                sb.activate_cdp_mode("https://www.facebook.com/")
                self.progress_signal.emit(30)
                
                # Cookie'leri yükle
                self.log_signal.emit("🍪 Cookie'ler yükleniyor...")
                with open(self.cookie_file, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                
                # Cookie'leri tarayıcıya ekle - Önce cookie'leri yükle, sonra Facebook'a git
                self.log_signal.emit(f"🍪 {len(cookies)} cookie yükleniyor...")
                success_count = 0
                facebook_cookies = 0
                
                # Önce Facebook'a git (cookie yüklemek için)
                self.log_signal.emit("🌐 Facebook domain'ine gidiliyor...")
                sb.cdp.get("https://www.facebook.com/")
                sb.sleep(2)
                
                # Çift yöntemle cookie yükleme (test_cookie_direct.py'den)
                for i, cookie in enumerate(cookies):
                    try:
                        if isinstance(cookie, dict) and cookie.get('name') and cookie.get('value'):
                            # Facebook cookie'si kontrolü
                            domain = cookie.get('domain', '')
                            if 'facebook.com' not in domain:
                                continue
                            
                            facebook_cookies += 1
                            
                            # Yöntem 1: CDP ile yükle
                            clean_cookie = {
                                'name': cookie['name'],
                                'value': cookie['value'],
                                'domain': cookie.get('domain', '.facebook.com'),
                                'path': cookie.get('path', '/'),
                                'secure': cookie.get('secure', True),
                                'httpOnly': cookie.get('httpOnly', False),
                                'sameSite': cookie.get('sameSite', 'Lax')
                            }
                            
                            if 'expires' in cookie:
                                clean_cookie['expires'] = cookie['expires']
                            
                            sb.cdp.set_all_cookies([clean_cookie])
                            
                            # Yöntem 2: JavaScript ile direkt yükle (daha etkili)
                            cookie_string = f"{cookie['name']}={cookie['value']}; domain={cookie['domain']}; path={cookie['path']}"
                            if cookie.get('secure'):
                                cookie_string += "; secure"
                            if cookie.get('sameSite'):
                                cookie_string += f"; samesite={cookie['sameSite']}"
                            
                            js_code = f"document.cookie = '{cookie_string}'"
                            sb.cdp.evaluate(js_code)
                            
                            success_count += 1
                            status = "🔑" if cookie['name'] in ['c_user', 'xs', 'datr', 'sb'] else "✅"
                            self.log_signal.emit(f"{status} Cookie {i+1}: {cookie['name']}")
                            
                    except Exception as cookie_error:
                        self.log_signal.emit(f"❌ Cookie {i+1} hatası: {str(cookie_error)}")
                        continue
                
                self.log_signal.emit(f"✅ {success_count}/{len(cookies)} cookie yüklendi ({facebook_cookies} Facebook cookie'si)")
                
                if facebook_cookies == 0:
                    self.log_signal.emit("⚠️ Hiç Facebook cookie'si bulunamadı!")
                    self.finished_signal.emit(False, "Facebook cookie'si bulunamadı")
                    return
                elif facebook_cookies < 3:
                    self.log_signal.emit("⚠️ Az sayıda Facebook cookie'si var, giriş başarısız olabilir")
                
                self.progress_signal.emit(60)
                
                # Cookie'ler yüklendikten sonra tek sayfa yenileme
                self.log_signal.emit("🔄 Cookie'ler yüklendi, sayfa yenileniyor...")
                sb.cdp.reload()
                sb.sleep(3)
                
                # Cookie giriş için kısa bekleme
                self.log_signal.emit("⏳ Cookie'lerin işlenmesi bekleniyor...")
                sb.sleep(2)  # Sadece 2 saniye bekle
                
                self.progress_signal.emit(80)
                
                # Debug bilgilerini logla
                self.debug_page_info(sb)
                
                # Tam ekran modu ve sayfa dışı tıklamaları engelle
                self.log_signal.emit("🖥️ Tam ekran modu etkinleştiriliyor...")
                try:
                    # Tam ekran modu
                    sb.cdp.evaluate("""
                        // Tam ekran modu
                        if (document.documentElement.requestFullscreen) {
                            document.documentElement.requestFullscreen();
                        } else if (document.documentElement.webkitRequestFullscreen) {
                            document.documentElement.webkitRequestFullscreen();
                        } else if (document.documentElement.msRequestFullscreen) {
                            document.documentElement.msRequestFullscreen();
                        }
                        
                        // Sayfa dışı tıklamaları engelle
                        document.addEventListener('click', function(e) {
                            // Sadece Facebook içeriği alanında tıklamaya izin ver
                            const facebookContent = document.querySelector('#mount_0_0, [role="main"], [data-pagelet]');
                            if (facebookContent && !facebookContent.contains(e.target)) {
                                e.preventDefault();
                                e.stopPropagation();
                                console.log('Sayfa dışı tıklama engellendi');
                                return false;
                            }
                        }, true);
                        
                        // Adres çubuğu ve tarayıcı UI'sine tıklamayı engelle
                        document.addEventListener('mousedown', function(e) {
                            if (e.clientY < 0 || e.clientX < 0) {
                                e.preventDefault();
                                e.stopPropagation();
                                return false;
                            }
                        }, true);
                    """)
                    sb.sleep(2)
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Tam ekran ayarları uygulanamadı: {str(e)}")
                
                # Giriş kontrolü
                current_url = sb.cdp.get_current_url()
                page_title = sb.cdp.get_title()
                self.log_signal.emit(f"🔍 Cookie giriş sonrası URL: {current_url}")
                self.log_signal.emit(f"🔍 Sayfa başlığı: {page_title}")
                
                # Giriş sayfası elementlerini kontrol et
                login_elements_present = False
                try:
                    login_selectors = [
                        'input[name="email"]',
                        'input[name="pass"]',
                        'button[name="login"]'
                    ]
                    
                    login_count = 0
                    for selector in login_selectors:
                        if sb.cdp.is_element_visible(selector):
                            login_count += 1
                    
                    login_elements_present = login_count >= 2  # En az 2 giriş elementi varsa
                    self.log_signal.emit(f"🔍 Giriş elementi sayısı: {login_count}/3")
                    
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Element kontrol hatası: {str(e)}")
                
                # Ana sayfa elementlerini kontrol et (daha spesifik)
                home_elements_found = False
                try:
                    # Sadece giriş yapmış kullanıcılarda olan spesifik elementler
                    specific_home_selectors = [
                        '[data-testid="newsfeed"]',  # Ana akış
                        '[aria-label="Ana Sayfa"][role="link"]',  # Ana sayfa linki
                        '[data-testid="left_nav_menu_list"]',  # Sol menü
                        '[data-testid="Keycommand_wrapper_ModalLayer"]',  # Modal wrapper
                        'div[data-pagelet="LeftRail"]',  # Sol panel
                        '[data-testid="search"]',  # Arama kutusu (giriş yapmış)
                        'div[role="complementary"]'  # Sağ panel
                    ]
                    
                    home_element_count = 0
                    for selector in specific_home_selectors:
                        try:
                            if sb.cdp.is_element_visible(selector):
                                self.log_signal.emit(f"✅ Spesifik ana sayfa elementi: {selector}")
                                home_element_count += 1
                        except:
                            continue
                    
                    # En az 2 spesifik element varsa ana sayfada sayılır
                    home_elements_found = home_element_count >= 2
                    self.log_signal.emit(f"🔍 Spesifik ana sayfa elementi sayısı: {home_element_count}")
                            
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Ana sayfa kontrol hatası: {str(e)}")
                
                # Başarı kriterleri - daha sıkı kontrol
                url_success = "facebook.com" in current_url and "login" not in current_url
                title_success = not any(word in page_title.lower() for word in ['giriş', 'login', 'kaydol', 'sign up', 'log in'])
                element_success = not login_elements_present and home_elements_found
                
                self.log_signal.emit(f"🔍 URL başarılı: {url_success}")
                self.log_signal.emit(f"🔍 Başlık başarılı: {title_success} ('{page_title}')")
                self.log_signal.emit(f"🔍 Element başarılı: {element_success} (giriş yok: {not login_elements_present}, ana sayfa var: {home_elements_found})")
                
                # JavaScript ile detaylı cookie kontrolü (test_cookie_direct.py'den)
                user_logged_in = False
                try:
                    js_result = sb.cdp.evaluate("""
                        (function() {
                            var cookies = document.cookie;
                            var allCookies = cookies.split(';').map(c => c.trim());
                            var cookieObj = {};
                            
                            allCookies.forEach(function(cookie) {
                                var parts = cookie.split('=');
                                if (parts.length === 2) {
                                    cookieObj[parts[0]] = parts[1];
                                }
                            });
                            
                            return {
                                c_user: cookieObj['c_user'] || 'YOK',
                                xs: cookieObj['xs'] || 'YOK',
                                cookieCount: allCookies.length,
                                hasValidUser: cookieObj['c_user'] && cookieObj['c_user'] !== 'YOK'
                            };
                        })()
                    """)
                    
                    user_logged_in = js_result.get('hasValidUser', False)
                    self.log_signal.emit(f"🔍 Cookie Sayısı: {js_result.get('cookieCount', 0)}")
                    self.log_signal.emit(f"🔍 c_user: {js_result.get('c_user', 'YOK')[:15]}...")
                    self.log_signal.emit(f"🔍 Kullanıcı giriş yapmış: {user_logged_in}")
                    
                except Exception as js_error:
                    self.log_signal.emit(f"⚠️ JavaScript kontrol hatası: {str(js_error)}")
                
                # Başarı kontrolü: Giriş elementleri yok VE geçerli c_user cookie var
                final_success = not login_elements_present and user_logged_in
                
                if final_success:
                    self.log_signal.emit("🎉 Cookie ile giriş başarılı!")
                    self.log_signal.emit("✅ Facebook hesabınıza başarıyla giriş yapıldı")
                    self.progress_signal.emit(85)
                    
                    # Grup toplama özelliği aktifse grupları topla
                    if self.collect_groups:
                        self.log_signal.emit("🔍 Grup toplama başlatılıyor...")
                        collected_groups = self.collect_facebook_groups(sb)
                        self.log_signal.emit(f"✅ {len(collected_groups)} grup toplandı!")
                    
                    self.progress_signal.emit(100)
                    
                    # Tarayıcıyı açık bırak
                    self.sb_instance = sb
                    self.log_signal.emit("🌐 Tarayıcı açık bırakıldı - Manuel olarak kapatabilirsiniz")
                    self.finished_signal.emit(True, "Cookie ile giriş başarılı!")
                    
                    # Tarayıcının kapanmaması için sonsuz döngü
                    self.log_signal.emit("⏳ Tarayıcı açık tutuluyor... (Kapatmak için uygulamayı kapatın)")
                    while True:
                        sb.sleep(10)  # 10 saniye bekle
                        try:
                            # Tarayıcının hala açık olup olmadığını kontrol et
                            sb.cdp.get_current_url()
                        except:
                            # Tarayıcı kapatıldıysa döngüden çık
                            self.log_signal.emit("🔴 Tarayıcı kapatıldı")
                            break
                else:
                    self.log_signal.emit("❌ Cookie ile giriş başarısız")
                    if login_elements_present:
                        self.log_signal.emit("⚠️ Giriş sayfası elementleri hala mevcut")
                    if not user_logged_in:
                        self.log_signal.emit("⚠️ Geçerli kullanıcı cookie'si bulunamadı")
                    
                    self.log_signal.emit("💡 Çözüm: Email/şifre ile yeni giriş yapıp güncel cookie alın")
                    self.finished_signal.emit(False, "Cookie'ler geçersiz - Yeni giriş gerekli")
                    
            except Exception as e:
                self.log_signal.emit(f"❌ Cookie giriş hatası: {str(e)}")
                self.finished_signal.emit(False, str(e))
    
    def save_cookies(self, sb):
        """Cookie'leri dosyaya kaydet"""
        try:
            self.log_signal.emit("💾 Cookie'ler kaydediliyor...")
            
            # Farklı yöntemlerle cookie almayı dene
            cookies = None
            try:
                cookies = sb.cdp.get_all_cookies()
                self.log_signal.emit(f"🔍 CDP'den {len(cookies) if cookies else 0} cookie alındı")
            except Exception as e:
                self.log_signal.emit(f"⚠️ CDP cookie alma hatası: {str(e)}")
                
            # Alternatif yöntem: JavaScript ile cookie al
            if not cookies:
                try:
                    js_cookies = sb.cdp.evaluate("document.cookie")
                    self.log_signal.emit(f"🔍 JavaScript cookie: {js_cookies[:100] if js_cookies else 'Boş'}...")
                    if js_cookies:
                        # JavaScript cookie'lerini parse et
                        cookies = self.parse_js_cookies(js_cookies)
                except Exception as e:
                    self.log_signal.emit(f"⚠️ JavaScript cookie alma hatası: {str(e)}")
            
            if not cookies:
                self.log_signal.emit("❌ Hiç cookie bulunamadı!")
                return
            
            # Timestamp ile dosya adı oluştur
            timestamp = int(time.time())
            cookie_filename = f"facebook_cookies_{timestamp}.json"
            
            # Cookie'leri temizle ve formatla
            clean_cookies = []
            self.log_signal.emit(f"🔍 İşlenecek cookie sayısı: {len(cookies)}")
            
            for i, cookie in enumerate(cookies):
                try:
                    # Cookie objesinin tipini ve içeriğini debug et
                    cookie_type = type(cookie).__name__
                    self.log_signal.emit(f"🔍 Cookie {i+1} tipi: {cookie_type}")
                    
                    # Farklı yöntemlerle cookie bilgilerini al
                    clean_cookie = {}
                    
                    # Method 1: Direct attribute access
                    try:
                        clean_cookie = {
                            'name': cookie.name if hasattr(cookie, 'name') else '',
                            'value': cookie.value if hasattr(cookie, 'value') else '',
                            'domain': cookie.domain if hasattr(cookie, 'domain') else '.facebook.com',
                            'path': cookie.path if hasattr(cookie, 'path') else '/',
                            'secure': cookie.secure if hasattr(cookie, 'secure') else True,
                            'httpOnly': cookie.httpOnly if hasattr(cookie, 'httpOnly') else False
                        }
                        
                        # Opsiyonel alanlar
                        if hasattr(cookie, 'expires') and cookie.expires:
                            clean_cookie['expires'] = cookie.expires
                        if hasattr(cookie, 'sameSite') and cookie.sameSite:
                            clean_cookie['sameSite'] = cookie.sameSite
                        else:
                            clean_cookie['sameSite'] = 'Lax'
                            
                    except Exception as attr_error:
                        self.log_signal.emit(f"⚠️ Attribute access hatası: {str(attr_error)}")
                        
                        # Method 2: Dictionary access
                        try:
                            if isinstance(cookie, dict):
                                clean_cookie = {
                                    'name': cookie.get('name', ''),
                                    'value': cookie.get('value', ''),
                                    'domain': cookie.get('domain', '.facebook.com'),
                                    'path': cookie.get('path', '/'),
                                    'secure': cookie.get('secure', True),
                                    'httpOnly': cookie.get('httpOnly', False),
                                    'sameSite': cookie.get('sameSite', 'Lax')
                                }
                                if 'expires' in cookie:
                                    clean_cookie['expires'] = cookie['expires']
                        except Exception as dict_error:
                            self.log_signal.emit(f"⚠️ Dictionary access hatası: {str(dict_error)}")
                            continue
                    
                    # Cookie'nin geçerli olup olmadığını kontrol et
                    if clean_cookie.get('name') and clean_cookie.get('value'):
                        # Sadece Facebook cookie'lerini kaydet
                        domain = clean_cookie.get('domain', '')
                        if 'facebook.com' in domain or clean_cookie['name'] in ['datr', 'sb', 'c_user', 'xs', 'fr']:
                            clean_cookies.append(clean_cookie)
                            cookie_type = "🔑 Önemli" if clean_cookie['name'] in ['c_user', 'xs'] else "✅ Normal"
                            self.log_signal.emit(f"{cookie_type} Cookie {i+1} işlendi: {clean_cookie['name']} (domain: {domain})")
                        else:
                            self.log_signal.emit(f"⚠️ Cookie {i+1} Facebook'a ait değil, atlandı: {clean_cookie['name']} (domain: {domain})")
                    else:
                        self.log_signal.emit(f"⚠️ Cookie {i+1} boş veya geçersiz")
                        
                except Exception as cookie_error:
                    self.log_signal.emit(f"❌ Cookie {i+1} işleme hatası: {str(cookie_error)}")
                    # Debug için cookie objesinin string representation'ını göster
                    try:
                        cookie_str = str(cookie)[:200]
                        self.log_signal.emit(f"🔍 Cookie debug: {cookie_str}")
                    except:
                        self.log_signal.emit("🔍 Cookie debug yapılamadı")
                    continue
            
            with open(cookie_filename, 'w', encoding='utf-8') as f:
                json.dump(clean_cookies, f, indent=2, ensure_ascii=False)
            
            self.log_signal.emit(f"✅ {len(clean_cookies)} cookie kaydedildi: {cookie_filename}")
            self.cookies_saved = True
            
        except Exception as e:
            self.log_signal.emit(f"❌ Cookie kaydetme hatası: {str(e)}")
    
    def parse_js_cookies(self, cookie_string):
        """JavaScript cookie string'ini parse et"""
        cookies = []
        if not cookie_string:
            return cookies
            
        try:
            cookie_pairs = cookie_string.split(';')
            for pair in cookie_pairs:
                if '=' in pair:
                    name, value = pair.strip().split('=', 1)
                    cookie = {
                        'name': name.strip(),
                        'value': value.strip(),
                        'domain': '.facebook.com',
                        'path': '/',
                        'secure': True,
                        'httpOnly': False,
                        'sameSite': 'Lax'
                    }
                    cookies.append(cookie)
        except Exception as e:
            self.log_signal.emit(f"⚠️ Cookie parse hatası: {str(e)}")
            
        return cookies
    
    def debug_page_info(self, sb):
        """Sayfa bilgilerini debug için logla"""
        try:
            current_url = sb.cdp.get_current_url()
            page_title = sb.cdp.get_title()
            self.log_signal.emit(f"🔍 Mevcut URL: {current_url}")
            self.log_signal.emit(f"🔍 Sayfa başlığı: {page_title}")
        except Exception as e:
            self.log_signal.emit(f"⚠️ Debug bilgisi alınamadı: {str(e)}")
            
    def collect_facebook_groups(self, sb):
        """Facebook gruplarını topla"""
        try:
            self.log_signal.emit("🔍 Facebook grupları toplanıyor...")
            
            # Gruplar sayfasına git
            groups_url = "https://www.facebook.com/groups/joins/?nav_source=tab&ordering=viewer_added"
            self.log_signal.emit(f"🌐 Gruplar sayfasına gidiliyor: {groups_url}")
            sb.cdp.get(groups_url)
            
            # Sayfanın yüklenmesini bekle
            sb.sleep(random.uniform(3, 5))
            self.log_signal.emit("⏳ Sayfa yükleniyor...")
            
            collected_groups = []
            scroll_count = 0
            max_scrolls = 20  # Maksimum scroll sayısı
            
            while scroll_count < max_scrolls:
                self.log_signal.emit(f"📜 Scroll {scroll_count + 1}/{max_scrolls}")
                
                # Mevcut grup linklerini topla
                try:
                    # "Grubu gör" linklerini ve grup isimlerini bul
                    group_data = sb.cdp.evaluate("""
                        (function() {
                            var groups = [];
                            
                            // Grup container'larını bul
                            var groupContainers = document.querySelectorAll('div[class*="x1jx94hy"]');
                            
                            groupContainers.forEach(function(container) {
                                try {
                                    // "Grubu gör" linkini bul
                                    var viewGroupLink = container.querySelector('a[aria-label="Grubu gör"]');
                                    if (!viewGroupLink) return;
                                    
                                    var href = viewGroupLink.getAttribute('href');
                                    if (!href || !href.includes('/groups/')) return;
                                    
                                    // Tam URL'ye çevir
                                    if (href.startsWith('/')) {
                                        href = 'https://www.facebook.com' + href;
                                    }
                                    
                                    // Grup ismini bul - farklı yöntemler dene
                                    var groupName = '';
                                    
                                    // Yöntem 1: aria-label'dan al
                                    var svgElement = container.querySelector('svg[aria-label]');
                                    if (svgElement && svgElement.getAttribute('aria-label')) {
                                        groupName = svgElement.getAttribute('aria-label');
                                    }
                                    
                                    // Yöntem 2: Link text'inden al
                                    if (!groupName) {
                                        var nameLinks = container.querySelectorAll('a[href*="/groups/"]');
                                        nameLinks.forEach(function(link) {
                                            var text = link.textContent.trim();
                                            if (text && text !== 'Grubu gör' && text.length > 0 && text.length < 100) {
                                                groupName = text;
                                            }
                                        });
                                    }
                                    
                                    // Yöntem 3: Span içindeki text'i al
                                    if (!groupName) {
                                        var spans = container.querySelectorAll('span');
                                        spans.forEach(function(span) {
                                            var text = span.textContent.trim();
                                            if (text && text !== 'Grubu gör' && text.length > 2 && text.length < 100 && 
                                                !text.includes('saat önce') && !text.includes('gün önce') && 
                                                !text.includes('En son') && !text.includes('ziyaret')) {
                                                if (!groupName || text.length > groupName.length) {
                                                    groupName = text;
                                                }
                                            }
                                        });
                                    }
                                    
                                    // Grup ismini temizle
                                    if (groupName) {
                                        groupName = groupName.replace(/\s+/g, ' ').trim();
                                        // Çok uzun isimleri kısalt
                                        if (groupName.length > 80) {
                                            groupName = groupName.substring(0, 77) + '...';
                                        }
                                    }
                                    
                                    // Grup bilgilerini ekle
                                    if (groupName && href) {
                                        groups.push({
                                            name: groupName,
                                            url: href
                                        });
                                    }
                                    
                                } catch (e) {
                                    console.log('Grup parse hatası:', e);
                                }
                            });
                            
                            return groups;
                        })()
                    """)
                    
                    # Yeni grupları ekle
                    new_groups = 0
                    for group in group_data:
                        # Aynı URL'ye sahip grup var mı kontrol et
                        existing = False
                        for existing_group in collected_groups:
                            if existing_group['url'] == group['url']:
                                existing = True
                                break
                        
                        if not existing:
                            collected_groups.append(group)
                            new_groups += 1
                            self.log_signal.emit(f"✅ Yeni grup bulundu: {group['name']} - {group['url']}")
                    
                    self.log_signal.emit(f"📊 Bu scroll'da {new_groups} yeni grup, toplam: {len(collected_groups)}")
                    
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Link toplama hatası: {str(e)}")
                
                # Sayfayı aşağı kaydır
                try:
                    sb.cdp.evaluate("window.scrollBy(0, 800);")
                    sb.sleep(random.uniform(2, 4))  # Scroll delay
                    
                    # Sayfanın sonuna gelip gelmediğini kontrol et
                    scroll_position = sb.cdp.evaluate("""
                        (function() {
                            return {
                                scrollTop: window.pageYOffset,
                                scrollHeight: document.body.scrollHeight,
                                clientHeight: window.innerHeight
                            };
                        })()
                    """)
                    
                    # Sayfanın sonuna yaklaştıysak dur
                    if scroll_position['scrollTop'] + scroll_position['clientHeight'] >= scroll_position['scrollHeight'] - 100:
                        self.log_signal.emit("📄 Sayfa sonuna ulaşıldı")
                        break
                        
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Scroll hatası: {str(e)}")
                
                scroll_count += 1
                
                # Progress güncelle
                progress = 85 + int((scroll_count / max_scrolls) * 10)
                self.progress_signal.emit(min(progress, 95))
            
            self.log_signal.emit(f"🎉 Grup toplama tamamlandı! Toplam {len(collected_groups)} grup bulundu")
            
            # Grupları sinyal ile gönder
            self.groups_signal.emit(collected_groups)
            
            return collected_groups
            
        except Exception as e:
            self.log_signal.emit(f"❌ Grup toplama hatası: {str(e)}")
            return []
            # Sayfadaki form elementlerini kontrol et
            form_elements = [
                'input[name="email"]',
                'input[name="pass"]', 
                'button[name="login"]',
                'form#login_form',
                'div#login_form'
            ]
            
            for element in form_elements:
                try:
                    if sb.cdp.is_element_visible(element):
                        self.log_signal.emit(f"✅ Element bulundu: {element}")
                    else:
                        self.log_signal.emit(f"❌ Element bulunamadı: {element}")
                except:
                    self.log_signal.emit(f"❓ Element kontrol edilemedi: {element}")
                    
        except Exception as e:
            self.log_signal.emit(f"🔍 Debug bilgisi alınamadı: {str(e)}")


class FacebookLoginGUI(QMainWindow):
    """Ana GUI sınıfı"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.login_thread = None
        self.collected_groups = []  # Toplanan grupları saklamak için
        self.selected_groups = []  # Seçili grupları saklamak için
        self.current_cookie_id = None  # Mevcut cookie ID'si
        self.selected_image_path = None  # Seçili resim dosyası
        self.sharing_thread = None  # Paylaşım thread'i
        
    def init_ui(self):
        """Kullanıcı arayüzünü başlat"""
        self.setWindowTitle("Facebook Login Tool - SeleniumBase CDP Mode")
        self.setGeometry(100, 100, 800, 600)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QVBoxLayout(central_widget)
        
        # Başlık
        title_label = QLabel("🔐 Facebook Giriş Sistemi")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Email/Şifre tab'ı
        self.create_credentials_tab()
        
        # Cookie tab'ı
        self.create_cookie_tab()
        
        # Grup listesi tab'ı
        self.create_groups_tab()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Log alanı
        log_group = QGroupBox("📋 İşlem Logları")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log_text)
        
        # Log temizle butonu
        clear_log_btn = QPushButton("🗑️ Logları Temizle")
        clear_log_btn.clicked.connect(self.clear_logs)
        log_layout.addWidget(clear_log_btn)
        
        main_layout.addWidget(log_group)
        
        # Durum çubuğu
        self.statusBar().showMessage("Hazır")
        
    def create_credentials_tab(self):
        """Email/Şifre giriş tab'ını oluştur"""
        credentials_widget = QWidget()
        layout = QVBoxLayout(credentials_widget)
        
        # Giriş formu
        form_group = QGroupBox("📧 Email ve Şifre ile Giriş")
        form_layout = QVBoxLayout(form_group)
        
        # Email
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("ornek@email.com")
        email_layout.addWidget(self.email_input)
        form_layout.addLayout(email_layout)
        
        # Şifre
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Şifre:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Şifrenizi girin")
        password_layout.addWidget(self.password_input)
        form_layout.addLayout(password_layout)
        
        # Şifreyi göster checkbox
        self.show_password_cb = QCheckBox("Şifreyi göster")
        self.show_password_cb.toggled.connect(self.toggle_password_visibility)
        form_layout.addWidget(self.show_password_cb)
        
        # Bekleme süresi ayarı
        wait_layout = QHBoxLayout()
        wait_layout.addWidget(QLabel("Bekleme Süresi:"))
        self.wait_time_input = QLineEdit("15")
        self.wait_time_input.setMaximumWidth(50)
        self.wait_time_input.setPlaceholderText("15")
        wait_layout.addWidget(self.wait_time_input)
        wait_layout.addWidget(QLabel("saniye"))
        wait_layout.addStretch()
        form_layout.addLayout(wait_layout)
        
        # Grup toplama checkbox'ı
        self.collect_groups_cb = QCheckBox("🔍 Giriş sonrası Facebook gruplarını topla")
        self.collect_groups_cb.setChecked(True)  # Varsayılan olarak aktif
        form_layout.addWidget(self.collect_groups_cb)
        
        # Manuel doğrulama bilgisi
        manual_info = QLabel("ℹ️ Giriş sonrası 2FA/CAPTCHA/Güvenlik kontrolü için yukarıdaki süre kadar beklenecektir.")
        manual_info.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        manual_info.setWordWrap(True)
        form_layout.addWidget(manual_info)
        
        # Giriş butonu
        self.login_btn = QPushButton("🚀 Facebook'a Giriş Yap")
        self.login_btn.clicked.connect(self.login_with_credentials)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #1877f2;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #166fe5;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        form_layout.addWidget(self.login_btn)
        
        layout.addWidget(form_group)
        layout.addStretch()
        
        self.tab_widget.addTab(credentials_widget, "📧 Email/Şifre Girişi")
    
    def create_cookie_tab(self):
        """Cookie giriş tab'ını oluştur"""
        cookie_widget = QWidget()
        layout = QVBoxLayout(cookie_widget)
        
        # Cookie giriş formu
        cookie_group = QGroupBox("🍪 Cookie Dosyası ile Giriş")
        cookie_layout = QVBoxLayout(cookie_group)
        
        # Dosya seçimi
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Cookie Dosyası:"))
        self.cookie_file_input = QLineEdit()
        self.cookie_file_input.setPlaceholderText("Cookie dosyası seçin...")
        self.cookie_file_input.setReadOnly(True)
        file_layout.addWidget(self.cookie_file_input)
        
        self.browse_btn = QPushButton("📁 Dosya Seç")
        self.browse_btn.clicked.connect(self.browse_cookie_file)
        file_layout.addWidget(self.browse_btn)
        cookie_layout.addLayout(file_layout)
        
        # Grup toplama checkbox'ı (cookie için)
        self.collect_groups_cookie_cb = QCheckBox("🔍 Giriş sonrası Facebook gruplarını topla")
        self.collect_groups_cookie_cb.setChecked(True)  # Varsayılan olarak aktif
        cookie_layout.addWidget(self.collect_groups_cookie_cb)
        
        # Cookie giriş butonu
        self.cookie_login_btn = QPushButton("🍪 Cookie ile Giriş Yap")
        self.cookie_login_btn.clicked.connect(self.login_with_cookies)
        self.cookie_login_btn.setStyleSheet("""
            QPushButton {
                background-color: #42b883;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #369870;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        cookie_layout.addWidget(self.cookie_login_btn)
        
        layout.addWidget(cookie_group)
        
        # Cookie dosyaları listesi
        cookie_list_group = QGroupBox("📂 Mevcut Cookie Dosyaları")
        cookie_list_layout = QVBoxLayout(cookie_list_group)
        
        self.refresh_cookie_list_btn = QPushButton("🔄 Listeyi Yenile")
        self.refresh_cookie_list_btn.clicked.connect(self.refresh_cookie_list)
        cookie_list_layout.addWidget(self.refresh_cookie_list_btn)
        
        self.cookie_list_text = QTextEdit()
        self.cookie_list_text.setMaximumHeight(150)
        self.cookie_list_text.setReadOnly(True)
        cookie_list_layout.addWidget(self.cookie_list_text)
        
        layout.addWidget(cookie_list_group)
        layout.addStretch()
        
        self.tab_widget.addTab(cookie_widget, "🍪 Cookie Girişi")
        
        # İlk yüklemede cookie listesini yenile
        self.refresh_cookie_list()
    
    def create_groups_tab(self):
        """Grup listesi tab'ını oluştur"""
        groups_widget = QWidget()
        layout = QVBoxLayout(groups_widget)
        
        # Bilgi etiketi
        info_label = QLabel("ℹ️ Giriş yaptıktan sonra toplanan gruplar burada görünecektir. Grupları seçerek favori listenize ekleyebilirsiniz.")
        info_label.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Splitter ile iki bölüm oluştur
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Sol bölüm - Toplanan Gruplar
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Toplanan gruplar başlığı
        collected_group = QGroupBox("📋 Toplanan Gruplar")
        collected_layout = QVBoxLayout(collected_group)
        
        # Grup sayısı etiketi
        self.groups_count_label = QLabel("📊 Toplam grup sayısı: 0")
        self.groups_count_label.setStyleSheet("font-weight: bold; color: #1877f2;")
        collected_layout.addWidget(self.groups_count_label)
        
        # Toplanan gruplar listesi
        self.groups_list_widget = QListWidget()
        self.groups_list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.groups_list_widget.itemDoubleClicked.connect(self.add_to_selected)
        collected_layout.addWidget(self.groups_list_widget)
        
        # Toplanan gruplar butonları
        collected_buttons_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("✅ Tümünü Seç")
        self.select_all_btn.clicked.connect(self.select_all_groups)
        self.select_all_btn.setEnabled(False)
        collected_buttons_layout.addWidget(self.select_all_btn)
        
        self.add_selected_btn = QPushButton("➡️ Seçilenleri Ekle")
        self.add_selected_btn.clicked.connect(self.add_selected_to_favorites)
        self.add_selected_btn.setEnabled(False)
        collected_buttons_layout.addWidget(self.add_selected_btn)
        
        collected_buttons_layout.addStretch()
        collected_layout.addLayout(collected_buttons_layout)
        
        left_layout.addWidget(collected_group)
        splitter.addWidget(left_widget)
        
        # Sağ bölüm - Seçili Gruplar
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Seçili gruplar başlığı
        selected_group = QGroupBox("⭐ Seçili Gruplar (Cookie'ye Özel)")
        selected_layout = QVBoxLayout(selected_group)
        
        # Seçili grup sayısı etiketi
        self.selected_count_label = QLabel("📊 Seçili grup sayısı: 0")
        self.selected_count_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        selected_layout.addWidget(self.selected_count_label)
        
        # Cookie bilgisi etiketi
        self.cookie_info_label = QLabel("🍪 Cookie ID: Henüz giriş yapılmadı")
        self.cookie_info_label.setStyleSheet("color: #666; font-size: 10px;")
        selected_layout.addWidget(self.cookie_info_label)
        
        # Seçili gruplar listesi
        self.selected_groups_widget = QListWidget()
        self.selected_groups_widget.itemDoubleClicked.connect(self.remove_from_selected)
        selected_layout.addWidget(self.selected_groups_widget)
        
        # Seçili gruplar butonları
        selected_buttons_layout = QHBoxLayout()
        
        self.remove_selected_btn = QPushButton("❌ Seçileni Kaldır")
        self.remove_selected_btn.clicked.connect(self.remove_selected_from_favorites)
        self.remove_selected_btn.setEnabled(False)
        selected_buttons_layout.addWidget(self.remove_selected_btn)
        
        self.clear_selected_btn = QPushButton("🗑️ Tümünü Temizle")
        self.clear_selected_btn.clicked.connect(self.clear_selected_groups)
        self.clear_selected_btn.setEnabled(False)
        selected_buttons_layout.addWidget(self.clear_selected_btn)
        
        selected_buttons_layout.addStretch()
        selected_layout.addLayout(selected_buttons_layout)
        
        right_layout.addWidget(selected_group)
        splitter.addWidget(right_widget)
        
        # Splitter oranlarını ayarla
        splitter.setSizes([400, 400])
        
        # Paylaşım bölümü
        self.create_sharing_section(layout)
        
        # Alt butonlar
        bottom_buttons_layout = QHBoxLayout()
        
        # Listeyi temizle butonu
        self.clear_groups_btn = QPushButton("🗑️ Toplanan Grupları Temizle")
        self.clear_groups_btn.clicked.connect(self.clear_groups_list)
        self.clear_groups_btn.setEnabled(False)
        bottom_buttons_layout.addWidget(self.clear_groups_btn)
        
        # Dosyaya kaydet butonu
        self.save_groups_btn = QPushButton("💾 Seçili Grupları Kaydet")
        self.save_groups_btn.clicked.connect(self.save_groups_to_file)
        self.save_groups_btn.setEnabled(False)
        bottom_buttons_layout.addWidget(self.save_groups_btn)
        
        # Panoya kopyala butonu
        self.copy_groups_btn = QPushButton("📋 Seçili Grupları Kopyala")
        self.copy_groups_btn.clicked.connect(self.copy_groups_to_clipboard)
        self.copy_groups_btn.setEnabled(False)
        bottom_buttons_layout.addWidget(self.copy_groups_btn)
        
        # Seçili grupları yükle butonu
        self.load_selected_btn = QPushButton("📂 Seçili Grupları Yükle")
        self.load_selected_btn.clicked.connect(self.load_selected_groups)
        self.load_selected_btn.setEnabled(False)
        bottom_buttons_layout.addWidget(self.load_selected_btn)
        
        bottom_buttons_layout.addStretch()
        layout.addLayout(bottom_buttons_layout)
        
        self.tab_widget.addTab(groups_widget, "🔍 Grup Yönetimi")
    
    def create_sharing_section(self, parent_layout):
        """Paylaşım bölümünü oluştur"""
        sharing_group = QGroupBox("📢 Grup Paylaşımı")
        sharing_layout = QVBoxLayout(sharing_group)
        
        # Paylaşım metni
        text_layout = QVBoxLayout()
        text_layout.addWidget(QLabel("📝 Paylaşım Metni:"))
        
        self.sharing_text = QTextEdit()
        self.sharing_text.setMaximumHeight(100)
        self.sharing_text.setPlaceholderText("Gruplarda paylaşmak istediğiniz metni buraya yazın...")
        text_layout.addWidget(self.sharing_text)
        
        sharing_layout.addLayout(text_layout)
        
        # Resim ekleme bölümü
        image_layout = QHBoxLayout()
        image_layout.addWidget(QLabel("🖼️ Resim:"))
        
        self.image_path_label = QLabel("Henüz resim seçilmedi")
        self.image_path_label.setStyleSheet("color: #666; font-style: italic;")
        image_layout.addWidget(self.image_path_label)
        
        self.select_image_btn = QPushButton("📁 Resim Seç")
        self.select_image_btn.clicked.connect(self.select_image)
        image_layout.addWidget(self.select_image_btn)
        
        self.clear_image_btn = QPushButton("❌ Resmi Kaldır")
        self.clear_image_btn.clicked.connect(self.clear_image)
        self.clear_image_btn.setEnabled(False)
        image_layout.addWidget(self.clear_image_btn)
        
        image_layout.addStretch()
        sharing_layout.addLayout(image_layout)
        
        # Paylaşım ayarları
        settings_layout = QHBoxLayout()
        
        settings_layout.addWidget(QLabel("⏱️ Gruplar arası bekleme süresi:"))
        
        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setMinimum(10)
        self.delay_spinbox.setMaximum(300)
        self.delay_spinbox.setValue(30)
        self.delay_spinbox.setSuffix(" saniye")
        settings_layout.addWidget(self.delay_spinbox)
        
        settings_layout.addStretch()
        
        # Paylaş butonu
        self.share_to_groups_btn = QPushButton("🚀 Seçili Gruplarda Paylaş")
        self.share_to_groups_btn.clicked.connect(self.start_sharing)
        self.share_to_groups_btn.setEnabled(False)
        self.share_to_groups_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        settings_layout.addWidget(self.share_to_groups_btn)
        
        sharing_layout.addLayout(settings_layout)
        
        # Paylaşım durumu
        self.sharing_status_label = QLabel("📊 Paylaşım durumu: Hazır")
        self.sharing_status_label.setStyleSheet("color: #666; font-size: 11px;")
        sharing_layout.addWidget(self.sharing_status_label)
        
        # Progress bar
        self.sharing_progress = QProgressBar()
        self.sharing_progress.setVisible(False)
        sharing_layout.addWidget(self.sharing_progress)
        
        parent_layout.addWidget(sharing_group)
    
    def toggle_password_visibility(self, checked):
        """Şifre görünürlüğünü değiştir"""
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
    
    def browse_cookie_file(self):
        """Cookie dosyası seç"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Cookie Dosyası Seç", 
            "", 
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            self.cookie_file_input.setText(file_path)
    
    def refresh_cookie_list(self):
        """Mevcut cookie dosyalarını listele"""
        cookie_files = [f for f in os.listdir('.') if f.startswith('facebook_cookies_') and f.endswith('.json')]
        
        if cookie_files:
            cookie_list = "Mevcut cookie dosyaları:\n\n"
            for i, file in enumerate(cookie_files, 1):
                # Dosya tarihini al
                try:
                    timestamp = int(file.split('_')[-1].split('.')[0])
                    date_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
                    cookie_list += f"{i}. {file} ({date_str})\n"
                except:
                    cookie_list += f"{i}. {file}\n"
        else:
            cookie_list = "Henüz kaydedilmiş cookie dosyası yok.\nİlk önce email/şifre ile giriş yaparak cookie oluşturun."
        
        self.cookie_list_text.setText(cookie_list)
    
    def login_with_credentials(self):
        """Email ve şifre ile giriş başlat"""
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        
        if not email or not password:
            QMessageBox.warning(self, "Uyarı", "Lütfen email ve şifre alanlarını doldurun!")
            return
        
        self.start_login_process("credentials", email=email, password=password)
    
    def login_with_cookies(self):
        """Cookie ile giriş başlat"""
        cookie_file = self.cookie_file_input.text().strip()
        
        if not cookie_file:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir cookie dosyası seçin!")
            return
        
        if not os.path.exists(cookie_file):
            QMessageBox.warning(self, "Uyarı", "Seçilen cookie dosyası bulunamadı!")
            return
        
        self.start_login_process("cookies", cookie_file=cookie_file)
    
    def start_login_process(self, login_type, **kwargs):
        """Giriş işlemini başlat"""
        # Butonları devre dışı bırak
        self.login_btn.setEnabled(False)
        self.cookie_login_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)
        
        # Progress bar'ı göster
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Grup toplama seçeneğini kontrol et
        collect_groups = False
        if login_type == "credentials":
            collect_groups = self.collect_groups_cb.isChecked()
        elif login_type == "cookies":
            collect_groups = self.collect_groups_cookie_cb.isChecked()
        
        # Bekleme süresini al
        try:
            wait_time = int(self.wait_time_input.text().strip())
            if wait_time < 5:
                wait_time = 5  # Minimum 5 saniye
            elif wait_time > 60:
                wait_time = 60  # Maksimum 60 saniye
        except:
            wait_time = 15  # Varsayılan 15 saniye
        
        kwargs['wait_time'] = wait_time
        kwargs['collect_groups'] = collect_groups
        
        # Thread'i başlat
        self.login_thread = FacebookLoginThread(login_type, **kwargs)
        self.login_thread.log_signal.connect(self.add_log)
        self.login_thread.progress_signal.connect(self.update_progress)
        self.login_thread.finished_signal.connect(self.login_finished)
        self.login_thread.groups_signal.connect(self.update_groups_list)
        self.login_thread.start()
        
        self.statusBar().showMessage("Giriş işlemi devam ediyor...")
    
    def add_log(self, message):
        """Log mesajı ekle"""
        timestamp = time.strftime('%H:%M:%S')
        self.log_text.append(f"[{timestamp}] {message}")
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def update_progress(self, value):
        """Progress bar'ı güncelle"""
        self.progress_bar.setValue(value)
    
    def login_finished(self, success, message):
        """Giriş işlemi tamamlandı"""
        # Butonları tekrar aktif et
        self.login_btn.setEnabled(True)
        self.cookie_login_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
        
        # Progress bar'ı gizle
        self.progress_bar.setVisible(False)
        
        if success:
            # Cookie ID'sini ayarla
            self.current_cookie_id = self.get_cookie_id()
            if self.current_cookie_id:
                self.cookie_info_label.setText(f"🍪 Cookie ID: {self.current_cookie_id}")
                self.load_selected_btn.setEnabled(True)
                # Seçili grupları yükle
                self.load_selected_groups_for_cookie()
            
            QMessageBox.information(self, "Başarılı", message)
            self.statusBar().showMessage("Giriş başarılı!")
            # Cookie listesini yenile
            self.refresh_cookie_list()
        else:
            QMessageBox.critical(self, "Hata", message)
            self.statusBar().showMessage("Giriş başarısız!")
        
        self.add_log(f"🏁 İşlem tamamlandı: {message}")
    
    def clear_logs(self):
        """Logları temizle"""
        self.log_text.clear()
        self.add_log("📋 Loglar temizlendi")
    
    def update_groups_list(self, groups):
        """Grup listesini güncelle"""
        self.collected_groups = groups
        
        # Grup sayısını güncelle
        self.groups_count_label.setText(f"📊 Toplam grup sayısı: {len(groups)}")
        
        # Grup listesini güncelle
        self.groups_list_widget.clear()
        if groups:
            for group in groups:
                item = QListWidgetItem(f"{group['name']}")
                item.setData(Qt.UserRole, group)  # Grup verisini item'a ekle
                item.setToolTip(f"Grup: {group['name']}\nURL: {group['url']}")
                self.groups_list_widget.addItem(item)
            
            # Butonları aktif et
            self.clear_groups_btn.setEnabled(True)
            self.select_all_btn.setEnabled(True)
            self.add_selected_btn.setEnabled(True)
            
            # Grup listesi tab'ına geç
            self.tab_widget.setCurrentIndex(2)  # Grup listesi tab'ı (3. tab)
            
            self.add_log(f"✅ {len(groups)} grup listesi güncellendi")
        else:
            self.add_log("⚠️ Hiç grup bulunamadı")
        
        # Seçili grupları yükle (eğer cookie ID varsa)
        if self.current_cookie_id:
            self.load_selected_groups_for_cookie()
    
    def clear_groups_list(self):
        """Toplanan grup listesini temizle"""
        self.collected_groups = []
        self.groups_list_widget.clear()
        self.groups_count_label.setText("📊 Toplam grup sayısı: 0")
        
        # Butonları devre dışı bırak
        self.clear_groups_btn.setEnabled(False)
        self.select_all_btn.setEnabled(False)
        self.add_selected_btn.setEnabled(False)
        
        self.add_log("🗑️ Toplanan grup listesi temizlendi")
    
    def select_all_groups(self):
        """Tüm grupları seç"""
        for i in range(self.groups_list_widget.count()):
            item = self.groups_list_widget.item(i)
            item.setSelected(True)
        self.add_log("✅ Tüm gruplar seçildi")
    
    def add_to_selected(self, item):
        """Çift tıklanan grubu seçili gruplara ekle"""
        group_data = item.data(Qt.UserRole)
        if group_data and group_data not in self.selected_groups:
            self.selected_groups.append(group_data)
            self.update_selected_groups_display()
            self.save_selected_groups_for_cookie()
            self.add_log(f"⭐ Grup seçili listeye eklendi: {group_data['name']}")
    
    def add_selected_to_favorites(self):
        """Seçili grupları favori listeye ekle"""
        selected_items = self.groups_list_widget.selectedItems()
        added_count = 0
        
        for item in selected_items:
            group_data = item.data(Qt.UserRole)
            if group_data and group_data not in self.selected_groups:
                self.selected_groups.append(group_data)
                added_count += 1
        
        if added_count > 0:
            self.update_selected_groups_display()
            self.save_selected_groups_for_cookie()
            self.add_log(f"⭐ {added_count} grup seçili listeye eklendi")
        else:
            self.add_log("⚠️ Seçili gruplar zaten listede mevcut")
    
    def remove_from_selected(self, item):
        """Çift tıklanan grubu seçili gruplardan kaldır"""
        group_name = item.text()
        # Grup adına göre bul ve kaldır
        for group in self.selected_groups[:]:  # Kopya üzerinde iterate et
            if group['name'] == group_name:
                self.selected_groups.remove(group)
                self.update_selected_groups_display()
                self.save_selected_groups_for_cookie()
                self.add_log(f"❌ Grup seçili listeden kaldırıldı: {group_name}")
                break
    
    def remove_selected_from_favorites(self):
        """Seçili grubu favori listeden kaldır"""
        current_item = self.selected_groups_widget.currentItem()
        if current_item:
            group_name = current_item.text()
            for group in self.selected_groups[:]:
                if group['name'] == group_name:
                    self.selected_groups.remove(group)
                    self.update_selected_groups_display()
                    self.save_selected_groups_for_cookie()
                    self.add_log(f"❌ Grup seçili listeden kaldırıldı: {group_name}")
                    break
    
    def clear_selected_groups(self):
        """Tüm seçili grupları temizle"""
        self.selected_groups = []
        self.update_selected_groups_display()
        self.save_selected_groups_for_cookie()
        self.add_log("🗑️ Seçili gruplar temizlendi")
    
    def update_selected_groups_display(self):
        """Seçili gruplar görünümünü güncelle"""
        self.selected_groups_widget.clear()
        self.selected_count_label.setText(f"📊 Seçili grup sayısı: {len(self.selected_groups)}")
        
        for group in self.selected_groups:
            item = QListWidgetItem(group['name'])
            item.setToolTip(f"Grup: {group['name']}\nURL: {group['url']}")
            self.selected_groups_widget.addItem(item)
        
        # Butonları güncelle
        has_selected = len(self.selected_groups) > 0
        self.remove_selected_btn.setEnabled(has_selected)
        self.clear_selected_btn.setEnabled(has_selected)
        self.save_groups_btn.setEnabled(has_selected)
        self.copy_groups_btn.setEnabled(has_selected)
        self.share_to_groups_btn.setEnabled(has_selected)
    
    def get_cookie_id(self):
        """Mevcut cookie'den benzersiz ID oluştur"""
        try:
            # En son cookie dosyasını bul
            cookie_files = [f for f in os.listdir('.') if f.startswith('facebook_cookies_') and f.endswith('.json')]
            if not cookie_files:
                return None
            
            latest_cookie = max(cookie_files, key=lambda x: os.path.getctime(x))
            
            with open(latest_cookie, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            # c_user cookie'sinden ID al
            for cookie in cookies:
                if isinstance(cookie, dict) and cookie.get('name') == 'c_user':
                    return cookie.get('value', 'unknown')
            
            return 'unknown'
        except:
            return None
    
    def save_selected_groups_for_cookie(self):
        """Seçili grupları cookie'ye özel dosyaya kaydet"""
        if not self.current_cookie_id:
            return
        
        try:
            filename = f"selected_groups_{self.current_cookie_id}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.selected_groups, f, indent=2, ensure_ascii=False)
            
            self.add_log(f"💾 Seçili gruplar kaydedildi: {filename}")
        except Exception as e:
            self.add_log(f"❌ Seçili grup kaydetme hatası: {str(e)}")
    
    def load_selected_groups_for_cookie(self):
        """Cookie'ye özel seçili grupları yükle"""
        if not self.current_cookie_id:
            return
        
        try:
            filename = f"selected_groups_{self.current_cookie_id}.json"
            
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    self.selected_groups = json.load(f)
                
                self.update_selected_groups_display()
                self.cookie_info_label.setText(f"🍪 Cookie ID: {self.current_cookie_id} (Seçili gruplar yüklendi)")
                self.add_log(f"📂 Seçili gruplar yüklendi: {len(self.selected_groups)} grup")
            else:
                self.selected_groups = []
                self.update_selected_groups_display()
                self.cookie_info_label.setText(f"🍪 Cookie ID: {self.current_cookie_id} (Yeni profil)")
        except Exception as e:
            self.add_log(f"❌ Seçili grup yükleme hatası: {str(e)}")
    
    def load_selected_groups(self):
        """Manuel olarak seçili grupları yükle"""
        if not self.current_cookie_id:
            QMessageBox.warning(self, "Uyarı", "Önce giriş yapmanız gerekiyor!")
            return
        
        self.load_selected_groups_for_cookie()
    
    def select_image(self):
        """Paylaşım için resim seç"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Paylaşım Resmi Seç", 
            "", 
            "Resim Dosyaları (*.png *.jpg *.jpeg *.gif *.bmp);;Tüm Dosyalar (*)"
        )
        
        if file_path:
            self.selected_image_path = file_path
            # Dosya adını kısalt
            filename = os.path.basename(file_path)
            if len(filename) > 30:
                filename = filename[:27] + "..."
            
            self.image_path_label.setText(f"✅ {filename}")
            self.image_path_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            self.clear_image_btn.setEnabled(True)
            self.add_log(f"🖼️ Resim seçildi: {file_path}")
    
    def clear_image(self):
        """Seçili resmi kaldır"""
        self.selected_image_path = None
        self.image_path_label.setText("Henüz resim seçilmedi")
        self.image_path_label.setStyleSheet("color: #666; font-style: italic;")
        self.clear_image_btn.setEnabled(False)
        self.add_log("❌ Resim kaldırıldı")
    
    def start_sharing(self):
        """Grup paylaşımını başlat"""
        # Kontroller
        if not self.selected_groups:
            QMessageBox.warning(self, "Uyarı", "Paylaşım yapılacak grup seçilmedi!")
            return
        
        sharing_text = self.sharing_text.toPlainText().strip()
        if not sharing_text and not self.selected_image_path:
            QMessageBox.warning(self, "Uyarı", "Paylaşım metni veya resim eklemelisiniz!")
            return
        
        if not self.login_thread or not hasattr(self.login_thread, 'sb_instance') or not self.login_thread.sb_instance:
            QMessageBox.warning(self, "Uyarı", "Önce Facebook'a giriş yapmalısınız ve tarayıcı açık olmalıdır!")
            return
        
        # Onay al
        reply = QMessageBox.question(
            self, 
            "Paylaşım Onayı", 
            f"Seçili {len(self.selected_groups)} grupta paylaşım yapılacak.\n\n"
            f"Metin: {'Var' if sharing_text else 'Yok'}\n"
            f"Resim: {'Var' if self.selected_image_path else 'Yok'}\n"
            f"Bekleme süresi: {self.delay_spinbox.value()} saniye\n\n"
            f"Devam etmek istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Paylaşım thread'ini başlat
        self.sharing_thread = GroupSharingThread(
            sb_instance=self.login_thread.sb_instance,
            selected_groups=self.selected_groups.copy(),
            sharing_text=sharing_text,
            image_path=self.selected_image_path,
            delay_seconds=self.delay_spinbox.value()
        )
        
        # Sinyalleri bağla
        self.sharing_thread.log_signal.connect(self.add_log)
        self.sharing_thread.progress_signal.connect(self.update_sharing_progress)
        self.sharing_thread.status_signal.connect(self.update_sharing_status)
        self.sharing_thread.finished_signal.connect(self.sharing_finished)
        
        # UI'yi güncelle
        self.share_to_groups_btn.setEnabled(False)
        self.sharing_progress.setVisible(True)
        self.sharing_progress.setValue(0)
        self.sharing_progress.setMaximum(len(self.selected_groups))
        
        # Thread'i başlat
        self.sharing_thread.start()
        self.add_log(f"🚀 Grup paylaşımı başlatıldı: {len(self.selected_groups)} grup")
    
    def update_sharing_progress(self, value):
        """Paylaşım progress'ini güncelle"""
        self.sharing_progress.setValue(value)
    
    def update_sharing_status(self, status):
        """Paylaşım durumunu güncelle"""
        self.sharing_status_label.setText(f"📊 Paylaşım durumu: {status}")
    
    def sharing_finished(self, success, message):
        """Paylaşım tamamlandı"""
        self.share_to_groups_btn.setEnabled(True)
        self.sharing_progress.setVisible(False)
        
        if success:
            QMessageBox.information(self, "Başarılı", message)
            self.sharing_status_label.setText("📊 Paylaşım durumu: Tamamlandı ✅")
        else:
            QMessageBox.critical(self, "Hata", message)
            self.sharing_status_label.setText("📊 Paylaşım durumu: Hata ❌")
        
        self.add_log(f"🏁 Paylaşım tamamlandı: {message}")
    
    def save_groups_to_file(self):
        """Seçili grupları dosyaya kaydet"""
        if not self.selected_groups:
            QMessageBox.warning(self, "Uyarı", "Kaydedilecek seçili grup yok!")
            return
        
        try:
            # Dosya adı oluştur
            timestamp = int(time.time())
            cookie_suffix = f"_{self.current_cookie_id}" if self.current_cookie_id else ""
            filename = f"selected_facebook_groups{cookie_suffix}_{timestamp}.txt"
            
            # Dosyaya kaydet
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Seçili Facebook Grupları - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                if self.current_cookie_id:
                    f.write(f"Cookie ID: {self.current_cookie_id}\n")
                f.write(f"Toplam Seçili Grup Sayısı: {len(self.selected_groups)}\n")
                f.write("=" * 60 + "\n\n")
                
                for i, group in enumerate(self.selected_groups, 1):
                    f.write(f"{i}. {group['name']}\n")
                    f.write(f"   URL: {group['url']}\n\n")
            
            QMessageBox.information(self, "Başarılı", f"Seçili gruplar başarıyla kaydedildi:\n{filename}")
            self.add_log(f"💾 Seçili gruplar dosyaya kaydedildi: {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya kaydetme hatası:\n{str(e)}")
            self.add_log(f"❌ Dosya kaydetme hatası: {str(e)}")
    
    def copy_groups_to_clipboard(self):
        """Seçili grupları panoya kopyala"""
        if not self.selected_groups:
            QMessageBox.warning(self, "Uyarı", "Kopyalanacak seçili grup yok!")
            return
        
        try:
            # Clipboard'a kopyalanacak metni hazırla
            clipboard_text = f"Seçili Facebook Grupları - {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            if self.current_cookie_id:
                clipboard_text += f"Cookie ID: {self.current_cookie_id}\n"
            clipboard_text += f"Toplam Seçili Grup Sayısı: {len(self.selected_groups)}\n"
            clipboard_text += "=" * 60 + "\n\n"
            
            for i, group in enumerate(self.selected_groups, 1):
                clipboard_text += f"{i}. {group['name']}\n"
                clipboard_text += f"   URL: {group['url']}\n\n"
            
            # Panoya kopyala
            clipboard = QApplication.clipboard()
            clipboard.setText(clipboard_text)
            
            QMessageBox.information(self, "Başarılı", f"{len(self.selected_groups)} seçili grup panoya kopyalandı!")
            self.add_log(f"📋 {len(self.selected_groups)} seçili grup panoya kopyalandı")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Panoya kopyalama hatası:\n{str(e)}")
            self.add_log(f"❌ Panoya kopyalama hatası: {str(e)}")


def main():
    """Ana fonksiyon"""
    app = QApplication(sys.argv)
    
    # Uygulama ikonunu ayarla (varsa)
    app.setApplicationName("Facebook Login Tool")
    app.setApplicationVersion("1.0")
    
    # Ana pencereyi oluştur ve göster
    window = FacebookLoginGUI()
    window.show()
    
    # Uygulamayı çalıştır
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()