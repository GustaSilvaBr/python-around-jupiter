import os
from dotenv import find_dotenv, load_dotenv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

JUPITER_USERNAME = os.getenv("JUPITER_USERNAME")
JUPITER_PASSWORD = os.getenv("PASSWORD")
print("PASS: "+JUPITER_PASSWORD)
LESSON_PLAN_FILE = "lesson_plans/"+"Q3_ALL_TOGETHER.csv"


def setup_browser():
    print("Setting up browser...")
    try:
        browser = webdriver.Chrome()
        return browser
    except Exception as e:
        print(f"Error setting up browser: {e}")
        return None


def login_to_jupiter(browser, username, password):
    print("Executing login sequence...")
    browser.get("https://login.jupitered.com/login/")
    wait = WebDriverWait(browser, 10)

    staff_tab = wait.until(EC.element_to_be_clickable((By.ID, "tab_staff")))
    staff_tab.click()
    browser.find_element(By.ID, "text_username1").send_keys(username)
    browser.find_element(By.ID, "text_password1").send_keys(password)
    browser.find_element(By.ID, "timeoutin1_label").click()
    lock_for_60min = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(), '60 minutes')]")))
    lock_for_60min.click()
    browser.find_element(By.ID, "loginbtn").click()
    
    print("\n" + "="*50)
    print("ACTION REQUIRED: Please enter the access code in the browser.")
    print("The script will wait up to 5 minutes for you to log in.")
    print("="*50 + "\n")
    
    try:
        login_wait = WebDriverWait(browser, 300)
        login_wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Logout')]")))
        print("Login successful.")
    except TimeoutException:
        print("Timed out waiting for login to complete. Exiting.")
        raise

def navigate_to_lesson_area(browser):
    wait = WebDriverWait(browser, 15)
    wait.until(EC.element_to_be_clickable((By.ID, "booktab"))).click()
    # quarter_id = "3rd Quarter, 2024-25 HS"
    wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(), '3rd Quarter, 2024-25 HS')]"))).click()
    
    print("Navigating to the main lesson plan area...")
    wait = WebDriverWait(browser, 20)
    
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'More')]"))).click()

    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Lesson Plans')]"))).click()
    
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Edit Lessons')]"))).click()
    
    wait.until(EC.visibility_of_element_located((By.ID, "text_unit")))
    
    print(" -> Filling out the form...")
    
    print("Successfully navigated to the lesson plan area.")

def getText(element):
    return element.text

def deletion(browser, course):
    
    wait = WebDriverWait(browser, 15)
    print(f"\n--- Starting deletion process for course: {course} ---")

    try:
        # Step 1: Select the course from the dropdown menu.
        print(f"Selecting course: {course}...")
        
        
        # From the now-visible list, click on the target course.
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[text()='{course}']"))).click()
        wait.until(EC.visibility_of_element_located((By.ID, "text_unit")))
        
        print(f"Successfully selected course '{course}'.")
        # Wait a moment for the lesson content for the new course to load.
        time.sleep(2)

    except TimeoutException:
        print(f"Error: Could not find or select the course '{course}'.")
        print("Please ensure the course name is correct and visible on the page.")
        return # Exit if the course cannot be selected.

    print("Searching for lessons to delete...")
    try:
        wait.until(EC.element_to_be_clickable((By.ID, "lesson_label"))).click()
        menu_container = wait.until(EC.visibility_of_element_located((By.ID, "menulist_lesson")))
        items = menu_container.find_elements(By.XPATH, ".//div[contains(@class, 'menurow') or contains(@class, 'menuun')]")
        index = 0
       
        if type(items) == list:
            only_texts = list(map(getText,items))
            total = len(only_texts)
            #print("ONLY TEXTS: ", only_texts)
            while(index < total):
                print("CONTAGEM: ", index)
                item_text = only_texts[index]
                print("ITEM_TEXT: ", item_text)
                item = browser.find_element(By.XPATH, f"//div[text()='{item_text}']")
                print("TEXTO DO ITEM: ", item.text.lower())
                item_class = item.get_attribute("class")
                print("ITEM FOUND")
                time.sleep(1.5)
                if 'menuun' in item_class:
                    print("It broke here")
                    break

                if 'menurow' in item_class and '2025' in item_text.lower():
                    item.click()
                    delete_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Delete']")))
                    delete_button.click()
                    delete_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='right']//div[text()='Delete']")))
                    delete_button.click()
                    
                    wait.until(EC.visibility_of_element_located((By.ID, "text_unit")))
                    
                    delete_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Done']")))
                    delete_button.click()
                    delete_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Edit Lessons']")))
                    delete_button.click()
                    print("EU ESTOU AQUI")
                    delete_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='New Lesson Plan']")))
                    delete_button.click()
                    print("EU ESTOU AQUI AGORA")
                    index = index + 1
                    #An unexpected error occurred in the deletion loop: Message: no such element: Unable to locate element: {"method":"xpath","selector":"//div[text()='№ 3; 3/2/2025: Introduction to Programming With Lua']"}
                else:
                    index = index + 1
                print("QUASE LÁ GUSTAVOOO")
                time.sleep(1.5)
                
    except Exception as e:
        print(f"An unexpected error occurred in the deletion loop: {e}")
        print("Continuing to the next course if available.")
           
    print(f"--- Deletion process finished for course: {course} ---")                
                

def main():
    browser = None
    try:
        browser = setup_browser()
        if not browser:
            return

        login_to_jupiter(browser, JUPITER_USERNAME, JUPITER_PASSWORD)
        
        navigate_to_lesson_area(browser)
        
        deletion(browser, "CP_9")

        print("\nAutomation complete for all courses!")

    except Exception as e:
        print(f"\nAn unexpected error occurred in the main process: {e}")
    finally:
        if browser:
            print("Closing browser in 15 seconds...")
            time.sleep(15)
            browser.quit()


if __name__ == "__main__":
    main()
