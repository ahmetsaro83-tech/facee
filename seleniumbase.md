SeleniumBase
All-in-one Browser Automation Framework:
Web Crawling / Testing / Scraping / Stealth

PyPI version GitHub version SeleniumBase Docs SeleniumBase GitHub Actions 

🚀 Start | 🏰 Features | 🎛️ Options | 📚 Examples | 🌠 Scripts | 📱 Mobile
📘 APIs | 🔠 Formats | 🔴 Recorder | 📊 Dashboard | 🗾 Locales | 💻 Farm
🎖️ GUI | 📰 TestPage | 👤 UC Mode | 🐙 CDP Mode | 📶 Charts | 🌐 Grid
👁️ How | 🚝 Migrate | 🗂️ CasePlans | ♻️ Template | 🧬 Hybrid | 🚎 Tours
🤖 CI/CD | 🕹️ JSMgr | 🌏 Translator | 🎞️ Presenter | 🛂 Dialog | 🖼️ Visual

SeleniumBase is the professional toolkit for web automation activities. Built for testing websites, bypassing CAPTCHAs, enhancing productivity, completing tasks, and scaling your business.

📚 Learn from over 200 examples in the SeleniumBase/examples/ folder.

🐙 Note that UC Mode / CDP Mode (Stealth Mode) have their own ReadMe files.

ℹ️ Most scripts run with raw python, although some scripts use Syntax Formats that expect pytest (a Python unit-testing framework included with SeleniumBase that can discover, collect, and run tests automatically).

📗 Here's raw_google.py, which performs a Google search:

from seleniumbase import SB

with SB(test=True, uc=True) as sb:
    sb.open("https://google.com/ncr")
    sb.type('[title="Search"]', "SeleniumBase GitHub page\n")
    sb.click('[href*="github.com/seleniumbase/"]')
    sb.save_screenshot_to_logs()  # ./latest_logs/
    print(sb.get_page_title())
python raw_google.py

SeleniumBase Test

📗 Here's an example of bypassing Cloudflare's challenge page: SeleniumBase/examples/cdp_mode/raw_gitlab.py

from seleniumbase import SB

with SB(uc=True, test=True, locale="en") as sb:
    url = "https://gitlab.com/users/sign_in"
    sb.activate_cdp_mode(url)
    sb.uc_gui_click_captcha()
    sb.sleep(2)
SeleniumBase SeleniumBase

📗 Here's test_get_swag.py, which tests an e-commerce site:

from seleniumbase import BaseCase
BaseCase.main(__name__, __file__)  # Call pytest

class MyTestClass(BaseCase):
    def test_swag_labs(self):
        self.open("https://www.saucedemo.com")
        self.type("#user-name", "standard_user")
        self.type("#password", "secret_sauce\n")
        self.assert_element("div.inventory_list")
        self.click('button[name*="backpack"]')
        self.click("#shopping_cart_container a")
        self.assert_text("Backpack", "div.cart_item")
        self.click("button#checkout")
        self.type("input#first-name", "SeleniumBase")
        self.type("input#last-name", "Automation")
        self.type("input#postal-code", "77123")
        self.click("input#continue")
        self.click("button#finish")
        self.assert_text("Thank you for your order!")
pytest test_get_swag.py

SeleniumBase Test

(The default browser is --chrome if not set.)

📗 Here's test_coffee_cart.py, which verifies an e-commerce site:

pytest test_coffee_cart.py --demo
SeleniumBase Coffee Cart Test

(--demo mode slows down tests and highlights actions)


📗 Here's test_demo_site.py, which covers several actions:

pytest test_demo_site.py
SeleniumBase Example

Easy to type, click, select, toggle, drag & drop, and more.

(For more examples, see the SeleniumBase/examples/ folder.)

SeleniumBase

Explore the README:

Get Started / Installation
Basic Example / Usage
Common Test Methods
Fun Facts / Learn More
Demo Mode / Debugging
Command-line Options
Directory Configuration
SeleniumBase Dashboard
Generating Test Reports
▶️ How is SeleniumBase different from raw Selenium? (click to expand)
📚 Learn about different ways of writing tests:

📗📝 Here's test_simple_login.py, which uses BaseCase class inheritance, and runs with pytest or pynose. (Use self.driver to access Selenium's raw driver.)

from seleniumbase import BaseCase
BaseCase.main(__name__, __file__)

class TestSimpleLogin(BaseCase):
    def test_simple_login(self):
        self.open("seleniumbase.io/simple/login")
        self.type("#username", "demo_user")
        self.type("#password", "secret_pass")
        self.click('a:contains("Sign in")')
        self.assert_exact_text("Welcome!", "h1")
        self.assert_element("img#image1")
        self.highlight("#image1")
        self.click_link("Sign out")
        self.assert_text("signed out", "#top_message")
📘📝 Here's raw_login_sb.py, which uses the SB Context Manager. Runs with pure python. (Use sb.driver to access Selenium's raw driver.)

from seleniumbase import SB

with SB() as sb:
    sb.open("seleniumbase.io/simple/login")
    sb.type("#username", "demo_user")
    sb.type("#password", "secret_pass")
    sb.click('a:contains("Sign in")')
    sb.assert_exact_text("Welcome!", "h1")
    sb.assert_element("img#image1")
    sb.highlight("#image1")
    sb.click_link("Sign out")
    sb.assert_text("signed out", "#top_message")
📙📝 Here's raw_login_driver.py, which uses the Driver Manager. Runs with pure python. (The driver is an improved version of Selenium's raw driver, with more methods.)

from seleniumbase import Driver

driver = Driver()
try:
    driver.open("seleniumbase.io/simple/login")
    driver.type("#username", "demo_user")
    driver.type("#password", "secret_pass")
    driver.click('a:contains("Sign in")')
    driver.assert_exact_text("Welcome!", "h1")
    driver.assert_element("img#image1")
    driver.highlight("#image1")
    driver.click_link("Sign out")
    driver.assert_text("signed out", "#top_message")
finally:
    driver.quit()

SeleniumBase Set up Python & Git:
Supported Python Versions

🔵 Add Python and Git to your System PATH.

🔵 Using a Python virtual env is recommended.


SeleniumBase Install SeleniumBase:
You can install seleniumbase from PyPI or GitHub:

🔵 How to install seleniumbase from PyPI:

pip install seleniumbase
(Add --upgrade OR -U to upgrade SeleniumBase.)
(Add --force-reinstall to upgrade indirect packages.)
(Use pip3 if multiple versions of Python are present.)
🔵 How to install seleniumbase from a GitHub clone:

git clone https://github.com/seleniumbase/SeleniumBase.git
cd SeleniumBase/
pip install -e .
🔵 How to upgrade an existing install from a GitHub clone:

git pull
pip install -e .
🔵 Type seleniumbase or sbase to verify that SeleniumBase was installed successfully:

 ___      _          _             ___              
/ __| ___| |___ _ _ (_)_  _ _ __  | _ ) __ _ ______ 
\__ \/ -_) / -_) ' \| | \| | '  \ | _ \/ _` (_-< -_)
|___/\___|_\___|_||_|_|\_,_|_|_|_\|___/\__,_/__|___|
----------------------------------------------------

╭──────────────────────────────────────────────────╮
│  * USAGE: "seleniumbase [COMMAND] [PARAMETERS]"  │
│  *    OR:        "sbase [COMMAND] [PARAMETERS]"  │
│                                                  │
│ COMMANDS:        PARAMETERS / DESCRIPTIONS:      │
│    get / install    [DRIVER_NAME] [OPTIONS]      │
│    methods          (List common Python methods) │
│    options          (List common pytest options) │
│    behave-options   (List common behave options) │
│    gui / commander  [OPTIONAL PATH or TEST FILE] │
│    behave-gui       (SBase Commander for Behave) │
│    caseplans        [OPTIONAL PATH or TEST FILE] │
│    mkdir            [DIRECTORY] [OPTIONS]        │
│    mkfile           [FILE.py] [OPTIONS]          │
│    mkrec / codegen  [FILE.py] [OPTIONS]          │
│    recorder         (Open Recorder Desktop App.) │
│    record           (If args: mkrec. Else: App.) │
│    mkpres           [FILE.py] [LANG]             │
│    mkchart          [FILE.py] [LANG]             │
│    print            [FILE] [OPTIONS]             │
│    translate        [SB_FILE.py] [LANG] [ACTION] │
│    convert          [WEBDRIVER_UNITTEST_FILE.py] │
│    extract-objects  [SB_FILE.py]                 │
│    inject-objects   [SB_FILE.py] [OPTIONS]       │
│    objectify        [SB_FILE.py] [OPTIONS]       │
│    revert-objects   [SB_FILE.py] [OPTIONS]       │
│    encrypt / obfuscate                           │
│    decrypt / unobfuscate                         │
│    proxy            (Start a basic proxy server) │
│    download server  (Get Selenium Grid JAR file) │
│    grid-hub         [start|stop] [OPTIONS]       │
│    grid-node        [start|stop] --hub=[HOST/IP] │
│                                                  │
│ *  EXAMPLE => "sbase get chromedriver stable"    │
│ *  For command info => "sbase help [COMMAND]"    │
│ *  For info on all commands => "sbase --help"    │
╰──────────────────────────────────────────────────╯
🔵 Downloading webdrivers:
✅ SeleniumBase automatically downloads webdrivers as needed, such as chromedriver.

▶️ Here's sample output from a chromedriver download. (click to expand)

SeleniumBase Basic Example / Usage:
🔵 If you've cloned SeleniumBase, you can run tests from the examples/ folder.

Here's my_first_test.py:

cd examples/
pytest my_first_test.py
SeleniumBase Test

Here's the full code for my_first_test.py:

from seleniumbase import BaseCase
BaseCase.main(__name__, __file__)

class MyTestClass(BaseCase):
    def test_swag_labs(self):
        self.open("https://www.saucedemo.com")
        self.type("#user-name", "standard_user")
        self.type("#password", "secret_sauce\n")
        self.assert_element("div.inventory_list")
        self.assert_exact_text("Products", "span.title")
        self.click('button[name*="backpack"]')
        self.click("#shopping_cart_container a")
        self.assert_exact_text("Your Cart", "span.title")
        self.assert_text("Backpack", "div.cart_item")
        self.click("button#checkout")
        self.type("#first-name", "SeleniumBase")
        self.type("#last-name", "Automation")
        self.type("#postal-code", "77123")
        self.click("input#continue")
        self.assert_text("Checkout: Overview")
        self.assert_text("Backpack", "div.cart_item")
        self.assert_text("29.99", "div.inventory_item_price")
        self.click("button#finish")
        self.assert_exact_text("Thank you for your order!", "h2")
        self.assert_element('img[alt="Pony Express"]')
        self.js_click("a#logout_sidebar_link")
        self.assert_element("div#login_button_container")
By default, CSS Selectors are used for finding page elements.
If you're new to CSS Selectors, games like CSS Diner can help you learn.
For more reading, here's an advanced guide on CSS attribute selectors.

SeleniumBase Here are some common SeleniumBase methods:
self.open(url)  # Navigate the browser window to the URL.
self.type(selector, text)  # Update the field with the text.
self.click(selector)  # Click the element with the selector.
self.click_link(link_text)  # Click the link containing text.
self.go_back()  # Navigate back to the previous URL.
self.select_option_by_text(dropdown_selector, option)
self.hover_and_click(hover_selector, click_selector)
self.drag_and_drop(drag_selector, drop_selector)
self.get_text(selector)  # Get the text from the element.
self.get_current_url()  # Get the URL of the current page.
self.get_page_source()  # Get the HTML of the current page.
self.get_attribute(selector, attribute)  # Get element attribute.
self.get_title()  # Get the title of the current page.
self.switch_to_frame(frame)  # Switch into the iframe container.
self.switch_to_default_content()  # Leave the iframe container.
self.open_new_window()  # Open a new window in the same browser.
self.switch_to_window(window)  # Switch to the browser window.
self.switch_to_default_window()  # Switch to the original window.
self.get_new_driver(OPTIONS)  # Open a new driver with OPTIONS.
self.switch_to_driver(driver)  # Switch to the browser driver.
self.switch_to_default_driver()  # Switch to the original driver.
self.wait_for_element(selector)  # Wait until element is visible.
self.is_element_visible(selector)  # Return element visibility.
self.is_text_visible(text, selector)  # Return text visibility.
self.sleep(seconds)  # Do nothing for the given amount of time.
self.save_screenshot(name)  # Save a screenshot in .png format.
self.assert_element(selector)  # Verify the element is visible.
self.assert_text(text, selector)  # Verify text in the element.
self.assert_exact_text(text, selector)  # Verify text is exact.
self.assert_title(title)  # Verify the title of the web page.
self.assert_downloaded_file(file)  # Verify file was downloaded.
self.assert_no_404_errors()  # Verify there are no broken links.
self.assert_no_js_errors()  # Verify there are no JS errors.
🔵 For the complete list of SeleniumBase methods, see: Method Summary


SeleniumBase Fun Facts / Learn More:
✅ SeleniumBase automatically handles common WebDriver actions such as launching web browsers before tests, saving screenshots during failures, and closing web browsers after tests.

✅ SeleniumBase lets you customize tests via command-line options.

✅ SeleniumBase uses simple syntax for commands. Example:

self.type("input", "dogs\n")  # (The "\n" presses ENTER)
Most SeleniumBase scripts can be run with pytest, pynose, or pure python. Not all test runners can run all test formats. For example, tests that use the sb pytest fixture can only be run with pytest. (See Syntax Formats) There's also a Gherkin test format that runs with behave.

pytest coffee_cart_tests.py --rs
pytest test_sb_fixture.py --demo
pytest test_suite.py --rs --html=report.html --dashboard

pynose basic_test.py --mobile
pynose test_suite.py --headless --report --show-report

python raw_sb.py
python raw_test_scripts.py

behave realworld.feature
behave calculator.feature -D rs -D dashboard
✅ pytest includes automatic test discovery. If you don't specify a specific file or folder to run, pytest will automatically search through all subdirectories for tests to run based on the following criteria:

Python files that start with test_ or end with _test.py.
Python methods that start with test_.
With a SeleniumBase pytest.ini file present, you can modify default discovery settings. The Python class name can be anything because seleniumbase.BaseCase inherits unittest.TestCase to trigger autodiscovery.

✅ You can do a pre-flight check to see which tests would get discovered by pytest before the actual run:

pytest --co -q
✅ You can be more specific when calling pytest or pynose on a file:

pytest [FILE_NAME.py]::[CLASS_NAME]::[METHOD_NAME]

pynose [FILE_NAME.py]:[CLASS_NAME].[METHOD_NAME]
✅ No More Flaky Tests! SeleniumBase methods automatically wait for page elements to finish loading before interacting with them (up to a timeout limit). This means you no longer need random time.sleep() statements in your scripts.

NO MORE FLAKY TESTS!

✅ SeleniumBase supports all major browsers and operating systems:

Browsers: Chrome, Edge, Firefox, and Safari.

Systems: Linux/Ubuntu, macOS, and Windows.

✅ SeleniumBase works on all popular CI/CD platforms:

GitHub Actions integration Jenkins integration Azure integration Google Cloud integration AWS integration Your Computer

✅ SeleniumBase includes an automated/manual hybrid solution called MasterQA to speed up manual testing with automation while manual testers handle validation.

✅ SeleniumBase supports running tests while offline (assuming webdrivers have previously been downloaded when online).

✅ For a full list of SeleniumBase features, Click Here.


SeleniumBase Demo Mode / Debugging:
🔵 Demo Mode helps you see what a test is doing. If a test is moving too fast for your eyes, run it in Demo Mode to pause the browser briefly between actions, highlight page elements being acted on, and display assertions:

pytest my_first_test.py --demo
🔵 time.sleep(seconds) can be used to make a test wait at a specific spot:

import time; time.sleep(3)  # Do nothing for 3 seconds.
🔵 Debug Mode with Python's built-in pdb library helps you debug tests:

import pdb; pdb.set_trace()
import pytest; pytest.set_trace()
breakpoint()  # Shortcut for "import pdb; pdb.set_trace()"
(pdb commands: n, c, s, u, d => next, continue, step, up, down)

🔵 To pause an active test that throws an exception or error, (and keep the browser window open while Debug Mode begins in the console), add --pdb as a pytest option:

pytest test_fail.py --pdb
🔵 To start tests in Debug Mode, add --trace as a pytest option:

pytest test_coffee_cart.py --trace
SeleniumBase test with the pdbp (Pdb+) debugger


🔵 Command-line Options:
✅ Here are some useful command-line options that come with pytest:

-v  # Verbose mode. Prints the full name of each test and shows more details.
-q  # Quiet mode. Print fewer details in the console output when running tests.
-x  # Stop running the tests after the first failure is reached.
--html=report.html  # Creates a detailed pytest-html report after tests finish.
--co | --collect-only  # Show what tests would get run. (Without running them)
--co -q  # (Both options together!) - Do a dry run with full test names shown.
-n=NUM  # Multithread the tests using that many threads. (Speed up test runs!)
-s  # See print statements. (Should be on by default with pytest.ini present.)
--junit-xml=report.xml  # Creates a junit-xml report after tests finish.
--pdb  # If a test fails, enter Post Mortem Debug Mode. (Don't use with CI!)
--trace  # Enter Debug Mode at the beginning of each test. (Don't use with CI!)
-m=MARKER  # Run tests with the specified pytest marker.
✅ SeleniumBase provides additional pytest command-line options for tests:

--browser=BROWSER  # (The web browser to use. Default: "chrome".)
--chrome  # (Shortcut for "--browser=chrome". On by default.)
--edge  # (Shortcut for "--browser=edge".)
--firefox  # (Shortcut for "--browser=firefox".)
--safari  # (Shortcut for "--browser=safari".)
--settings-file=FILE  # (Override default SeleniumBase settings.)
--env=ENV  # (Set the test env. Access with "self.env" in tests.)
--account=STR  # (Set account. Access with "self.account" in tests.)
--data=STRING  # (Extra test data. Access with "self.data" in tests.)
--var1=STRING  # (Extra test data. Access with "self.var1" in tests.)
--var2=STRING  # (Extra test data. Access with "self.var2" in tests.)
--var3=STRING  # (Extra test data. Access with "self.var3" in tests.)
--variables=DICT  # (Extra test data. Access with "self.variables".)
--user-data-dir=DIR  # (Set the Chrome user data directory to use.)
--protocol=PROTOCOL  # (The Selenium Grid protocol: http|https.)
--server=SERVER  # (The Selenium Grid server/IP used for tests.)
--port=PORT  # (The Selenium Grid port used by the test server.)
--cap-file=FILE  # (The web browser's desired capabilities to use.)
--cap-string=STRING  # (The web browser's desired capabilities to use.)
--proxy=SERVER:PORT  # (Connect to a proxy server:port as tests are running)
--proxy=USERNAME:PASSWORD@SERVER:PORT  # (Use an authenticated proxy server)
--proxy-bypass-list=STRING # (";"-separated hosts to bypass, Eg "*.foo.com")
--proxy-pac-url=URL  # (Connect to a proxy server using a PAC_URL.pac file.)
--proxy-pac-url=USERNAME:PASSWORD@URL  # (Authenticated proxy with PAC URL.)
--proxy-driver  # (If a driver download is needed, will use: --proxy=PROXY.)
--multi-proxy  # (Allow multiple authenticated proxies when multi-threaded.)
--agent=STRING  # (Modify the web browser's User-Agent string.)
--mobile  # (Use the mobile device emulator while running tests.)
--metrics=STRING  # (Set mobile metrics: "CSSWidth,CSSHeight,PixelRatio".)
--chromium-arg="ARG=N,ARG2"  # (Set Chromium args, ","-separated, no spaces.)
--firefox-arg="ARG=N,ARG2"  # (Set Firefox args, comma-separated, no spaces.)
--firefox-pref=SET  # (Set a Firefox preference:value set, comma-separated.)
--extension-zip=ZIP  # (Load a Chrome Extension .zip|.crx, comma-separated.)
--extension-dir=DIR  # (Load a Chrome Extension directory, comma-separated.)
--disable-features="F1,F2"  # (Disable features, comma-separated, no spaces.)
--binary-location=PATH  # (Set path of the Chromium browser binary to use.)
--driver-version=VER  # (Set the chromedriver or uc_driver version to use.)
--sjw  # (Skip JS Waits for readyState to be "complete" or Angular to load.)
--wfa  # (Wait for AngularJS to be done loading after specific web actions.)
--pls=PLS  # (Set pageLoadStrategy on Chrome: "normal", "eager", or "none".)
--headless  # (The default headless mode. Linux uses this mode by default.)
--headless1  # (Use Chrome's old headless mode. Fast, but has limitations.)
--headless2  # (Use Chrome's new headless mode, which supports extensions.)
--headed  # (Run tests in headed/GUI mode on Linux OS, where not default.)
--xvfb  # (Run tests using the Xvfb virtual display server on Linux OS.)
--xvfb-metrics=STRING  # (Set Xvfb display size on Linux: "Width,Height".)
--locale=LOCALE_CODE  # (Set the Language Locale Code for the web browser.)
--interval=SECONDS  # (The autoplay interval for presentations & tour steps)
--start-page=URL  # (The starting URL for the web browser when tests begin.)
--archive-logs  # (Archive existing log files instead of deleting them.)
--archive-downloads  # (Archive old downloads instead of deleting them.)
--time-limit=SECONDS  # (Safely fail any test that exceeds the time limit.)
--slow  # (Slow down the automation. Faster than using Demo Mode.)
--demo  # (Slow down and visually see test actions as they occur.)
--demo-sleep=SECONDS  # (Set the wait time after Slow & Demo Mode actions.)
--highlights=NUM  # (Number of highlight animations for Demo Mode actions.)
--message-duration=SECONDS  # (The time length for Messenger alerts.)
--check-js  # (Check for JavaScript errors after page loads.)
--ad-block  # (Block some types of display ads from loading.)
--host-resolver-rules=RULES  # (Set host-resolver-rules, comma-separated.)
--block-images  # (Block images from loading during tests.)
--do-not-track  # (Indicate to websites that you don't want to be tracked.)
--verify-delay=SECONDS  # (The delay before MasterQA verification checks.)
--ee | --esc-end  # (Lets the user end the current test via the ESC key.)
--recorder  # (Enables the Recorder for turning browser actions into code.)
--rec-behave  # (Same as Recorder Mode, but also generates behave-gherkin.)
--rec-sleep  # (If the Recorder is enabled, also records self.sleep calls.)
--rec-print  # (If the Recorder is enabled, prints output after tests end.)
--disable-cookies  # (Disable Cookies on websites. Pages might break!)
--disable-js  # (Disable JavaScript on websites. Pages might break!)
--disable-csp  # (Disable the Content Security Policy of websites.)
--disable-ws  # (Disable Web Security on Chromium-based browsers.)
--enable-ws  # (Enable Web Security on Chromium-based browsers.)
--enable-sync  # (Enable "Chrome Sync" on websites.)
--uc | --undetected  # (Use undetected-chromedriver to evade bot-detection.)
--uc-cdp-events  # (Capture CDP events when running in "--undetected" mode.)
--log-cdp  # ("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})
--remote-debug  # (Sync to Chrome Remote Debugger chrome://inspect/#devices)
--ftrace | --final-trace  # (Debug Mode after each test. Don't use with CI!)
--dashboard  # (Enable the SeleniumBase Dashboard. Saved at: dashboard.html)
--dash-title=STRING  # (Set the title shown for the generated dashboard.)
--enable-3d-apis  # (Enables WebGL and 3D APIs.)
--swiftshader  # (Chrome "--use-gl=angle" / "--use-angle=swiftshader-webgl")
--incognito  # (Enable Chrome's Incognito mode.)
--guest  # (Enable Chrome's Guest mode.)
--dark  # (Enable Chrome's Dark mode.)
--devtools  # (Open Chrome's DevTools when the browser opens.)
--rs | --reuse-session  # (Reuse browser session for all tests.)
--rcs | --reuse-class-session  # (Reuse session for tests in class.)
--crumbs  # (Delete all cookies between tests reusing a session.)
--disable-beforeunload  # (Disable the "beforeunload" event on Chrome.)
--window-position=X,Y  # (Set the browser's starting window position.)
--window-size=WIDTH,HEIGHT  # (Set the browser's starting window size.)
--maximize  # (Start tests with the browser window maximized.)
--screenshot  # (Save a screenshot at the end of each test.)
--no-screenshot  # (No screenshots saved unless tests directly ask it.)
--visual-baseline  # (Set the visual baseline for Visual/Layout tests.)
--wire  # (Use selenium-wire's webdriver for replacing selenium webdriver.)
--external-pdf  # (Set Chromium "plugins.always_open_pdf_externally":True.)
--timeout-multiplier=MULTIPLIER  # (Multiplies the default timeout values.)
--list-fail-page  # (After each failing test, list the URL of the failure.)
(See the full list of command-line option definitions here. For detailed examples of command-line options, see customizing_test_runs.md)

🔵 During test failures, logs and screenshots from the most recent test run will get saved to the latest_logs/ folder. Those logs will get moved to archived_logs/ if you add --archive_logs to command-line options, or have ARCHIVE_EXISTING_LOGS set to True in settings.py, otherwise log files with be cleaned up at the start of the next test run. The test_suite.py collection contains tests that fail on purpose so that you can see how logging works.

cd examples/

pytest test_suite.py --chrome

pytest test_suite.py --firefox
An easy way to override seleniumbase/config/settings.py is by using a custom settings file. Here's the command-line option to add to tests: (See examples/custom_settings.py) --settings_file=custom_settings.py (Settings include default timeout values, a two-factor auth key, DB credentials, S3 credentials, and other important settings used by tests.)

🔵 To pass additional data from the command-line to tests, add --data="ANY STRING". Inside your tests, you can use self.data to access that.


SeleniumBase Directory Configuration:
🔵 When running tests with pytest, you'll want a copy of pytest.ini in your root folders. When running tests with pynose, you'll want a copy of setup.cfg in your root folders. These files specify default configuration details for tests. Test folders should also include a blank init.py file to allow your test files to import other files from that folder.

🔵 sbase mkdir DIR creates a folder with config files and sample tests:

sbase mkdir ui_tests
That new folder will have these files:

ui_tests/
├── __init__.py
├── my_first_test.py
├── parameterized_test.py
├── pytest.ini
├── requirements.txt
├── setup.cfg
├── test_demo_site.py
└── boilerplates/
    ├── __init__.py
    ├── base_test_case.py
    ├── boilerplate_test.py
    ├── classic_obj_test.py
    ├── page_objects.py
    ├── sb_fixture_test.py
    └── samples/
        ├── __init__.py
        ├── google_objects.py
        ├── google_test.py
        ├── sb_swag_test.py
        └── swag_labs_test.py
ProTip™: You can also create a boilerplate folder without any sample tests in it by adding -b or --basic to the sbase mkdir command:

sbase mkdir ui_tests --basic
That new folder will have these files:

ui_tests/
├── __init__.py
├── pytest.ini
├── requirements.txt
└── setup.cfg
Of those files, the pytest.ini config file is the most important, followed by a blank __init__.py file. There's also a setup.cfg file (for pynose). Finally, the requirements.txt file can be used to help you install seleniumbase into your environments (if it's not already installed).

SeleniumBase Log files from failed tests:
Let's try an example of a test that fails:

""" test_fail.py """
from seleniumbase import BaseCase
BaseCase.main(__name__, __file__)

class MyTestClass(BaseCase):

    def test_find_army_of_robots_on_xkcd_desert_island(self):
        self.open("https://xkcd.com/731/")
        self.assert_element("div#ARMY_OF_ROBOTS", timeout=1)  # This should fail
You can run it from the examples/ folder like this:

pytest test_fail.py
🔵 You'll notice that a logs folder, ./latest_logs/, was created to hold information (and screenshots) about the failing test. During test runs, past results get moved to the archived_logs folder if you have ARCHIVE_EXISTING_LOGS set to True in settings.py, or if your run tests with --archive-logs. If you choose not to archive existing logs, they will be deleted and replaced by the logs of the latest test run.


SeleniumBase SeleniumBase Dashboard:
🔵 The --dashboard option for pytest generates a SeleniumBase Dashboard located at dashboard.html, which updates automatically as tests run and produce results. Example:

pytest --dashboard --rs --headless
The SeleniumBase Dashboard

🔵 Additionally, you can host your own SeleniumBase Dashboard Server on a port of your choice. Here's an example of that using Python's http.server:

python -m http.server 1948
🔵 Now you can navigate to http://localhost:1948/dashboard.html in order to view the dashboard as a web app. This requires two different terminal windows: one for running the server, and another for running the tests, which should be run from the same directory. (Use Ctrl+C to stop the http server.)

🔵 Here's a full example of what the SeleniumBase Dashboard may look like:

pytest test_suite.py test_image_saving.py --dashboard --rs --headless
The SeleniumBase Dashboard


SeleniumBase Generating Test Reports:
🔵 pytest HTML Reports:
✅ Using --html=report.html gives you a fancy report of the name specified after your test suite completes.

pytest test_suite.py --html=report.html
Example Pytest Report

✅ When combining pytest html reports with SeleniumBase Dashboard usage, the pie chart from the Dashboard will get added to the html report. Additionally, if you set the html report URL to be the same as the Dashboard URL when also using the dashboard, (example: --dashboard --html=dashboard.html), then the Dashboard will become an advanced html report when all the tests complete.

✅ Here's an example of an upgraded html report:

pytest test_suite.py --dashboard --html=report.html
Dashboard Pytest HTML Report

If viewing pytest html reports in Jenkins, you may need to configure Jenkins settings for the html to render correctly. This is due to Jenkins CSP changes.

You can also use --junit-xml=report.xml to get an xml report instead. Jenkins can use this file to display better reporting for your tests.

pytest test_suite.py --junit-xml=report.xml
🔵 pynose Reports:
The --report option gives you a fancy report after your test suite completes.

pynose test_suite.py --report
Example pynose Report

(NOTE: You can add --show-report to immediately display pynose reports after the test suite completes. Only use --show-report when running tests locally because it pauses the test run.)

🔵 behave Dashboard & Reports:
(The behave_bdd/ folder can be found in the examples/ folder.)

behave behave_bdd/features/ -D dashboard -D headless
SeleniumBase

You can also use --junit to get .xml reports for each behave feature. Jenkins can use these files to display better reporting for your tests.

behave behave_bdd/features/ --junit -D rs -D headless
🔵 Allure Reports:
See: https://allurereport.org/docs/pytest/

SeleniumBase no longer includes allure-pytest as part of installed dependencies. If you want to use it, install it first:

pip install allure-pytest
Now your tests can create Allure results files, which can be processed by Allure Reports.

pytest test_suite.py --alluredir=allure_results
SeleniumBase Using a Proxy Server:
If you wish to use a proxy server for your browser tests (Chromium or Firefox), you can add --proxy=IP_ADDRESS:PORT as an argument on the command line.

pytest proxy_test.py --proxy=IP_ADDRESS:PORT
If the proxy server that you wish to use requires authentication, you can do the following (Chromium only):

pytest proxy_test.py --proxy=USERNAME:PASSWORD@IP_ADDRESS:PORT
SeleniumBase also supports SOCKS4 and SOCKS5 proxies:

pytest proxy_test.py --proxy="socks4://IP_ADDRESS:PORT"

pytest proxy_test.py --proxy="socks5://IP_ADDRESS:PORT"
To make things easier, you can add your frequently-used proxies to PROXY_LIST in proxy_list.py, and then use --proxy=KEY_FROM_PROXY_LIST to use the IP_ADDRESS:PORT of that key.

pytest proxy_test.py --proxy=proxy1
SeleniumBase Changing the User-Agent:
🔵 If you wish to change the User-Agent for your browser tests (Chromium and Firefox only), you can add --agent="USER AGENT STRING" as an argument on the command-line.

pytest user_agent_test.py --agent="Mozilla/5.0 (Nintendo 3DS; U; ; en) Version/1.7412.EU"
SeleniumBase Handling Pop-Up Alerts:
🔵 self.accept_alert() automatically waits for and accepts alert pop-ups. self.dismiss_alert() automatically waits for and dismisses alert pop-ups. On occasion, some methods like self.click(SELECTOR) might dismiss a pop-up on its own because they call JavaScript to make sure that the readyState of the page is complete before advancing. If you're trying to accept a pop-up that got dismissed this way, use this workaround: Call self.find_element(SELECTOR).click() instead, (which will let the pop-up remain on the screen), and then use self.accept_alert() to accept the pop-up (more on that here). If pop-ups are intermittent, wrap code in a try/except block.

SeleniumBase Building Guided Tours for Websites:
🔵 Learn about SeleniumBase Interactive Walkthroughs (in the examples/tour_examples/ folder). It's great for prototyping a website onboarding experience.


SeleniumBase Production Environments & Integrations:
▶️ Here are some things you can do to set up a production environment for your testing. (click to expand)

SeleniumBase Detailed Method Specifications and Examples:
🔵 Navigating to a web page: (and related commands)

self.open("https://xkcd.com/378/")  # This method opens the specified page.

self.go_back()  # This method navigates the browser to the previous page.

self.go_forward()  # This method navigates the browser forward in history.

self.refresh_page()  # This method reloads the current page.

self.get_current_url()  # This method returns the current page URL.

self.get_page_source()  # This method returns the current page source.
ProTip™: You can use the self.get_page_source() method with Python's find() command to parse through HTML to find something specific. (For more advanced parsing, see the BeautifulSoup example.)

source = self.get_page_source()
head_open_tag = source.find('<head>')
head_close_tag = source.find('</head>', head_open_tag)
everything_inside_head = source[head_open_tag+len('<head>'):head_close_tag]
🔵 Clicking:

To click an element on the page:

self.click("div#my_id")
ProTip™: In most web browsers, you can right-click on a page and select Inspect Element to see the CSS selector details that you'll need to create your own scripts.

🔵 Typing Text:

self.type(selector, text) # updates the text from the specified element with the specified value. An exception is raised if the element is missing or if the text field is not editable. Example:

self.type("input#id_value", "2012")
You can also use self.add_text() or the WebDriver .send_keys() command, but those won't clear the text box first if there's already text inside.

🔵 Getting the text from an element on a page:

text = self.get_text("header h2")
🔵 Getting the attribute value from an element on a page:

attribute = self.get_attribute("#comic img", "title")
🔵 Asserting existence of an element on a page within some number of seconds:

self.wait_for_element_present("div.my_class", timeout=10)
(NOTE: You can also use: self.assert_element_present(ELEMENT))

🔵 Asserting visibility of an element on a page within some number of seconds:

self.wait_for_element_visible("a.my_class", timeout=5)
(NOTE: The short versions of that are self.find_element(ELEMENT) and self.assert_element(ELEMENT). The find_element() version returns the element.)

Since the line above returns the element, you can combine that with .click() as shown below:

self.find_element("a.my_class", timeout=5).click()

# But you're better off using the following statement, which does the same thing:

self.click("a.my_class")  # DO IT THIS WAY!
ProTip™: You can use dots to signify class names (Ex: div.class_name) as a simplified version of div[class="class_name"] within a CSS selector.

You can also use *= to search for any partial value in a CSS selector as shown below:

self.click('a[name*="partial_name"]')
🔵 Asserting visibility of text inside an element on a page within some number of seconds:

self.assert_text("Make it so!", "div#trek div.picard div.quotes")
self.assert_text("Tea. Earl Grey. Hot.", "div#trek div.picard div.quotes", timeout=3)
(NOTE: self.find_text(TEXT, ELEMENT) and self.wait_for_text(TEXT, ELEMENT) also do this. For backwards compatibility, older method names were kept, but the default timeout may be different.)

🔵 Asserting Anything:

self.assert_true(var1 == var2)

self.assert_false(var1 == var2)

self.assert_equal(var1, var2)
🔵 Useful Conditional Statements: (with creative examples)

❓ is_element_visible(selector): (visible on the page)

if self.is_element_visible('div#warning'):
    print("Red Alert: Something bad might be happening!")
❓ is_element_present(selector): (present in the HTML)

if self.is_element_present('div#top_secret img.tracking_cookie'):
    self.contact_cookie_monster()  # Not a real SeleniumBase method
else:
    current_url = self.get_current_url()
    self.contact_the_nsa(url=current_url, message="Dark Zone Found")  # Not a real SeleniumBase method
def is_there_a_cloaked_klingon_ship_on_this_page():
    if self.is_element_present("div.ships div.klingon"):
        return not self.is_element_visible("div.ships div.klingon")
    return False
❓ is_text_visible(text, selector): (text visible on element)

if self.is_text_visible("You Shall Not Pass!", "h1"):
    self.open("https://www.youtube.com/watch?v=3xYXUeSmb-Y")
▶️ Click for a longer example of is_text_visible():
❓ is_link_text_visible(link_text):

if self.is_link_text_visible("Stop! Hammer time!"):
    self.click_link("Stop! Hammer time!")
🔵 Switching Tabs:
If your test opens up a new tab/window, you can switch to it. (SeleniumBase automatically switches to new tabs that don't open to about:blank URLs.)

self.switch_to_window(1)  # This switches to the new tab (0 is the first one)
🔵 How to handle iframes:
🔵 iframes follow the same principle as new windows: You must first switch to the iframe if you want to perform actions in there:

self.switch_to_frame("iframe")
# ... Now perform actions inside the iframe
self.switch_to_parent_frame()  # Exit the current iframe
To exit from multiple iframes, use self.switch_to_default_content(). (If inside a single iframe, this has the same effect as self.switch_to_parent_frame().)

self.switch_to_frame('iframe[name="frame1"]')
self.switch_to_frame('iframe[name="frame2"]')
# ... Now perform actions inside the inner iframe
self.switch_to_default_content()  # Back to the main page
🔵 You can also use a context manager to act inside iframes:

with self.frame_switch("iframe"):
    # ... Now perform actions while inside the code block
# You have left the iframe
This also works with nested iframes:

with self.frame_switch('iframe[name="frame1"]'):
    with self.frame_switch('iframe[name="frame2"]'):
        # ... Now perform actions while inside the code block
    # You are now back inside the first iframe
# You have left all the iframes
🔵 How to execute custom jQuery scripts:
jQuery is a powerful JavaScript library that allows you to perform advanced actions in a web browser. If the web page you're on already has jQuery loaded, you can start executing jQuery scripts immediately. You'd know this because the web page would contain something like the following in the HTML:

<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.3/jquery.min.js"></script>
🔵 It's OK if you want to use jQuery on a page that doesn't have it loaded yet. To do so, run the following command first:

self.activate_jquery()
▶️ Here are some examples of using jQuery in your scripts. (click to expand)
🔵 How to handle a restrictive CSP:
❗ Some websites have a restrictive Content Security Policy to prevent users from loading jQuery and other external libraries onto their websites. If you need to use jQuery or another JS library on those websites, add --disable-csp as a pytest command-line option to load a Chromium extension that bypasses the CSP.

🔵 More JavaScript fun:
▶️ In this example, JavaScript creates a referral button on a page, which is then clicked. (click to expand)
🔵 How to use deferred asserts:
Let's say you want to verify multiple different elements on a web page in a single test, but you don't want the test to fail until you verified several elements at once so that you don't have to rerun the test to find more missing elements on the same page. That's where deferred asserts come in. Here's an example:

from seleniumbase import BaseCase
BaseCase.main(__name__, __file__)

class DeferredAssertTests(BaseCase):
    def test_deferred_asserts(self):
        self.open("https://xkcd.com/993/")
        self.wait_for_element("#comic")
        self.deferred_assert_element('img[alt="Brand Identity"]')
        self.deferred_assert_element('img[alt="Rocket Ship"]')  # Will Fail
        self.deferred_assert_element("#comicmap")
        self.deferred_assert_text("Fake Item", "ul.comicNav")  # Will Fail
        self.deferred_assert_text("Random", "ul.comicNav")
        self.deferred_assert_element('a[name="Super Fake !!!"]')  # Will Fail
        self.deferred_assert_exact_text("Brand Identity", "#ctitle")
        self.deferred_assert_exact_text("Fake Food", "#comic")  # Will Fail
        self.process_deferred_asserts()
deferred_assert_element() and deferred_assert_text() will save any exceptions that would be raised. To flush out all the failed deferred asserts into a single exception, make sure to call self.process_deferred_asserts() at the end of your test method. If your test hits multiple pages, you can call self.process_deferred_asserts() before navigating to a new page so that the screenshot from your log files matches the URL where the deferred asserts were made.

🔵 How to access raw WebDriver:
If you need access to any commands that come with standard WebDriver, you can call them directly like this:

self.driver.delete_all_cookies()
capabilities = self.driver.capabilities
self.driver.find_elements("partial link text", "GitHub")
(In general, you'll want to use the SeleniumBase versions of methods when available.)

🔵 How to retry failing tests automatically:
You can use pytest --reruns=NUM to retry failing tests that many times. Add --reruns-delay=SECONDS to wait that many seconds between retries. Example:

pytest --reruns=1 --reruns-delay=1
You can use the @retry_on_exception() decorator to retry failing methods. (First import: from seleniumbase import decorators). To learn more about SeleniumBase decorators, click here.



UC Mode
SeleniumBase UC Mode 👤¶
👤 SeleniumBase UC Mode (Undetected-Chromedriver Mode) allows bots to appear human, which lets them evade detection from anti-bot services that try to block them or trigger CAPTCHAs on various websites.

(For the successor to default UC Mode, see CDP Mode 🐙)¶

(Watch the 1st UC Mode tutorial on YouTube! ▶️)


(Watch the 2nd UC Mode tutorial on YouTube! ▶️)


(Watch the 3rd UC Mode tutorial on YouTube! ▶️)


(Watch the 4th UC Mode tutorial on YouTube! ▶️)

👤 UC Mode is based on undetected-chromedriver. UC Mode includes multiple updates, fixes, and improvements, such as:

Automatically changing user-agents to prevent detection.
Automatically setting various Chromium args as needed.
Has special uc_*() methods for bypassing CAPTCHAs.
👤 Here's a simple example with the Driver manager:

from seleniumbase import Driver

driver = Driver(uc=True)
url = "https://gitlab.com/users/sign_in"
driver.uc_open_with_reconnect(url, 4)
driver.uc_gui_click_captcha()
driver.quit()
SeleniumBase

👤 Here's an example with the SB manager (which has more methods and functionality than the Driver format):

from seleniumbase import SB

with SB(uc=True) as sb:
    url = "https://gitlab.com/users/sign_in"
    sb.uc_open_with_reconnect(url, 4)
    sb.uc_gui_click_captcha()
(Note: If running UC Mode scripts on headless Linux machines, then you'll need to use the SB manager instead of the Driver manager because the SB manager includes a special virtual display that allows for PyAutoGUI actions.)

👤 Here's a longer example: (Note that sb.uc_gui_click_captcha() performs a special click using PyAutoGUI if a CAPTCHA is detected.)

from seleniumbase import SB

with SB(uc=True, test=True) as sb:
    url = "https://gitlab.com/users/sign_in"
    sb.uc_open_with_reconnect(url, 4)
    sb.uc_gui_click_captcha()
    sb.assert_text("Username", '[for="user_login"]', timeout=3)
    sb.assert_element('label[for="user_login"]')
    sb.highlight('button:contains("Sign in")')
    sb.highlight('h1:contains("GitLab.com")')
    sb.post_message("SeleniumBase wasn't detected", duration=4)
👤 Here's an example where clicking the checkbox is required, even for humans:
(Commonly seen on forms that are CAPTCHA-protected.)

SeleniumBase

from seleniumbase import SB

with SB(uc=True, test=True) as sb:
    url = "https://seleniumbase.io/apps/turnstile"
    sb.uc_open_with_reconnect(url, reconnect_time=2)
    sb.uc_gui_handle_captcha()
    sb.assert_element("img#captcha-success", timeout=3)
    sb.set_messenger_theme(location="top_left")
    sb.post_message("SeleniumBase wasn't detected", duration=3)
SeleniumBase

If running on a Linux server, uc_gui_handle_captcha() might not be good enough. Switch to uc_gui_click_captcha() to be more stealthy. Note that these methods auto-detect between CF Turnstile and Google reCAPTCHA.

Sometimes you need to add incognito=True with uc=True to maximize your anti-detection abilities. (Some websites can detect you if you don't do that.)

👤 Here's an example where the CAPTCHA appears after submitting a form:

from seleniumbase import SB

with SB(uc=True, test=True, incognito=True, locale="en") as sb:
    url = "https://ahrefs.com/website-authority-checker"
    input_field = 'input[placeholder="Enter domain"]'
    submit_button = 'span:contains("Check Authority")'
    sb.uc_open_with_reconnect(url)  # The bot-check is later
    sb.type(input_field, "github.com/seleniumbase/SeleniumBase")
    sb.reconnect(0.1)
    sb.uc_click(submit_button, reconnect_time=4)
    sb.uc_gui_click_captcha()
    sb.wait_for_text_not_visible("Checking", timeout=12)
    sb.highlight('p:contains("github.com/seleniumbase/SeleniumBase")')
    sb.highlight('a:contains("Top 100 backlinks")')
    sb.set_messenger_theme(location="bottom_center")
    sb.post_message("SeleniumBase wasn't detected!")
SeleniumBase

👤 Here, the CAPTCHA appears after clicking to go to the sign-in screen:

from seleniumbase import SB

with SB(uc=True, test=True, ad_block=True) as sb:
    url = "https://www.thaiticketmajor.com/concert/"
    sb.uc_open_with_reconnect(url, 6.111)
    sb.uc_click("button.btn-signin", 4.1)
    sb.uc_gui_click_captcha()
SeleniumBase

👤 On Linux, use sb.uc_gui_click_captcha() to handle CAPTCHAs (Cloudflare Turnstiles):

from seleniumbase import SB

with SB(uc=True, test=True) as sb:
    url = "https://www.virtualmanager.com/en/login"
    sb.uc_open_with_reconnect(url, 4)
    print(sb.get_page_title())
    sb.uc_gui_click_captcha()  # Only used if needed
    print(sb.get_page_title())
    sb.assert_element('input[name*="email"]')
    sb.assert_element('input[name*="login"]')
    sb.set_messenger_theme(location="bottom_center")
    sb.post_message("SeleniumBase wasn't detected!")
uc_gui_click_captcha on Linux

The 2nd print() should output Virtual Manager, which means that the automation successfully passed the Turnstile.

(Note: UC Mode is detectable in Headless Mode, so don't combine those options. Instead, use xvfb=True / --xvfbon Linux for the special virtual display, which is enabled by default when not changing headed/headless settings.)

👤 In UC Mode, driver.get(url) has been modified from its original version: If anti-bot services are detected from a requests.get(url) call that's made before navigating to the website, then driver.uc_open_with_reconnect(url) will be used instead. To open a URL normally in UC Mode, use driver.default_get(url).

👤 Here are some examples that use UC Mode¶
SeleniumBase/examples/verify_undetected.py
SeleniumBase/examples/raw_bing_captcha.py
SeleniumBase/examples/raw_uc_mode.py
SeleniumBase/examples/raw_cf.py
👤 Here's an example where incognito=True is needed for bypassing detection:

SeleniumBase/examples/raw_pixelscan.py
from seleniumbase import SB

with SB(uc=True, incognito=True, test=True) as sb:
    sb.driver.uc_open_with_reconnect("https://pixelscan.net/", 10)
    sb.remove_elements("jdiv")  # Remove chat widgets
    sb.highlight("span.text-success", loops=8)
    sb.highlight(".bot-detection-context", loops=10, scroll=False)
    sb.sleep(2)
SeleniumBase

👤 Here are some UC Mode examples that bypass CAPTCHAs when clicking is required¶
SeleniumBase/examples/raw_pyautogui.py
SeleniumBase/examples/raw_turnstile.py
SeleniumBase/examples/raw_form_turnstile.py
SeleniumBase/examples/uc_cdp_events.py
SeleniumBase

👤 Here are the SeleniumBase UC Mode methods: (--uc / uc=True)¶
driver.uc_open(url)

driver.uc_open_with_tab(url)

driver.uc_open_with_reconnect(url, reconnect_time=None)

driver.uc_open_with_disconnect(url, timeout=None)

driver.reconnect(timeout)

driver.disconnect()

driver.connect()

driver.uc_click(
    selector, by="css selector",
    timeout=settings.SMALL_TIMEOUT, reconnect_time=None)

driver.uc_gui_press_key(key)

driver.uc_gui_press_keys(keys)

driver.uc_gui_write(text)

driver.uc_gui_click_x_y(x, y, timeframe=0.25)

driver.uc_gui_click_captcha(frame="iframe", retry=False, blind=False)
# driver.uc_gui_click_cf(frame="iframe", retry=False, blind=False)
# driver.uc_gui_click_rc(frame="iframe", retry=False, blind=False)

driver.uc_gui_handle_captcha(frame="iframe")
# driver.uc_gui_handle_cf(frame="iframe")
# driver.uc_gui_handle_rc(frame="iframe")
(Note that the reconnect_time is used to specify how long the driver should be disconnected from Chrome to prevent detection before reconnecting again.)

👤 Since driver.get(url) is slower in UC Mode for bypassing detection, use driver.default_get(url) for a standard page load instead:

driver.default_get(url)  # Faster, but Selenium can be detected
👤 Here are some examples of using those special UC Mode methods: (Use self.driver for BaseCase formats. Use sb.driver for SB() formats):

url = "https://gitlab.com/users/sign_in"
driver.uc_open_with_reconnect(url, reconnect_time=3)
driver.uc_open_with_reconnect(url, 3)

driver.reconnect(5)
driver.reconnect(timeout=5)
👤 You can also set the reconnect_time / timeout to "breakpoint" as a valid option. This allows the user to perform manual actions (until typing c and pressing ENTER to continue from the breakpoint):

url = "https://gitlab.com/users/sign_in"
driver.uc_open_with_reconnect(url, reconnect_time="breakpoint")
driver.uc_open_with_reconnect(url, "breakpoint")

driver.reconnect(timeout="breakpoint")
driver.reconnect("breakpoint")
(Note that while the special UC Mode breakpoint is active, you can't use Selenium commands in the browser, and the browser can't detect Selenium.)

👤 On Linux, use xvfb=True / --xvfb to activate a special virtual display. This allows you to run a regular browser in an environment that has no GUI. This is important for two reasons: One: UC Mode is detectable in headless mode. Two: pyautogui doesn't work in headless mode. (Note that some methods such as uc_gui_click_captcha() require pyautogui for performing special actions.)

👤 uc_gui_click_captcha() auto-detects the CAPTCHA type before trying to click it. This is a generic method for both CF Turnstile and Google reCAPTCHA. It will use the code from uc_gui_click_cf() and uc_gui_click_rc() as needed.

👤 uc_gui_click_cf(frame="iframe", retry=False, blind=False) has three args. (All optional). The first one, frame, lets you specify the selector above the iframe in case the CAPTCHA is not located in the first iframe on the page. (In the case of Shadow-DOM, specify the selector of an element that's above the Shadow-DOM.) The second one, retry, lets you retry the click after reloading the page if the first one didn't work (and a CAPTCHA is still present after the page reload). The third arg, blind, (if True), will retry after a page reload (if the first click failed) by clicking at the last known coordinates of the CAPTCHA checkbox without confirming first with Selenium that a CAPTCHA is still on the page.

👤 uc_gui_click_rc(frame="iframe", retry=False, blind=False) is for reCAPTCHA. This may only work a few times before not working anymore... not because Selenium was detected, but because reCAPTCHA uses advanced AI to detect unusual activity, unlike the CF Turnstile, which only uses basic detection.

👤 To find out if UC Mode will work at all on a specific site (before adjusting for timing), load your site with the following script:

from seleniumbase import SB

with SB(uc=True) as sb:
    sb.uc_open_with_reconnect(URL, reconnect_time="breakpoint")
(If you remain undetected while loading the page and performing manual actions, then you know you can create a working script once you swap the breakpoint with a time and add special methods like sb.uc_click as needed.)

👤 Multithreaded UC Mode:

If you're using pytest for multithreaded UC Mode (which requires using one of the pytest syntax formats), then all you have to do is set the number of threads when your script runs. (-n NUM) Eg:

pytest --uc -n 4
(Then pytest-xdist is automatically used to spin up and process the threads.)

If you don't want to use pytest for multithreading, then you'll need to do a little more work. That involves using a different multithreading library, (eg. concurrent.futures), and making sure that thread-locking is done correctly for processes that share resources. To handle that thread-locking, include sys.argv.append("-n") in your SeleniumBase file.

Here's a sample script that uses concurrent.futures for spinning up multiple processes:

import sys
from concurrent.futures import ThreadPoolExecutor
from seleniumbase import Driver
sys.argv.append("-n")  # Tell SeleniumBase to do thread-locking as needed

def launch_driver(url):
    driver = Driver(uc=True)
    try:
        driver.get(url=url)
        driver.sleep(2)
    finally:
        driver.quit()

urls = ['https://seleniumbase.io/demo_page' for i in range(3)]
with ThreadPoolExecutor(max_workers=len(urls)) as executor:
    for url in urls:
        executor.submit(launch_driver, url)
👤 What makes UC Mode work?

Here are the 3 primary things that UC Mode does to make bots appear human:

Modifies chromedriver to rename Chrome DevTools Console variables.
Launches Chrome browsers before attaching chromedriver to them.
Disconnects chromedriver from Chrome during stealthy actions.
For example, if the Chrome DevTools Console variables aren't renamed, you can expect to find them easily when using selenium for browser automation:

SeleniumBase

(If those variables are still there, then websites can easily detect your bots.)

If you launch Chrome using chromedriver, then there will be settings that make your browser look like a bot. (Instead, UC Mode connects chromedriver to Chrome after the browser is launched, which makes Chrome look like a normal, human-controlled web browser.)

While chromedriver is connected to Chrome, website services can detect it. Thankfully, raw selenium already includes driver.service.stop() for stopping the chromedriver service, driver.service.start() for starting the chromedriver service, and driver.start_session(capabilities) for reviving the active browser session with the given capabilities. (SeleniumBase UC Mode methods automatically use those raw selenium methods as needed.)

Links to those raw Selenium method definitions have been provided for reference (but you don't need to call those methods directly):

driver.service.stop()
driver.service.start()
driver.start_session(capabilities)
Also note that chromedriver isn't detectable in a browser tab if it never touches that tab. Here's a JS command that lets you open a URL in a new tab (from your current tab):

window.open("URL"); --> (Info: W3Schools)
The above JS method is used within SeleniumBase UC Mode methods for opening URLs in a stealthy way. Since some websites try to detect if your browser is a bot on the initial page load, this allows you to bypass detection in those situations. After a few seconds (customizable), UC Mode tells chromedriver to connect to that tab so that automated commands can now be issued. At that point, chromedriver could be detected if websites are looking for it (but generally websites only look for it during specific events, such as page loads, form submissions, and button clicks).

Avoiding detection while clicking is easy if you schedule your clicks to happen at a future point when the chromedriver service has been stopped. Here's a JS command that lets you schedule events (such as clicks) to happen in the future:

window.setTimeout(function() { SCRIPT }, MS); --> (Info: W3Schools)
The above JS method is used within the SeleniumBase UC Mode method: sb.uc_click(selector) so that clicking can be done in a stealthy way. UC Mode schedules your click, disconnects chromedriver from Chrome, waits a little (customizable), and reconnects.

🏆 Choosing the right CAPTCHA service for your business / website:

SeleniumBase

As an ethical hacker / cybersecurity researcher who builds bots that bypass CAPTCHAs for sport, the CAPTCHA service that I personally recommend for keeping bots out is Google reCAPTCHA:

SeleniumBase

Since Google makes Chrome, Google's own reCAPTCHA service has access to more data than other CAPTCHA services, and can therefore use that data to make better decisions about whether or not web activity is coming from real humans or automated bots.

⚖️ Legal implications of web-scraping:

Based on the following article, https://nubela.co/blog/meta-lost-the-scraping-legal-battle-to-bright-data/, (which outlines a court case where social-networking company: Meta lost the legal battle to data-scraping company: Bright Data), it was determined that web scraping is 100% legal in the eyes of the courts as long as: 1. The scraping is only done with public data and not private data. 2. The scraping isn’t done while logged in on the site being scraped.

If the above criteria are met, then scrape away! (According to the article)

(Note: I'm not a lawyer, so I can't officially offer legal advice, but I can direct people to existing articles online where people can find their own answers.)



🐙 CDP Mode
SeleniumBase CDP Mode 🐙¶
🐙 SeleniumBase CDP Mode (Chrome Devtools Protocol Mode) is a special mode inside of SeleniumBase UC Mode that lets bots appear human while controlling the browser with the CDP-Driver. Although regular UC Mode can't perform WebDriver actions while the driver is disconnected from the browser, the CDP-Driver can.


(Watch the CDP Mode tutorial on YouTube! ▶️)


(Watch "Hacking websites with CDP" on YouTube! ▶️)


(Watch "Web-Scraping with GitHub Actions" on YouTube! ▶️)

👤 UC Mode avoids bot-detection by first disconnecting WebDriver from the browser at strategic times, calling special PyAutoGUI methods to bypass CAPTCHAs (as needed), and finally reconnecting the driver afterwards so that WebDriver actions can be performed again. Although this approach works for bypassing simple CAPTCHAs, more flexibility is needed for bypassing bot-detection on websites with advanced protection. (That's where CDP Mode comes in.)

🐙 CDP Mode is based on python-cdp, trio-cdp, and nodriver. trio-cdp is an early implementation of python-cdp, and nodriver is a modern implementation of python-cdp. (Refactored Python-CDP code is imported from MyCDP.)

🐙 CDP Mode includes multiple updates to the above, such as:

Sync methods. (Using async/await is not necessary!)
The ability to use WebDriver and CDP-Driver together.
Backwards compatibility for existing UC Mode scripts.
More configuration options when launching browsers.
More methods. (And bug-fixes for existing methods.)
PyAutoGUI integration for advanced stealth abilities.
Faster response time for support. (Eg. Discord Chat)
🐙 CDP Mode Usage¶
sb.activate_cdp_mode(url)
(Call that from a UC Mode script)

That disconnects WebDriver from Chrome (which prevents detection), and gives you access to sb.cdp methods (which don't trigger anti-bot checks).

Simple example: (SeleniumBase/examples/cdp_mode/raw_gitlab.py)

from seleniumbase import SB

with SB(uc=True, test=True, locale="en") as sb:
    url = "https://gitlab.com/users/sign_in"
    sb.activate_cdp_mode(url)
    sb.uc_gui_click_captcha()
    sb.sleep(2)
SeleniumBase SeleniumBase

(If the CAPTCHA wasn't bypassed automatically, then sb.uc_gui_click_captcha() gets the job done.)

Note that PyAutoGUI is an optional dependency. If calling a method that uses it when not already installed, then SeleniumBase installs PyAutoGUI at run-time.

For some Cloudflare CAPTCHAs that appear within websites, you may need to use sb.cdp.gui_click_element(selector) instead (if the Turnstile wasn't bypassed automatically). Example: (SeleniumBase/examples/cdp_mode/raw_planetmc.py)

from seleniumbase import SB

with SB(uc=True, test=True) as sb:
    url = "www.planetminecraft.com/account/sign_in/"
    sb.activate_cdp_mode(url)
    sb.sleep(2)
    sb.cdp.gui_click_element("#turnstile-widget div")
    sb.sleep(2)
SeleniumBase

When using sb.cdp.gui_click_element(selector) on CF Turnstiles, use the parent selector that appears above the #shadow-root element: Eg. sb.cdp.gui_click_element("#turnstile-widget div")

SeleniumBase

🐙 Here are a few common sb.cdp methods¶
sb.cdp.click(selector) (Uses the CDP API to click)
sb.cdp.click_if_visible(selector)
sb.cdp.gui_click_element(selector) (Uses PyAutoGUI)
sb.cdp.type(selector, text)
sb.cdp.press_keys(selector, text) (Human-speed type)
sb.cdp.select_all(selector)
sb.cdp.get_text(selector)
Methods that start with sb.cdp.gui use PyAutoGUI for interaction.

To use WebDriver methods again, call:

sb.reconnect() or sb.connect()
(Note that reconnecting allows anti-bots to detect you, so only reconnect if it is safe to do so.)

To disconnect again, call:

sb.disconnect()
While disconnected, if you accidentally call a WebDriver method, then SeleniumBase will attempt to use the CDP Mode version of that method (if available). For example, if you accidentally call sb.click(selector) instead of sb.cdp.click(selector), then your WebDriver call will automatically be redirected to the CDP Mode version. Not all WebDriver methods have a matching CDP Mode method. In that scenario, calling a WebDriver method while disconnected could raise an error, or make WebDriver automatically reconnect first.

To find out if WebDriver is connected or disconnected, call:

sb.is_connected()
Note: When CDP Mode is initialized from UC Mode, the WebDriver is disconnected from the browser. (The stealthy CDP-Driver takes over.)

🐙 CDP Mode examples (SeleniumBase/examples/cdp_mode)¶
▶️ 🔖 Example 1: (Pokemon site using Incapsula/Imperva protection with invisible reCAPTCHA)
SeleniumBase/examples/cdp_mode/raw_pokemon.py

▶️ 🔖 Example 2: (Hyatt site using Kasada protection)
SeleniumBase/examples/cdp_mode/raw_hyatt.py

▶️ 🔖 Example 3: (BestWestern site using DataDome protection)
SeleniumBase/examples/cdp_mode/raw_bestwestern.py

▶️ 🔖 Example 4: (Walmart site using Akamai protection with PerimeterX)
SeleniumBase/examples/cdp_mode/raw_walmart.py

▶️ 🔖 Example 5: (Nike site using Shape Security)
SeleniumBase/examples/cdp_mode/raw_nike.py

(Note: Extra sb.sleep() calls have been added to prevent bot-detection because some sites will flag you as a bot if you perform actions too quickly.)

(Note: Some sites may IP-block you for 36 hours or more if they catch you using regular Selenium WebDriver. Be extra careful when creating and/or modifying automation scripts that run on them.)

🐙 CDP Mode API / Methods¶
sb.cdp.get(url, **kwargs)
sb.cdp.open(url, **kwargs)
sb.cdp.reload(ignore_cache=True, script_to_evaluate_on_load=None)
sb.cdp.refresh(*args, **kwargs)
sb.cdp.get_event_loop()
sb.cdp.add_handler(event, handler)
sb.cdp.find_element(selector, best_match=False, timeout=None)
sb.cdp.find(selector, best_match=False, timeout=None)
sb.cdp.locator(selector, best_match=False, timeout=None)
sb.cdp.find_element_by_text(text, tag_name=None, timeout=None)
sb.cdp.find_all(selector, timeout=None)
sb.cdp.find_elements_by_text(text, tag_name=None)
sb.cdp.select(selector, timeout=None)
sb.cdp.select_all(selector, timeout=None)
sb.cdp.find_elements(selector, timeout=None)
sb.cdp.find_visible_elements(selector, timeout=None)
sb.cdp.click_nth_element(selector, number)
sb.cdp.click_nth_visible_element(selector, number)
sb.cdp.click_link(link_text)
sb.cdp.go_back()
sb.cdp.go_forward()
sb.cdp.get_navigation_history()
sb.cdp.tile_windows(windows=None, max_columns=0)
sb.cdp.grant_permissions(permissions, origin=None)
sb.cdp.grant_all_permissions()
sb.cdp.reset_permissions()
sb.cdp.get_all_cookies(*args, **kwargs)
sb.cdp.set_all_cookies(*args, **kwargs)
sb.cdp.save_cookies(*args, **kwargs)
sb.cdp.load_cookies(*args, **kwargs)
sb.cdp.clear_cookies()
sb.cdp.sleep(seconds)
sb.cdp.bring_active_window_to_front()
sb.cdp.bring_to_front()
sb.cdp.get_active_element()
sb.cdp.get_active_element_css()
sb.cdp.click(selector, timeout=None)
sb.cdp.click_active_element()
sb.cdp.click_if_visible(selector)
sb.cdp.click_visible_elements(selector, limit=0)
sb.cdp.mouse_click(selector, timeout=None)
sb.cdp.nested_click(parent_selector, selector)
sb.cdp.get_nested_element(parent_selector, selector)
sb.cdp.select_option_by_text(dropdown_selector, option)
sb.cdp.flash(selector, duration=1, color="44CC88", pause=0)
sb.cdp.highlight(selector)
sb.cdp.focus(selector)
sb.cdp.highlight_overlay(selector)
sb.cdp.get_parent(element)
sb.cdp.remove_element(selector)
sb.cdp.remove_from_dom(selector)
sb.cdp.remove_elements(selector)
sb.cdp.send_keys(selector, text, timeout=None)
sb.cdp.press_keys(selector, text, timeout=None)
sb.cdp.type(selector, text, timeout=None)
sb.cdp.set_value(selector, text, timeout=None)
sb.cdp.submit(selector)
sb.cdp.evaluate(expression)
sb.cdp.js_dumps(obj_name)
sb.cdp.maximize()
sb.cdp.minimize()
sb.cdp.medimize()
sb.cdp.set_window_rect(x, y, width, height)
sb.cdp.reset_window_size()
sb.cdp.open_new_window(url=None, switch_to=True)
sb.cdp.switch_to_window(window)
sb.cdp.switch_to_newest_window()
sb.cdp.open_new_tab(url=None, switch_to=True)
sb.cdp.switch_to_tab(tab)
sb.cdp.switch_to_newest_tab()
sb.cdp.close_active_tab()
sb.cdp.get_active_tab()
sb.cdp.get_tabs()
sb.cdp.get_window()
sb.cdp.get_text(selector)
sb.cdp.get_title()
sb.cdp.get_current_url()
sb.cdp.get_origin()
sb.cdp.get_page_source()
sb.cdp.get_user_agent()
sb.cdp.get_cookie_string()
sb.cdp.get_locale_code()
sb.cdp.get_local_storage_item(key)
sb.cdp.get_session_storage_item(key)
sb.cdp.get_screen_rect()
sb.cdp.get_window_rect()
sb.cdp.get_window_size()
sb.cdp.get_window_position()
sb.cdp.get_element_rect(selector, timeout=None)
sb.cdp.get_element_size(selector, timeout=None)
sb.cdp.get_element_position(selector, timeout=None)
sb.cdp.get_gui_element_rect(selector, timeout=None)
sb.cdp.get_gui_element_center(selector, timeout=None)
sb.cdp.get_document()
sb.cdp.get_flattened_document()
sb.cdp.get_element_attributes(selector)
sb.cdp.get_element_attribute(selector, attribute)
sb.cdp.get_attribute(selector, attribute)
sb.cdp.get_element_html(selector)
sb.cdp.set_locale(locale)
sb.cdp.set_local_storage_item(key, value)
sb.cdp.set_session_storage_item(key, value)
sb.cdp.set_attributes(selector, attribute, value)
sb.cdp.gui_press_key(key)
sb.cdp.gui_press_keys(keys)
sb.cdp.gui_write(text)
sb.cdp.gui_click_x_y(x, y)
sb.cdp.gui_click_element(selector)
sb.cdp.gui_drag_drop_points(x1, y1, x2, y2, timeframe=0.35)
sb.cdp.gui_drag_and_drop(drag_selector, drop_selector, timeframe=0.35)
sb.cdp.gui_click_and_hold(selector, timeframe=0.35)
sb.cdp.gui_hover_x_y(x, y)
sb.cdp.gui_hover_element(selector)
sb.cdp.gui_hover_and_click(hover_selector, click_selector)
sb.cdp.internalize_links()
sb.cdp.is_checked(selector)
sb.cdp.is_selected(selector)
sb.cdp.check_if_unchecked(selector)
sb.cdp.select_if_unselected(selector)
sb.cdp.uncheck_if_checked(selector)
sb.cdp.unselect_if_selected(selector)
sb.cdp.is_element_present(selector)
sb.cdp.is_element_visible(selector)
sb.cdp.is_text_visible(text, selector="body")
sb.cdp.is_exact_text_visible(text, selector="body")
sb.cdp.wait_for_text(text, selector="body", timeout=None)
sb.cdp.wait_for_text_not_visible(text, selector="body", timeout=None)
sb.cdp.wait_for_element_visible(selector, timeout=None)
sb.cdp.wait_for_element_not_visible(selector, timeout=None)
sb.cdp.wait_for_element_absent(selector, timeout=None)
sb.cdp.assert_element(selector, timeout=None)
sb.cdp.assert_element_visible(selector, timeout=None)
sb.cdp.assert_element_present(selector, timeout=None)
sb.cdp.assert_element_absent(selector, timeout=None)
sb.cdp.assert_element_not_visible(selector, timeout=None)
sb.cdp.assert_element_attribute(selector, attribute, value=None)
sb.cdp.assert_title(title)
sb.cdp.assert_title_contains(substring)
sb.cdp.assert_url(url)
sb.cdp.assert_url_contains(substring)
sb.cdp.assert_text(text, selector="html", timeout=None)
sb.cdp.assert_exact_text(text, selector="html", timeout=None)
sb.cdp.assert_text_not_visible(text, selector="body", timeout=None)
sb.cdp.assert_true()
sb.cdp.assert_false()
sb.cdp.assert_equal(first, second)
sb.cdp.assert_not_equal(first, second)
sb.cdp.assert_in(first, second)
sb.cdp.assert_not_in(first, second)
sb.cdp.scroll_into_view(selector)
sb.cdp.scroll_to_y(y)
sb.cdp.scroll_to_top()
sb.cdp.scroll_to_bottom()
sb.cdp.scroll_up(amount=25)
sb.cdp.scroll_down(amount=25)
sb.cdp.save_screenshot(name, folder=None, selector=None)
sb.cdp.print_to_pdf(name, folder=None)
🐙 CDP Mode WebElement API / Methods¶
element.clear_input()
element.click()
element.flash(duration=0.5, color="EE4488")
element.focus()
element.gui_click(timeframe=0.25)
element.highlight_overlay()
element.mouse_click()
element.mouse_drag(destination)
element.mouse_move()
element.press_keys(text)
element.query_selector(selector)
element.querySelector(selector)
element.query_selector_all(selector)
element.querySelectorAll(selector)
element.remove_from_dom()
element.save_screenshot(*args, **kwargs)
element.save_to_dom()
element.scroll_into_view()
element.select_option()
element.send_file(*file_paths)
element.send_keys(text)
element.set_text(value)
element.type(text)
element.get_position()
element.get_html()
element.get_js_attributes()
element.get_attribute(attribute)
element.get_parent()

