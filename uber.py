import csv
import os
import time
import random
import requests
import register_steps as reg_steps
import bypass  
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FOptions
from selenium.webdriver.chrome.options import Options as COptions
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import re
import browser_headers as bh
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def wait_for_element_to_disappear(driver, by, value, timeout=300):
    try:
        # Wait until the element appears
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        print("Element appeared, waiting for it to disappear...")

        # Then wait until it's gone
        WebDriverWait(driver, timeout).until_not(
            EC.presence_of_element_located((by, value))
        )
        print("Element disappeared.")
    except Exception as e:
        print(f"Timeout or error: {e}")

def init_driver_firefox(target_url="https://auth.uber.com/"):
    mobile_emulation = {
    "deviceMetrics": {"width": 375, "height": 812, "pixelRatio": 3.0},  # iPhone X size
    "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) "
                 "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                 "Version/13.0.4 Mobile/15E148 Safari/604.1"
    }
    

    options = FOptions()
    options.add_argument("--start-maximized")

    # Load profile with randomized headers
    profile = FirefoxProfile()
    profile.set_preference("intl.accept_languages", bh.get_random_language())
    # profile_path = os.path.join(userDataDir, profileDir)
    profile.set_preference("general.useragent.override", bh.get_random_user_agent())
  
   # Try to hide automation (partial, not as strong as Chrome)
    profile.set_preference("dom.webdriver.enabled", False)
    profile.set_preference("useAutomationExtension", False)
    profile.set_preference("media.navigator.enabled", False)
    profile.set_preference("webdriver_enable_native_events", False)
    profile.update_preferences()
    driver = webdriver.Firefox(options=options, firefox_profile=profile)
    width, height = map(int, bh.get_random_screen_resolution().split('x'))
    driver.set_window_size(375, 812)
    # Simulate a referrer with JavaScript injection
    driver.get("about:blank")
    referrer = bh.get_random_referrer()
    script = f"""
    Object.defineProperty(document, 'referrer', {{
        get: function() {{ return "{referrer}"; }}
    }});
    var link = document.createElement('a');
    link.href = "{target_url}";
    link.rel = 'noreferrer';
    document.body.appendChild(link);
    link.click();
    """
    driver.execute_script(script)
    time.sleep(2)

    return driver




def init_driver_chrome(target_url="https://auth.uber.com/",profile_dir="Default", user_data_dir="%AppData%\\Local\\Google\\Chrome\\User Data"):
    print("Before init Chrome with undetected-chromedriver")

    # Set up Chrome options
    options = COptions()

    # Language
    options.add_argument(f"--lang={bh.get_random_language()}")

    # User-Agent
    options.add_argument(f"user-agent={bh.get_random_user_agent()}")
    options.add_argument(f"Referer={bh.get_random_referrer()}")

    # Window Size
    window_size = bh.get_random_screen_resolution()
    options.add_argument(f"--window-size={window_size}")

    # Disable automation flags to help hide WebDriver
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    #  Add Chrome profile path
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument(f"--profile-directory={profile_dir}")
    
    # Optional: Headless (uncomment to run in headless mode)
    # options.add_argument("--headless")

    # Initialize undetected Chrome driver
    driver = uc.Chrome(options=options)

    # Manually set window size to ensure compatibility
    width, height = map(int, window_size.split('x'))
    driver.set_window_size(width, height)

    # Inject script to hide webdriver detection
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
    })

    # Simulate a referrer with JavaScript injection
    driver.get("about:blank")
    referrer = bh.get_random_referrer()
    script = f"""
    Object.defineProperty(document, 'referrer', {{
        get: function() {{ return "{referrer}"; }}
    }});
    var link = document.createElement('a');
    link.href = "{target_url}";
    link.rel = 'noreferrer';
    document.body.appendChild(link);
    link.click();
    """
    driver.execute_script(script)
    time.sleep(2)

    return driver




# Create Mail.tm email address
def create_temp_email():
    domain_resp = requests.get("https://api.mail.tm/domains")
    domain = domain_resp.json()['hydra:member'][0]['domain']

    username = f"test{random.randint(10000, 99999)}"
    email = f"{username}@{domain}"
    password = "Test@123456"

    # Register account
    acc_resp = requests.post("https://api.mail.tm/accounts", json={
        "address": email,
        "password": password
    })

    # Wait for account registration to complete
    if acc_resp.status_code != 201:
        raise Exception("Email account creation failed")

    # Get token
    token_resp = requests.post("https://api.mail.tm/token", json={
        "address": email,
        "password": password
    })

    token = token_resp.json()["token"]

    return {
        "email": email,
        "password": password,
        "token": token
    }

# Wait for email and extract 6-digit code
def get_verification_code(token):
    headers = {"Authorization": f"Bearer {token}"}
    headers = {"Authorization": f"Bearer {token}"}
    for _ in range(15):
        inbox = requests.get("https://api.mail.tm/messages", headers=headers).json()
        if inbox['hydra:member']:
            msg_id = inbox['hydra:member'][0]['id']
            msg = requests.get(f"https://api.mail.tm/messages/{msg_id}", headers=headers).json()
            lines = msg['text'].splitlines()
            code_match = re.search(r'\b\d{4}\b', lines[17])
            print(code_match)
            if code_match:
                return code_match.group(0)
        time.sleep(3)
    return None


def save_to_csv(email, password, code, success):
    file_exists = os.path.isfile("accounts.csv")
    with open("accounts.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Email", "Password", "Code", "Verified"])
        writer.writerow([email, password, code if code else "N/A", "Yes" if success else "No"])
 
# --- Main bot logic ---
temp_email = create_temp_email()
print("Temporary email:", temp_email["email"])
print("Temporary password:", temp_email["password"])

driver =init_driver_chrome('https://auth.uber.com/')
time.sleep(3)

print('site accessed')

reg_steps.email_step(driver, temp_email)
time.sleep(3)
#<p tabindex="-1" data-theme="home.instructions" class="sc-1io4bok-0 KalLU sc-d5trka-0 text">Please solve this puzzle so we know you are a real person</p>
wait_for_element_to_disappear(driver, By.ID, "FunCaptcha")
# Wait for email and grab verification code
print("Waiting for verification code email...")
code = get_verification_code(temp_email["token"])


if code:
    print("Verification code received:", code)
    # Paste code into the form
    driver.find_element(By.ID, "EMAIL_OTP_CODE-0").send_keys(code)
    driver.find_element(By.ID, "forward-button").click()
    time.sleep(5)
else:
    print("No verification code received.")



time.sleep(3)


driver.find_element(By.ID, "alt-action-skip").click()


time.sleep(3)

driver.find_element(By.ID, "FIRST_NAME").send_keys("Test")
driver.find_element(By.ID, "LAST_NAME").send_keys("User")
driver.find_element(By.ID, "forward-button").click()

time.sleep(10)

driver.find_element(By.ID, 'LEGAL_ACCEPT_TERMS').click()

time.sleep(5)
driver.find_element(By.ID, "forward-button").click()

save_to_csv(temp_email["email"], temp_email["password"], code, True)

driver.quit()
