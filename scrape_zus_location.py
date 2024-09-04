from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import json
import time
from tqdm import tqdm
from pprint import pprint


states = ["perlis", "kedah", "penang", "kelantan", "terengganu", "perak", "pahang", "negeri-sembilan",
          "kuala-lumpur-selangor", "pahang", "melaka", "johor", "sarawak", "sabah"]


base_url = r"https://zuscoffee.com/category/store/"


def get_url(state):
    return f"{base_url}{state}"

def get_driver():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    chrome_path = ChromeDriverManager().install()
    if "THIRD_PARTY_NOTICES.chromedriver" in chrome_path:
        chrome_path = chrome_path.replace("THIRD_PARTY_NOTICES.chromedriver", "chromedriver")

    driver = Chrome(service=Service(chrome_path),
                                options=chrome_options)
    
    return driver

# def clean_string(input_str):
#     input_str = input_str.replace("\u2013", "-") # replace unicodes with correct symbol
#     input_str = input_str.replace("\u2019", "'")
    
#     return input_str

def get_store_data(driver, url):
    
    # list to hold individual store data
    individual_state_store_list = []
    
    driver.get(url)
    # driver.maximize_window()

    wait_time = 10
    wait = WebDriverWait(driver, wait_time)  # Wait up to 10 seconds while loading page
    
    # find the next button to navigate through pagination
    find_next_button_xpath = "//nav[@class='elementor-pagination' and @role='navigation']/a[@class='page-numbers next' and @href]"
    
    while True:
        try:
            # print(f"Waiting for up to {wait_time}s for store page to load...")
            store_elements_xpath = "//article[contains(@id, 'post-')]"
            store_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, store_elements_xpath)))
            
            time.sleep(2)
            
            # print(f"Page loaded successfully.")
            for store_element in store_elements:
                
                store_dict = {}
                # grab store name and address from p tags
                p_tags = store_element.find_elements(By.XPATH, ".//p")
                store_name = p_tags[0].text
                               
                store_address = p_tags[1].text
                
                # grab store google map link from 2nd a tag
                store_link = (store_element.find_element(By.XPATH, "(.//a)[2]")).get_attribute("href")
                
                store_dict["store_name"] = store_name
                store_dict["store_address"] = store_address
                store_dict["store_link"] = store_link

                individual_state_store_list.append(store_dict)
                
            # click the "Next" button, if no next button, exit
            try:
                find_next_button = driver.find_element(By.XPATH, find_next_button_xpath)
                driver.execute_script("arguments[0].click();", find_next_button)
                
            except NoSuchElementException:
                break
                
        except TimeoutException:
            print(f"Timeout: Page did not load within {wait_time}. Please check url or extend wait time")
               
    return individual_state_store_list

def write_to_json(full_dict):
    with open("store_data.json", "w") as json_file:
        json.dump(full_dict, json_file, indent=4)

def validate_store_details(full_dict):
    total_store = 0 
    
    for state, v in full_dict["state"].items():
        num_stores = len(v)
        total_store += num_stores
        print(f"State: {state}, Number of Stores: {num_stores}")
        
        for store in v:
            if store["store_name"] == "" or store["store_address"] == "":
                print(f"{store} Empty values detected!")
        
    print(f"Total store count: {total_store}")
    

def main(): 
    
    all_state_store_dict = {
        "state" : {}
    }
    
    for state in tqdm(states, desc="Processing states"):
        url = get_url(state)
        driver = get_driver()
        
        # get store data such as store name, address, google map link
        store_list: list = get_store_data(driver, url) #list of dictionaries
        
        if state not in all_state_store_dict.items():
            all_state_store_dict["state"][state] = {}
        
        
        all_state_store_dict["state"][state] = store_list   
        

        driver.close()
    # pprint(all_state_store_dict)
        
        
    # Dump data into a JSON file
    write_to_json(all_state_store_dict)

    # count how many stores per state and sum of all stores
    # check if there's empty store name or address
    validate_store_details(all_state_store_dict)
    
    
if __name__ == "__main__":
    main()