English Version
Overview: Web-Scrapers vs. Anti-Scrapers
The video provides a comprehensive overview of the ongoing battle between web scraping tools (Web-Scrapers) and the technologies designed to block them (Anti-Scrapers). The speaker, Michael Mintz, who is the creator of the SeleniumBase framework, discusses various tools, techniques for bypassing bot detection, and the legal landscape of web scraping.
Key Concepts Discussed
The Evolution of Bots: Initially, bots were easy to detect. However, modern bots and scraping tools have become sophisticated, making them difficult to distinguish from human users, much like the Cylons in Battlestar Galactica.
Web Scraping Tools (Web-Scrapers):
Commercial Tools:
Bright Data: A popular commercial service for web scraping, known for its powerful proxy networks and scraping tools. It was notably sued by Meta (Facebook) and X (Twitter) but won the cases, reaffirming the legality of scraping public data.
ZenRows: Another commercial web scraping tool.
Open-Source Stealth Frameworks (many with over 1,000 GitHub stars):
undetected-chromedriver: A custom Selenium Chromedriver designed to pass bot mitigation systems.
SeleniumBase: An all-in-one browser automation framework for testing, scraping, and bypassing bot detection, created by the speaker.
puppeteer-real-browser: A package designed to bypass Puppeteer's bot-detecting captchas.
botasaurus: A framework to build "undefeatable" scrapers.
DrissionPage: A Python-based web automation tool.
nodriver: The successor to undetected-chromedriver.
patchright: An undetected version of the Playwright testing library.
pydoll: A library for automating Chromium-based browsers without a WebDriver.
Scrapling: A Python library to make web scraping easier.
cloudscraper: A Python module specifically to bypass Cloudflare's anti-bot page.
Anti-Scraping Tools (Anti-Scrapers) and CAPTCHAs:
CAPTCHA Services:
reCAPTCHA (Google): Asks users to identify objects in images (e.g., stairs, buses).
hCaptcha: Often requires users to click on images containing a specific object (e.g., a winged animal).
Cloudflare Turnstile: A "Verify you are human" checkbox that is generally easier to bypass.
Brotector CAPTCHA: An open-source CAPTCHA system.
Invisible Anti-Bot Services:
PerimeterX
Imperva Incapsula
DataDome
Shape Security
Kasada
Akamai
Code Examples and Demonstrations using SeleniumBase
The speaker demonstrates how to use SeleniumBase to bypass anti-bot measures, particularly from Cloudflare.
Example 1: Bypassing Cloudflare's Initial Challenge Page (on GitLab)
This code shows how to bypass the "Verifying you are human" page that appears before the main content loads.
Code:
code
Python
from seleniumbase import SB

with SB(uc=True, test=True, locale="en") as sb:
    url = "https://gitlab.com/users/sign_in"
    sb.activate_cdp_mode(url)
    sb.uc_gui_click_captcha()
    sb.sleep(2)
Explanation:
from seleniumbase import SB: Imports the necessary SeleniumBase library.
with SB(uc=True, ...): Initializes SeleniumBase in UC Mode (uc=True), which uses the undetected-chromedriver patch to appear more human-like.
sb.activate_cdp_mode(url): Activates the Chrome DevTools Protocol (CDP) mode, which is a powerful way to interact with the browser and bypass many detection mechanisms.
sb.uc_gui_click_captcha(): This is a crucial function. If the automated bypass fails, it uses PyAutoGUI (created by Al Sweigart) to programmatically move the mouse and click the CAPTCHA checkbox, simulating human interaction.
Example 2: Bypassing an Embedded Cloudflare Turnstile (on PlanetMinecraft)
This example is for when the CAPTCHA is part of the login form itself, not a separate challenge page.
Code:
code
Python
from seleniumbase import SB

with SB(uc=True, test=True) as sb:
    url = "https://www.planetminecraft.com/account/sign_in/"
    sb.activate_cdp_mode(url)
    sb.sleep(2)
    sb.cdp.gui_click_element("#turnstile-widget div")
    sb.sleep(2)
Explanation:
sb.cdp.gui_click_element("#turnstile-widget div"): This method is used to click a specific element on the page. For Cloudflare Turnstiles, you need to target the parent selector that appears directly above the #shadow-root element in the page's HTML structure. This allows PyAutoGUI to find and click the correct widget.