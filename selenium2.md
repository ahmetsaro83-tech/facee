Key Tactics and Tips:
Bypassing Bot Detection on ChatGPT: The video demonstrates using SeleniumBase's special "CDP Mode" (Chrome DevTools Protocol) to successfully query and scrape data from ChatGPT. This mode is designed to make the automation appear more human-like, thus bypassing the anti-bot defenses that websites like ChatGPT employ. The key is to activate CDP mode (sb.activate_cdp_mode()) after navigating to the URL.
Automating ChatGPT in GitHub Actions: A significant tactic shown is that this ChatGPT scraping script can be run directly within GitHub Actions. This allows for automated, scheduled, and free web scraping and data interaction with AI models without needing your own server. The video shows a successful GitHub Actions run where the script queries ChatGPT and prints the response in the logs.
Performance Comparison (SeleniumBase vs. Playwright): The presenter has created a dedicated GitHub repository (playwright-vs-seleniumbase) to benchmark the performance of these two frameworks. The results, gathered from automated runs in GitHub Actions, show that the "winner" depends on the operating system and the specific task:
Linux (Ubuntu): Performance is very close and depends on the use case. For single test flows, Playwright can be slightly faster, but for running multiple tests in parallel (multi), SeleniumBase shows a speed advantage.
macOS: SeleniumBase demonstrates a significant speed advantage over Playwright, especially when running multiple tests concurrently.
Windows: Playwright is generally faster than SeleniumBase.
Handling Dynamic Content: When scraping ChatGPT, the script waits for the "Stop button" to disappear before attempting to read the response. This is a good tactic for dealing with dynamic web pages where content is generated or typed out in real-time. It ensures the script only proceeds after the full response has been rendered.
Undetected-Testing Repository: The presenter highlights his GitHub repository named undetected-testing, which contains numerous examples of scripts (including the ChatGPT one) designed to bypass bot detection on various popular websites like Nike and Priceline.
Code Snippets:
1. Raw ChatGPT Scraping Script (using SeleniumBase CDP Mode)
This script navigates to ChatGPT, uses a stealth mode to bypass bot detection, types a query, and scrapes the resulting answer.
code
Python
from seleniumbase import SB

# Using a "with" statement and UC Mode to bypass bot detection
with SB(uc=True, test=True, ad_block=True) as sb:
    url = "https://chatgpt.com/"
    sb.activate_cdp_mode() # Activate Chrome DevTools Protocol Mode
    sb.sleep(1)

    # If a "Close dialog" button is visible, click it
    sb.click_if_visible('button[aria-label="Close dialog"]')

    # Define the query and type it into the text area
    query = "Compare Playwright to SeleniumBase in under 178 words"
    sb.press_keys("#prompt-textarea", query)
    sb.click('button[data-testid="send-button"]')
    
    print(f"*** Input for ChatGPT: ***\n\n{query}")
    sb.sleep(3)

    # Wait for the "Stop button" to disappear (meaning the response is complete)
    # The suppress(Exception) handles cases where the button might not appear at all
    with sb.suppress(Exception):
        sb.wait_for_element_not_visible(
            'button[data-testid="stop-button"]', timeout=20
        )

    # Find the response element, get its HTML, parse it, and print the clean text
    chat = sb.find_element('[data-message-author-role="assistant"] .markdown')
    soup = sb.get_beautiful_soup(chat.get_attribute("innerHTML"))
    response = soup.get_text().strip()
    print(f"*** Response from ChatGPT: ***\n\n{response}")
    sb.sleep(3)
2. Performance Test Script Structure (SeleniumBase Example)
This shows the basic structure used for the multi-test performance benchmark, utilizing pytest.
code
Python
import pytest

# Pytest main entry point to run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-rs", "-chs", "--pls=none"])

# Test function 1
def test_1(sb):
    sb.driver.get("https://www.saucedemo.com")
    print(sb.driver.current_url)

# Test function 2
def test_2(sb):
    sb.driver.get("https://material.angular.io")
    print(sb.driver.current_url)

# Test function 3
def test_3(sb):
    sb.driver.get("https://www.openstreetmap.org/help")
    print(sb.driver.current_url)
3. Performance Test Script Structure (Playwright Example)
This is the Playwright equivalent of the multi-test benchmark script, also using pytest.
code
Python
import pytest

# Note: The video mentions that pytest-playwright and SeleniumBase
# cannot be installed in the same environment due to overlapping arguments.

# Pytest main entry point
if __name__ == "__main__":
    pytest.main([__file__])

# Test function 1
def test_1(page):
    page.goto("https://www.saucedemo.com")
    print(page.url)

# Test function 2
def test_2(page):
    page.goto("https://material.angular.io")
    print(page.url)

# Test function 3
def test_3(page):
    page.goto("https://www.openstreetmap.org/help")
    print(page.url)