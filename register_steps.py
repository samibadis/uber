from selenium import webdriver
from selenium.webdriver.common.by import By
def email_step(driver,temp_email):
    driver.find_element(By.ID, "PHONE_NUMBER_or_EMAIL_ADDRESS").send_keys(temp_email["email"])
    driver.find_element(By.ID, "PHONE_NUMBER_or_EMAIL_ADDRESS").send_keys(webdriver.Keys.ENTER)
