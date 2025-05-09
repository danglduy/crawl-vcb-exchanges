# Vietcombank Exchange Rate Calculator

This web application provides a dynamic currency exchange calculator using the latest exchange rates from Vietcombank. The system crawls exchange rates from the Vietcombank website and allows users to perform currency conversions with adjustable percentages.

## Features

- Automated exchange rate crawling from Vietcombank's website
- Real-time currency conversion calculator
- Dynamic table with the ability to add/remove rows
- Adjustable extra percentage for each conversion
- One-click refresh of exchange rates without losing table data
- Responsive design that works on desktop and mobile devices
- Grand total calculation across all rows

## Tech Stack

- **Backend**: Python with Flask
- **Frontend**: HTML, CSS, JavaScript
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome
- **Web Scraping**: Selenium

## Installation

### Prerequisites

- Python 3.7+
- Chrome web browser (for Selenium)
- ChromeDriver (compatible with your Chrome version)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/vietcombank-exchange-calculator.git
   cd vietcombank-exchange-calculator
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required packages using uv (packages are already locked in the project):
   ```bash
   uv pip install .
   ```

4. Make sure ChromeDriver is installed and in your PATH or in the project directory.

## Usage

1. Start the Flask application (it will automatically get the latest rates if no CSV exists):
   ```bash
   python app.py
   ```

2. Open your web browser and go to `http://127.0.0.1:5000/`

3. Use the calculator:
  - Select a currency from the dropdown
  - Enter the value you want to convert
  - Adjust the extra percentage if needed
  - See the calculated total
  - Add more rows as needed
  - Click "Refresh Rates" to get the latest exchange rates

## Project Structure

```
vietcombank-exchange-calculator/
├── app.py                           # Flask application
├── services/
│   ├── __init__.py                  # Makes services a Python package
│   └── crawl.py                     # Crawler service for exchange rates
├── data/
│   └── .keep                        # Ensures data directory exists in git
│   └── vietcombank_exchange_rates.csv  # Crawled exchange rate data (generated, git-ignored)
├── templates/
│   └── index.jinja2                 # Main application interface
├── .gitignore                       # Git ignore configuration
└── README.md                        # Project documentation
```

## How It Works

1. **Automatic Crawling for Exchange Rates**:
  - The `services/crawl.py` module uses Selenium to crawl the Vietcombank website
  - It extracts currency rates from the exchange rate table
  - The data is saved to a CSV file for the application to use
  - If no CSV file exists when the app starts, the crawler is automatically executed

2. **Web Application**:
  - The Flask app loads the exchange rate data from the CSV
  - The frontend displays a dynamic table for currency conversion
  - Users can add/remove rows, select currencies, and enter values
  - The application calculates totals with extra percentages

3. **Rate Refreshing**:
  - The "Refresh Rates" button triggers the crawler to get new rates
  - The application updates the rates without disrupting the table

## Dependencies

This project uses the following main dependencies:
- Flask
- Pandas
- Selenium
- webdriver-manager

All dependencies are managed using `uv` and are already locked in the project.

## License

[MIT License](LICENSE)

## Acknowledgments

- Vietcombank for providing the exchange rate data
- The open-source community for the tools and libraries used in this project

---

*Note: This application is for educational and personal use only. Exchange rates are crawled from Vietcombank's public website. Always verify important currency conversions with official sources.*
