from flask import Flask, render_template, jsonify, request
import pandas as pd
import os
import subprocess
import time

app = Flask(__name__)

# Function to load the exchange rate data
def load_exchange_rates():
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vietcombank_exchange_rates.csv')
    try:
        # Load CSV and set 'Mã ngoại tệ' as index for easy lookup
        df = pd.read_csv(csv_path)
        # Convert the 'Bán' (selling) rate column to numeric values
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

    return render_template('index.html', currencies=currencies)

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

# API endpoint to refresh exchange rates by running main.py crawler
@app.route('/api/refresh', methods=['POST'])
def refresh_rates():
    try:
        # Run the crawler (main.py)
        result = subprocess.run(['python', 'main.py'],
                               capture_output=True,
                               text=True,
                               check=True)

        # Wait a short time to ensure file is written
        time.sleep(1)

        # Reload exchange rates
        df = load_exchange_rates()

        if df.empty:
            return jsonify({"success": False, "message": "Failed to load updated rates"}), 500

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

    except subprocess.CalledProcessError as e:
        return jsonify({
            "success": False,
            "message": f"Error running crawler: {e.stderr}"
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
