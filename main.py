import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from src.access_email import get_login_code
# what ok
from src.config import WEB_APP_PASSWORD, WEB_APP_USERNAME, MAILBOX_PASSWORD, MAILBOX_USERNAME, Player_name, Max_buynow, PLAYERS_TO_BUY

def no_results_found(driver):
    try:
        driver.find_element(By.XPATH, "//h2[text()='No results found']")
        return True
    except NoSuchElementException:
        return False

def check_item_bought(wait, old_balance, max_buy_now):
    try:
        max_buy_now = int(max_buy_now)
        # Wait for the coin balance to update
        new_balance_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.view-navbar-currency-coins")))
        new_balance = int(new_balance_element.text.replace(',', ''))  # Remove commas for thousands

        # Check if the new balance is less than the old balance by the buy now price
        if new_balance <= old_balance - max_buy_now:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking if item was bought: {e}")
        return False


def attempt_to_buy(wait, old_balance, max_buy_now):
    # Attempt to buy the item
    try:
        # Wait for the "Buy Now" button to be clickable
        buy_now_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-standard.buyButton.currency-coins")))
        buy_now_button.click()

        # Wait for a moment to let the coin balance update
        time.sleep(2)  

        ok_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Ok']]")))
        ok_button.click()

        # Wait for a moment to let the transaction complete and the balance to update
        time.sleep(5)

        back_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ut-navigation-button-control")))
        back_button.click()

        return check_item_bought(wait, old_balance, max_buy_now)
    except NoSuchElementException:
        # If the "Buy Now" button is not found, return False
        return False
    except Exception as e:
        print(f"Error attempting to buy: {e}")
        return False





def main():
    # Set up the driver
    service = Service(executable_path='C:\\Program Files (x86)\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe')
    driver = webdriver.Chrome(service=service)

    # Open the website
    driver.get('https://signin.ea.com/p/juno/login?execution=e31734922s1&initref=https%3A%2F%2Faccounts.ea.com%3A443%2Fconnect%2Fauth%3Fhide_create%3Dtrue%26display%3Dweb2%252Flogin%26scope%3Dbasic.identity%2Boffline%2Bsignin%2Bbasic.entitlement%2Bbasic.persona%26release_type%3Dprod%26response_type%3Dtoken%26redirect_uri%3Dhttps%253A%252F%252Fwww.ea.com%252Fea-sports-fc%252Fultimate-team%252Fweb-app%252Fauth.html%26accessToken%3D%26locale%3Den_US%26prompt%3Dlogin%26client_id%3DFC24_JS_WEB_APP')

    wait = WebDriverWait(driver, 10)  # wait for up to 10 seconds
    players_to_buy = PLAYERS_TO_BUY
    players_bought = 0

    try:
        username_elem = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="email"]')))
        password_elem = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="password"]')))
        login_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="logInBtn"]')))

        username_elem.send_keys(WEB_APP_USERNAME)
        password_elem.send_keys(WEB_APP_PASSWORD)
        login_button.click()
        
        button = driver.find_element(By.XPATH, '//*[@id="btnSendCode"]')
        button.click()
        
        time.sleep(15)


        code = get_login_code(MAILBOX_USERNAME, MAILBOX_PASSWORD)
        
        input_field = driver.find_element(By.XPATH, '//*[@id="twoFactorCode"]')
        input_field.send_keys(str(code))
        button = driver.find_element(By.XPATH, '//*[@id="btnSubmit"]')
        button.click()

        time.sleep(10)
        button = driver.find_element(By.XPATH, '//*[@id="Login"]/div/div/button[1]')
        button.click()
        
        time.sleep(10)

        transfers_button_xpath = "//button[.//span[text()='Transfers']]"
        transfers_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, transfers_button_xpath))
        )
        transfers_button.click()

        time.sleep(6)

        transfer_market_div_class = "ut-tile-transfer-market"
        wait = WebDriverWait(driver, 10) 
        transfer_market_div = wait.until(
        EC.visibility_of_element_located((By.CLASS_NAME, transfer_market_div_class))
        )
        transfer_market_div.click()

        time.sleep(6)

        player_name_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input.ut-text-input-control[placeholder="Type Player Name"]')))
        player_name_input.send_keys(Player_name)

        time.sleep(5)

        button_with_text = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "ul.ut-button-group.playerResultsList button:nth-of-type(1)"))
        )
        button_with_text.click()

        time.sleep(5)

        # Enter Max Buy Now Price
        max_price_input = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "ut-number-input-control"))
        )

        # Target the fourth input
        fourth_price_input = max_price_input[3]

        # Click the input to focus, clear it, and then set the value
        fourth_price_input.click()
        fourth_price_input.send_keys(Max_buynow)

        time.sleep(5)
        

        old_balance_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.view-navbar-currency-coins")))
        old_balance = int(old_balance_element.text.replace(',', ''))  # Remove commas for thousands
        print(f"Old balance: {old_balance}")

# Enter the search and buy loop
        while players_bought < players_to_buy:
            # Click the search button
            search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Search')]")))
            search_button.click()

            # Wait for the search results to load or for the "No results found" message
            time.sleep(2)  # Adjust this sleep as necessary for the page to load

            # Check for "No results found" message
            if no_results_found(driver):
                # Go back and wait 30 seconds before searching again
                back_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ut-navigation-button-control")))
                back_button.click()
                wait_time = random.randint(18, 30)
                time.sleep(wait_time)
                continue

            # Attempt to buy the item
            item_bought = attempt_to_buy(wait, old_balance, Max_buynow)

            if item_bought:
                # If the item was bought, increment the counter
                players_bought += 1
                print(f"Player bought successfully. Total players bought: {players_bought}")
                # Update the old balance after a successful purchase
                old_balance_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.view-navbar-currency-coins")))
                old_balance = int(old_balance_element.text.replace(',', ''))  # Remove commas for thousands

                wait_time = random.randint(18, 30)  # This will wait for a random time between 18 and 30 seconds
                time.sleep(wait_time)

                if players_bought >= players_to_buy:
                    print("Reached the target number of players to buy.")
                    break
            else:
                # If the item wasn't bought, find and click the back button
                back_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ut-navigation-button-control")))
                back_button.click()

            # Add a delay to prevent too frequent requests
            time.sleep(1)

    except Exception as e:
        print(f"An error occurred: {e}")

    driver.quit()
    

if __name__ == "__main__":
    main()
