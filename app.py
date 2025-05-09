from flask import Flask, render_template, jsonify
import pandas as pd
import os
import time
from services.crawl import crawl_vietcombank_exchange_rates

app = Flask(__name__)


# Function to get the path to the CSV file
def get_csv_path():
    # Create the data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    return os.path.join(data_dir, 'vietcombank_exchange_rates.csv')


# Function to load the exchange rate data
def load_exchange_rates():
    csv_path = get_csv_path()

    # Check if the CSV file exists, if not, crawl the data first
    if not os.path.exists(csv_path):
        print("Exchange rate CSV not found. Crawling data...")
        df = crawl_vietcombank_exchange_rates(csv_path)
        if df.empty:
            print("Warning: Failed to crawl initial exchange rate data.")
            return pd.DataFrame()

    try:
        # Load CSV
        df = pd.read_csv(csv_path)
        # Convert the 'Bán' (selling) rate column to numeric values
        # Remove any commas in the values
        df['Bán'] = df['Bán'].str.replace(',', '').astype(float)
        return df
    except Exception as e:
        print(f"Error loading exchange rates: {e}")
        return pd.DataFrame()


# Route for main page
@app.route('/')
def index():
    # Load exchange rates
    df = load_exchange_rates()

    # Prepare data for the template
    currencies = []

    if not df.empty:
        # Create a list of dictionaries with currency code and name
        currencies = [
            {'code': row['Mã ngoại tệ'],
             'name': row['Tên ngoại tệ'],
             'rate': row['Bán']}
            for _, row in df.iterrows()
        ]

    return render_template('index.jinja2', currencies=currencies)


# API route to get the rate for a specific currency
@app.route('/api/rate/<currency_code>')
def get_rate(currency_code):
    df = load_exchange_rates()

    if df.empty:
        return jsonify({"error": "Exchange rate data not available"}), 404

    # Find the currency in the dataframe
    currency_data = df[df['Mã ngoại tệ'] == currency_code]

    if currency_data.empty:
        return jsonify({"error": f"Currency {currency_code} not found"}), 404

    # Return the selling rate
    rate = currency_data.iloc[0]['Bán']
    return jsonify({"rate": rate})


# API endpoint to refresh exchange rates by calling the API
@app.route('/api/refresh', methods=['POST'])
def refresh_rates():
    try:
        # Get the CSV path
        csv_path = get_csv_path()

        # Fetch new rates from API
        print("Refreshing exchange rates from Vietcombank API...")
        df = crawl_vietcombank_exchange_rates(csv_path)

        if df.empty:
            return jsonify({"success": False, "message": "Failed to load updated rates"}), 500

        # Convert the 'Bán' (selling) rate column to numeric values
        df['Bán'] = df['Bán'].str.replace(',', '').astype(float)

        # Prepare updated currency data
        currencies = [
            {'code': row['Mã ngoại tệ'],
             'name': row['Tên ngoại tệ'],
             'rate': row['Bán']}
            for _, row in df.iterrows()
        ]

        return jsonify({
            "success": True,
            "message": "Exchange rates refreshed successfully",
            "currencies": currencies
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500


if __name__ == '__main__':
    # Ensure services directory exists
    if not os.path.exists('services'):
        os.makedirs('services')

    # Make sure we have initial data
    load_exchange_rates()

    # Start the Flask app
    app.run(debug=True)
