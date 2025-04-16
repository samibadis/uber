import csv
import os
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import re

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
    for _ in range(15):
        inbox = requests.get("https://api.mail.tm/messages", headers=headers).json()
        if inbox['hydra:member']:
            msg_id = inbox['hydra:member'][0]['id']
            msg = requests.get(f"https://api.mail.tm/messages/{msg_id}", headers=headers).json()
            code_match = re.search(r'\b\d{4}\b', msg['text'])
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

driver = webdriver.Firefox()
driver.get("https://auth.uber.com/")  # Replace with your own test site

print('site accessed')

driver.find_element(By.ID, "PHONE_NUMBER_or_EMAIL_ADDRESS").send_keys(temp_email["email"])
driver.find_element(By.ID, "PHONE_NUMBER_or_EMAIL_ADDRESS").send_keys(webdriver.Keys.ENTER)

time.sleep(3)

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


time.sleep(3)

driver.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]').click()

time.sleep(1)
driver.find_element(By.ID, "forward-button").click()

save_to_csv(temp_email["email"], temp_email["password"], code, True)

driver.quit()
