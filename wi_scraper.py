import getpass
import csv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import time
import re

def remove_emoji(string):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F" # emoticons
        u"\U0001F300-\U0001F5FF" # symbols & pictographs
        u"\U0001F680-\U0001F6FF" # transport & map symbols
        u"\U0001F1E0-\U0001F1FF" # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642"
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f" # dingbats
        u"\u3030"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

def scrape_page(driver):
  user_data = {}
  feed_cards = driver.find_elements(By.CLASS_NAME, 'feed-item')
  print(f"Number of feed cards found: {len(feed_cards)}")
  for feed_card in feed_cards:
    # Extract main user name
    user = feed_card.find_element(By.CLASS_NAME, 'mighty-attribution-name')
    if user:
      user_name = user.text.strip()
      user_name = remove_emoji(user_name)
      print(f"user: {user_name}")
      # users.add(user_name)
      if user_name not in user_data:
        user_data[user_name] = [0, 0]
      user_data[user_name][0] += 1  # Increment post count

    # Extract responders' names
    comments = feed_card.find_elements(By.CLASS_NAME, 'comment-item')
    for comment in comments:
      response_user = comment.find_element(By.CLASS_NAME, 'author-name')
      if response_user:
        response_user_name = response_user.text.strip()
        print(f"response user: {response_user_name}")
        # responses.add(response_user_name)
        if response_user_name not in user_data:
          user_data[response_user_name] = [0, 0]
        user_data[response_user_name][1] += 1  # Increment response count
  return [[user, data[0], data[1]] for user, data in user_data.items()]

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
  
  feed_url = 'https://personal-finance-literacy.mn.co/spaces/17645170/feed'
  driver.get(feed_url)

  # Wait for the feed page to load
  wait = WebDriverWait(driver, 30)
  try:
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.feed-item")))
    print("Successfully navigated to the feed page")
  except TimeoutException:
    print("Feed page did not load within the expected time")

  time.sleep(5)

  driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
  last_height = driver.execute_script("return document.body.scrollHeight")
  while True:
    # Scroll down to the bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    
    # Wait for new content to load
    time.sleep(2)
    
    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

  user_data = scrape_page(driver)

  # Open the "wi_users.csv" file and create it if not present
  with open('wi_users.csv', 'w', encoding='utf-8', newline='') as csv_file:
    writer = csv.writer(csv_file)

    writer.writerow(['Name', 'Posts', 'Responses'])
    for user in user_data:
      writer.writerow(user)

  print("Data has been successfully written to wi_users.csv")
  driver.quit()