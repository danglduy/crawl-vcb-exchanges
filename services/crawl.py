import requests
import pandas as pd
import os
import xml.etree.ElementTree as ET
from datetime import datetime


def fetch_exchange_rates():
    """Fetch exchange rates from Vietcombank API"""
    url = "https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx"

    try:
        # Make the request to the API
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the XML response
            return parse_exchange_rates_xml(response.content)
        else:
            print(f"Error: API returned status code {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching exchange rates: {e}")
        return pd.DataFrame()


def parse_exchange_rates_xml(xml_content):
    """Parse the XML content from Vietcombank API"""
    try:
        # Parse XML
        root = ET.fromstring(xml_content)

        # Prepare data structure for DataFrame
        data = []

        # Extract exchange rates
        for exrate in root.findall('.//Exrate'):
            currency_code = exrate.get('CurrencyCode')
            currency_name = exrate.get('CurrencyName')
            currency_en = exrate.get('CurrencyEN')
            buy_cash = exrate.get('Buy')
            buy_transfer = exrate.get('Transfer')
            sell = exrate.get('Sell')

            # Add to data list
            data.append({
                'Mã ngoại tệ': currency_code,
                'Tên ngoại tệ': currency_en,
                'Mua tiền mặt': buy_cash,
                'Mua chuyển khoản': buy_transfer,
                'Bán': sell
            })

        # Create DataFrame
        df = pd.DataFrame(data)

        # Filter out rows with missing sell rates (some currencies don't have all rates)
        df = df[df['Bán'].notnull() & (df['Bán'] != '')]

        return df

    except Exception as e:
        print(f"Error parsing XML: {e}")
        return pd.DataFrame()


def save_to_csv(df, filename):
    """Save DataFrame to CSV and return the absolute path"""
    # Ensure directory exists
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    df.to_csv(filename, index=False)
    return os.path.abspath(filename)


def crawl_vietcombank_exchange_rates(output_path=None):
    """Main function to fetch and extract exchange rates"""
    if output_path is None:
        # Use the default path relative to this file
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(script_dir, 'data')

        # Ensure data directory exists
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        output_path = os.path.join(data_dir, 'vietcombank_exchange_rates.csv')

    try:
        # Fetch exchange rates from API
        df = fetch_exchange_rates()

        if df.empty:
            print("No exchange rate data found")
            return pd.DataFrame()

        # Save to CSV
        save_to_csv(df, output_path)
        print(f"Exchange rates saved to {output_path}")

        return df

    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()


# Run the function when script is executed directly
if __name__ == "__main__":
    crawl_vietcombank_exchange_rates()
