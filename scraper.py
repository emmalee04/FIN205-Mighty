import getpass
import requests
import csv
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_page(driver, users, responses):
    feed_cards = driver.find_elements(By.CSS_SELECTOR, 'li.feed-item')
    print(f"Number of feed cards found: {len(feed_cards)}")
    for feed_card in feed_cards:
        # Extract main user name
        user = feed_card.find_element(By.CSS_SELECTOR, 'a.mighty-attribution-name')
        if user:
            user_name = user.text.strip()
            users.add(user_name)

        # Extract responders' names
        comments = feed_card.find_elements(By.CSS_SELECTOR, 'ul.comments-list li.comment-item')
        if comments:
            comment_items = comments.find_all('li', class_='comment-item')
            for comment in comment_items:
                response_user = comment.find('a', class_='author-name')
                if response_user:
                    response_user_name = response_user.text.strip()
                    responses.add(response_user_name)

if __name__ == "__main__":

  email_input = input("Enter your email: ")
  password_input = getpass.getpass("Enter your password: ")

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
  email.send_keys(email_input)
  
  # fill in the password field
  password = driver.find_element(By.CLASS_NAME, "password-input")
  password.send_keys(password_input)

  # submit the login form
  driver.find_element(By.CLASS_NAME, "actions").click()
  time.sleep(5)

  # navigate to wealth & income inequality
  
  feed_url = 'https://personal-finance-literacy.mn.co/spaces/16527694/feed'
  driver.get(feed_url)

  # Wait for the feed page to load
  wait = WebDriverWait(driver, 30)
  try:
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.feed-item")))
    print("Successfully navigated to the feed page")
  except TimeoutException:
    print("Feed page did not load within the expected time")

  time.sleep(5)


  users = set()
  responses = set()

  # scrape_page(driver, users, responses)

  print(users)
  print(responses)

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