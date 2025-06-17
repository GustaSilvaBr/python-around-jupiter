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
LESSON_PLAN_FILE = "lesson_plans/"+"current.csv"


def setup_browser():
    """Initializes and returns the Selenium browser instance."""
    print("Setting up browser...")
    try:
        browser = webdriver.Chrome()
        return browser
    except Exception as e:
        print(f"Error setting up browser: {e}")
        return None


def login_to_jupiter(browser, username, password):
    """
    Navigates to the login page, fills credentials, and waits for the user
    to manually enter the access code to complete the login.
    """
    print("Executing login sequence...")
    browser.get("https://login.jupitered.com/login/")
    wait = WebDriverWait(browser, 15)

    # --- Login logic ---
    staff_tab = wait.until(EC.element_to_be_clickable((By.ID, "tab_staff")))
    staff_tab.click()
    browser.find_element(By.ID, "text_username1").send_keys(username)
    browser.find_element(By.ID, "text_password1").send_keys(password)
    
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


def load_lesson_plan_data(file_path):
    print(f"Loading lesson plan data from {file_path}...")
    
    # Define the set of required column names for validation
    required_columns = {
        'unit', 'date', 'lesson', 'objectives', 'procedures', 
        'assessment', 'materials', 'course', 'quarter'
    }
    
    try:
        df = pd.read_csv(file_path)
        
        # Validate if the columns in the CSV match the required columns
        if set(df.columns) != required_columns:
            missing = required_columns - set(df.columns)
            extra = set(df.columns) - required_columns
            error_message = "Error: CSV columns do not match the required format."
            if missing:
                error_message += f"\nMissing columns: {sorted(list(missing))}"
            if extra:
                error_message += f"\nUnexpected columns: {sorted(list(extra))}"
            print(error_message)
            return None

        # If columns are correct, proceed with processing
        print("Columns validated successfully.")
        df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y') 
        df.fillna('', inplace=True)
        print("Data loaded and processed successfully.")
        return df
        
    except FileNotFoundError:
        print(f"Error: The file was not found at {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred while loading or processing the data: {e}")
        return None


def navigate_to_lesson_area(browser):
    print("Navigating to the main lesson plan area...")
    wait = WebDriverWait(browser, 20)
    
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'More')]"))).click()

    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Lesson Plans')]"))).click()
    
    wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Edit Lessons')]")))
    
    print("Successfully navigated to the lesson plan area.")


def fill_lesson_form_for_row(browser, lesson_details):
    #SELECIONAR O QUARTER
    
    wait = WebDriverWait(browser, 15)
    lesson_date_str = lesson_details['date'].strftime('%m/%d/%Y') 
    course_name = lesson_details['course']
    
    print(f"Processing lesson for '{course_name}' on {lesson_date_str}...")

    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Edit Lessons')]"))).click()

    wait.until(EC.visibility_of_element_located((By.ID, "text_unit")))
    
    print(" -> Filling out the form...")
    booktab = wait.until(EC.element_to_be_clickable((By.ID, "booktab")))
    
    if lesson_details['quarter'] != booktab.text:
        print("Lesson detail quarter: " + lesson_details['quarter'])
        print("booktab text: " + booktab.text)
        booktab.click()
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(), '{lesson_details['quarter']}')]"))).click()

    wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[text()='{lesson_details['course']}']"))).click()

    wait.until(EC.visibility_of_element_located((By.ID, "text_unit")))

    #browser.find_element(By.ID, "text_unit").send_keys(lesson_details['unit'])
    current_field = wait.until(EC.element_to_be_clickable((By.ID, "text_unit")))
    current_field.clear()
    current_field.send_keys(lesson_details['unit'])


    #browser.find_element(By.ID, "text_title").send_keys(lesson_details['lesson'])
    current_field = wait.until(EC.element_to_be_clickable((By.ID, "text_title")))
    current_field.clear()
    current_field.send_keys(lesson_details['lesson'])

    #browser.find_element(By.ID, "text_date1").send_keys(lesson_date_str)
    current_field = wait.until(EC.element_to_be_clickable((By.ID, "text_date1")))
    current_field.clear()
    current_field.send_keys(lesson_date_str)

    #browser.find_element(By.ID, "text_date2").send_keys(lesson_date_str)
    current_field = wait.until(EC.element_to_be_clickable((By.ID, "text_date2")))
    current_field.clear()
    current_field.send_keys(lesson_date_str)


    #browser.find_element(By.ID, "text_goals").send_keys(lesson_details['objectives'])
    current_field = wait.until(EC.element_to_be_clickable((By.ID, "text_goals")))
    current_field.clear()
    current_field.send_keys(lesson_details['objectives'])

    #browser.find_element(By.ID, "text_procedures").send_keys(lesson_details['procedures'])
    current_field = wait.until(EC.element_to_be_clickable((By.ID, "text_procedures")))
    current_field.clear()
    current_field.send_keys(lesson_details['procedures'])
    
    #browser.find_element(By.ID, "text_assessment").send_keys(lesson_details['assessment'])
    current_field = wait.until(EC.element_to_be_clickable((By.ID, "text_assessment")))
    current_field.clear()
    current_field.send_keys(lesson_details['assessment'])

    #browser.find_element(By.ID, "text_materials").send_keys(lesson_details['materials'])
    current_field = wait.until(EC.element_to_be_clickable((By.ID, "text_materials")))
    current_field.clear()
    current_field.send_keys(lesson_details['materials'])
    
    browser.find_element(By.XPATH, "//div[contains(text(), 'Done')]").click()

    # Step 5: Wait for the form to disappear, confirming submission.
    wait.until(EC.invisibility_of_element_located((By.ID, "text_unit")))
    print(" -> Successfully submitted lesson.")


def create_all_lesson_entries(browser, lesson_dataframe):
    print("\nStarting to process all lesson plans from the data file...")
    if lesson_dataframe is None or lesson_dataframe.empty:
        print("No lesson data to process.")
        return

    for index, lesson_row in lesson_dataframe.iterrows():
        try:
            fill_lesson_form_for_row(browser, lesson_row)
        except Exception as e:

            date_str = lesson_row['date'].strftime('%Y-%m-%d')
            course = lesson_row['course']
            print(f"---! ERROR processing lesson for '{course}' on {date_str}: {e}")
            print("---! The script will attempt to close the form and continue with the next lesson.")
            # Attempt to refresh or go back to escape a broken state
            browser.refresh() 
            # It's important to wait for the page to be ready again after a refresh
            time.sleep(5)
            continue


def main():
    """Main function to orchestrate the automation."""
    browser = None
    try:
        browser = setup_browser()
        if not browser:
            return

        login_to_jupiter(browser, JUPITER_USERNAME, JUPITER_PASSWORD)
        
        all_lesson_data = load_lesson_plan_data(LESSON_PLAN_FILE)
        if all_lesson_data is None:
            print("Could not load lesson data. Exiting.")
            return

        # Navigate to the single, main lesson plan area
        navigate_to_lesson_area(browser)

        # Process all lessons from the file sequentially
        create_all_lesson_entries(browser, all_lesson_data)
        
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
