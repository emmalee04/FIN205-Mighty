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
    last_height = driver.execute_script("return document.body.scrollHeight")  # Get initial page height
    feed_cards = []

    while True:
        # Find all feed cards currently loaded
        current_feed_cards = driver.find_elements(By.CLASS_NAME, 'feed-item')
        print(f"Number of feed cards found so far: {len(current_feed_cards)}")

        # Add new feed cards to the list (avoid duplicates)
        for card in current_feed_cards:
            if card not in feed_cards:
                feed_cards.append(card)

        # Scroll down to load more content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for new content to load

        # Check if we've reached the bottom of the page
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # Exit loop if no new content is loaded
        last_height = new_height

    print(f"Total number of feed cards found: {len(feed_cards)}")

    # Process each feed card
    for feed_card in feed_cards:
        try:
            # Extract main user name
            user = feed_card.find_element(By.CLASS_NAME, 'mighty-attribution-name')
            if user:
                user_name = user.text.strip()
                user_name = remove_emoji(user_name)
                print(f"user: {user_name}")
                if user_name not in user_data:
                    user_data[user_name] = [0, []]  # [post count, character counts]
                user_data[user_name][0] += 1  # Increment post count

                # Extract main post text for character count
                try:
                    post_text_element = feed_card.find_element(By.CSS_SELECTOR,
                        '.feed-item-post-description.mighty-wysiwyg-content.fr-view')
                    if post_text_element:
                        post_text = post_text_element.text.strip()
                        # Remove '…continue' if present
                        if '…continue' in post_text:
                            post_text = post_text.split('…continue')[0].strip()
                        user_data[user_name][1].append(len(post_text))  # Append character count of post
                except Exception as e:
                    print(f"Error extracting post text for {user_name}: {e}")
                    user_data[user_name][1].append(0)  # Append 0 if post text not found
        except Exception as e:
            print(f"Error extracting user or post count: {e}")

    formatted_data = []
    for user, data in user_data.items():
        character_counts_str = ', '.join(map(str, data[1])) if data[1] else '0'
        formatted_data.append([user, data[0], character_counts_str])

    return formatted_data


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

  # navigate to savings tips & tricks
  
  feed_url = 'https://personal-finance-literacy.mn.co/spaces/17645182/feed'
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

  # Open the "savings_users.csv" file and create it if not present
  with open('savings_users.csv', 'w', encoding='utf-8', newline='') as csv_file:
    writer = csv.writer(csv_file)

    writer.writerow(['Name', 'Posts', 'Character Counts'])
    for user in user_data:
      writer.writerow(user)

  print("Data has been successfully written to savings_users.csv")
  driver.quit()