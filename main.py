from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os


def setup_driver():
    """Set up and return configured WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36")

    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


def navigate_to_page(driver, url, wait_time=5):
    """Navigate to URL and wait for page to load"""
    driver.get(url)

    # Use explicit wait
    wait = WebDriverWait(driver, wait_time)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # Scroll to help load dynamic content
    driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(1)


def find_exchange_rate_table(driver):
    """Find and return the table containing exchange rate data"""
    tables = driver.find_elements(By.TAG_NAME, "table")

    # Find a table that contains currency information
    for table in tables:
        if any(currency in table.text for currency in ["USD", "EUR", "JPY"]):
            return table

    return None


def extract_table_data(table):
    """Extract data from a table element and return headers and data rows"""
    rows = table.find_elements(By.TAG_NAME, "tr")

    # Extract headers
    header_row = rows[0]
    header_cells = header_row.find_elements(By.TAG_NAME, "th")

    if not header_cells:
        # If no th elements, try td elements
        header_cells = header_row.find_elements(By.TAG_NAME, "td")

    # Get headers
    headers = [cell.text for cell in header_cells]

    # Extract data rows
    data = []
    for row in rows[1:]:  # Skip header row
        cells = row.find_elements(By.TAG_NAME, "td")
        if cells:
            row_data = [cell.text for cell in cells]
            data.append(row_data)

    return headers, data


def save_to_csv(df, filename="vietcombank_exchange_rates.csv"):
    """Save DataFrame to CSV and return the absolute path"""
    df.to_csv(filename, index=False)
    return os.path.abspath(filename)


def crawl_vietcombank_exchange_rates():
    """Main function to crawl and extract exchange rates"""
    driver = None

    try:
        # Setup and navigate
        driver = setup_driver()
        url = "https://www.vietcombank.com.vn/vi-VN/KHCN/Cong-cu-Tien-ich/Ty-gia"
        navigate_to_page(driver, url, wait_time=1)

        # Find and extract data
        exchange_table = find_exchange_rate_table(driver)

        if not exchange_table:
            print("No currency exchange table found.")
            return pd.DataFrame()

        # Extract data from table
        headers, data = extract_table_data(exchange_table)

        # Create DataFrame
        df = pd.DataFrame(data, columns=headers)
        return df

    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()
    finally:
        if driver:
            driver.quit()


# Run the function when script is executed directly
if __name__ == "__main__":
    print("Starting exchange rate extraction...")
    exchange_rates = crawl_vietcombank_exchange_rates()

    if not exchange_rates.empty:
        print("\nExchange rates data:")
        print(exchange_rates)

        # Save to CSV
        csv_path = save_to_csv(exchange_rates)
        print(f"Data saved to {csv_path}")
    else:
        print("No data found")
