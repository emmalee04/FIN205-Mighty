import requests
import csv
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_page(soup, users, responses):
    feed_cards = soup.find_all('li', class_='feed-item')
    print(f"Number of feed cards found: {len(feed_cards)}")
    for feed_card in feed_cards:
        # Extract main user name
        user = feed_card.find('a', class_='mighty-attribution-name')
        if user:
            user_name = user.text.strip()
            users.add(user_name)

        # Extract responders' names
        comments = feed_card.find('ul', class_='comments-list')
        if comments:
            comment_items = comments.find_all('li', class_='comment-item')
            for comment in comment_items:
                response_user = comment.find('a', class_='author-name')
                if response_user:
                    response_user_name = response_user.text.strip()
                    responses.add(response_user_name)

if __name__ == "__main__":

  # Retrieve page & parse
  options = uc.ChromeOptions()
  options.headless = False

  driver = uc.Chrome(
      use_subprocess=False,
      options=options,
  )

  driver.get('https://personal-finance-literacy.mn.co/sign_in#_gl=1*1tnfbh0*_ga*MTQ4NTMyNDg2NC4xNzMzMjUyNDY4*_ga_T49FMYQ9FZ*MTczMzI1ODYwMS4yLjEuMTczMzI1ODkwNy4wLjAuMA..*_ga_NEGJ2SXNP7*MTczMzI1ODYwMS4yLjEuMTczMzI1ODkwNy40My4wLjA.')

  # fill in the email field
  email = driver.find_element(By.CLASS_NAME, "email-input")
  email.send_keys("slee04@uw.edu")
  
  # fill in the password field
  password = driver.find_element(By.CLASS_NAME, "password-input")
  password.send_keys("Emmerthewheat2004!")

  # submit the login form
  driver.find_element(By.CLASS_NAME, "actions").click()
  time.sleep(5)

  # navigate to wealth & income inequality
  # driver.find_element(By.CSS_SELECTOR, "div.iBfMvEeuuz3wuXRxWVoV.v7J_BVc0_lX7U0MCslGA.qOUm2VYYHK9kmAWnIpTV.selected").click()
  # time.sleep(5)

  assignment_tab = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "div.iBfMvEeuuz3wuXRxWVoV.v7J_BVc0_lX7U0MCslGA.qOUm2VYYHK9kmAWnIpTV.selected"))
  )

  # Click the Feed tab
  assignment_tab.click()

  # Wait for the new page to load
  WebDriverWait(driver, 10).until(
    EC.url_contains("https://personal-finance-literacy.mn.co/spaces/16527694/page")
  )

  feed_tab = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "div.IrT8wZUpENfgA4h4tZdZ.ZN2JhFu3bpToBNa9PGgt a.flex-space-tab-link"))
  )

  # Click the Feed tab
  feed_tab.click()

  # Wait for the new page to load
  WebDriverWait(driver, 10).until(
    EC.url_contains("https://personal-finance-literacy.mn.co/spaces/16527694/feed")
  )


# users = set()
# responses = set()

# scrape_page(soup, users, responses)

# print(users)
# print(responses)

# # Open the "users.csv" file and create it if not present
# with open('users.csv', 'w', encoding='utf-8', newline='') as csv_file:
#     writer = csv.writer(csv_file)
    
#     # Writing the header of the CSV file
#     writer.writerow(['User Type', 'Name'])
    
#     # Writing each row of the CSV
#     for user in users:
#         writer.writerow(['Post Author', user])
    
#     for response in responses:
#         writer.writerow(['Responder', response])

# print("Data has been successfully written to users.csv")