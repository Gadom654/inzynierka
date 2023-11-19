from stock_app import db, data_fetcher  # Import app, db, and data_fetcher from __init__.py
from flask import Blueprint, render_template, jsonify, request, redirect, url_for
import yfinance as yf
from datetime import datetime, timedelta

# Get the end date and time for data fetching
end_date = datetime.now()

# Calculate the date 5 years ago
start_date = end_date - timedelta(days=365 * 5)

# Create a Blueprint
routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/')
def index():
    try:
        # Fetch data from the DynamoDB table
        response = db.scan()
        stocks_data = response.get('Items', [])

        companies = []
        for stock in stocks_data:
            company = {
                "name": stock.get("name", "N/A"),
                "symbol": stock.get("symbol", "N/A"),
                "current_price": stock["data"][-1]["close_price"] if "data" in stock and stock["data"] else "N/A",
                "pe_ratio": stock.get("pe_ratio", "N/A"),
                "market_cap": stock.get("market_cap", "N/A")
            }
            companies.append(company)

        return render_template('index.html', companies=companies)
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

from flask import jsonify, render_template, request, redirect, url_for

@routes_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').upper()

    try:
        # Searching for the stock in the DynamoDB database
        response = db.query(
            IndexName='name-index',
            KeyConditionExpression=Key('name').eq(query)
        )
        stocks = response.get('Items', [])

        if stocks:
            # If stocks exist, redirect to the first stock's page
            symbol = stocks[0].get('symbol')
            return redirect(url_for('routes_bp.stock_detail', symbol=symbol))
        else:
            # If no stock is found, return to a search results page or a not found page
            return render_template('search_not_found.html', query=query)
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

#@routes_bp.route('/')
#def index():
#    try:
#        # Fetch data from the MongoDB collection
#        stocks_collection = db.stocks
#        stocks_data = stocks_collection.find()
#
#        # Create a list to store company information
#        companies = []
#
#        for stock in stocks_data:
#            company = {
#                "name": stock.get("name", "N/A"),
#                "symbol": stock.get("symbol", "N/A"),
#                "current_price": stock["data"][-1]["close_price"] if "data" in stock and stock["data"] else "N/A",
#                "pe_ratio": stock.get("pe_ratio", "N/A"),
#                "market_cap": stock.get("market_cap", "N/A")
#            }
#            companies.append(company)
#
#        return render_template('index.html', companies=companies)
#    except Exception as e:
#        return jsonify({"message": f"Error: {str(e)}"}), 500
#
#
#@routes_bp.route('/search', methods=['GET'])
#def search():
#    query = request.args.get('query', '').upper()
#
#    # Search for the stock in the MongoDB database
#    stock = db.stocks.find_one(
#        {"$or": [{"name": {"$regex": query, "$options": 'i'}}, {"symbol": {"$regex": query, "$options": 'i'}}]})
#
#    if stock:
#        # If stock exists, redirect to the stock's page
#        symbol = stock.get('symbol')
#        return redirect(url_for('routes.stock_detail', symbol=symbol))
#    else:
#        # If no stock is found, return to a search results page or a not found page
#        return render_template('search_not_found.html', query=query)
#

@routes_bp.route('/fetch_stock_data', methods=['GET', 'POST'])
def fetch_stock_data():
    if request.method == 'POST':
        # Get the symbol entered by the user
        symbol = request.form.get('symbol')

        # Fetch stock data for the entered symbol using DataFetcher
        stock_data = data_fetcher.fetch_stock_data(symbol, start_date, end_date)

        if stock_data is not None:
            # Fetch additional stock information
            stock_name, pe_ratio, market_cap = data_fetcher.fetch_additional_info(symbol)

            # Extract and store data in the database using DataFetcher
            data_fetcher.fetch_and_store_stock_data_in_db(db, symbol, start_date, end_date)

            return jsonify({"message": f"Stock data for {symbol} fetched and stored successfully!"}), 200
        else:
            return jsonify({"message": "Unable to fetch stock data."}), 404

    return render_template('fetch_stock_data.html')


@routes_bp.route('/chart/<symbol>')
def display_chart(symbol):
    try:
        # Fetch historical stock data for the selected symbol
        stock = yf.Ticker(symbol)
        stock_data = stock.history(period="1y", interval="1d")  # Adjust the time period as needed

        # Prepare data for the chart (e.g., using JavaScript charting libraries like Chart.js or Plotly)
        # Example: Create a JavaScript array from the stock data
        chart_data = []
        for date, row in stock_data.iterrows():
            chart_data.append({'date': date.strftime('%Y-%m-%d'), 'close_price': row['Close']})

        return render_template('chart.html', symbol=symbol, chart_data=chart_data)
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


@routes_bp.route('/stock/<symbol>')
def stock_detail(symbol):
    try:
        # Fetch data for the specific stock from the DynamoDB table
        response = db.get_item(Key={'symbol': symbol})
        stock_data = response.get('Item')

        if stock_data:
            # Check if 'data' is available in stock_data, if not, set it to an empty list
            chart_data = stock_data.get("data", [])
            return render_template('stock.html', stock=stock_data, chart_data=chart_data)
        else:
            return jsonify({"message": "Stock not found."}), 404
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

#@routes_bp.route('/stock/<symbol>')
#def stock_detail(symbol):
#    try:
#        # Fetch data for the specific stock from the MongoDB collection
#        stocks_collection = db.stocks
#        stock_data = stocks_collection.find_one({"symbol": symbol})
#
#        if stock_data:
#            # Check if chart_data is available in stock_data, if not, set it to an empty list
#            chart_data = stock_data.get("data", [])
#            return render_template('stock.html', stock=stock_data, chart_data=chart_data)
#        else:
#            return jsonify({"message": "Stock not found."}), 404
#    except Exception as e:
#        return jsonify({"message": f"Error: {str(e)}"}), 500


@routes_bp.route('/fetch_stock_data/<symbol>')
def fetch_and_store_stock_data(symbol):
    try:
        # Fetch historical stock data using DataFetcher
        stock_data = data_fetcher.fetch_stock_data(symbol, start_date, end_date)

        if stock_data is not None:
            # Fetch additional stock information
            stock_name, pe_ratio, market_cap = data_fetcher.fetch_additional_info(symbol)

            # Extract and store data in the database using DataFetcher
            data_fetcher.fetch_and_store_stock_data_in_db(db, symbol, start_date, end_date)

            return jsonify({"message": "Close prices fetched and stored successfully!"}), 200
        else:
            return jsonify({"message": "Unable to fetch stock data."}), 404
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

