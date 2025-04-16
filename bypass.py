from selenium.common.exceptions import NoSuchElementException
import time
def check_captcha(driver, timeout=5):
 
    while True:
        try:
            driver.find_element("xpath", "//*[contains(@id, 'FunCaptcha')]")
            print(f"[DETECTED] FunCaptcha is still present. Waiting {timeout}s...")
            time.sleep(timeout)
        except NoSuchElementException:
            print("[OK] FunCaptcha is gone. Proceeding.")
            break