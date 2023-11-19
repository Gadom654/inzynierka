import yfinance as yf
import requests
from bs4 import BeautifulSoup
import json
from decimal import Decimal, InvalidOperation

class DataFetcher:
    def __init__(self):
        pass

    @staticmethod
    def fetch_stock_data(symbol, start_date, end_date):
        try:
            stock = yf.Ticker(symbol)
            stock_data = stock.history(start=start_date, end=end_date, interval="1d")
            return stock_data
        except Exception as e:
            print(f"Error fetching stock data for {symbol}: {str(e)}")
            return None

    @staticmethod
    def fetch_additional_info(symbol):
        try:
            api_key="19859RY0D58DN3BY"
            # Define the API endpoint
            url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}"

            # Make the API request
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()

                # Extract the desired information
                stock_name = data.get("Name")
                pe_ratio = Decimal(str(data.get("PERatio"))) if data.get("PERatio") is not None else None
                market_cap = data.get("MarketCapitalization")

                if market_cap is not None and market_cap != 'None':
                    # Ensure that market_cap is a string representing a number
                    market_cap = Decimal(market_cap) / Decimal(1e6)
                    market_cap = market_cap.quantize(Decimal('0.01'))

                return stock_name, pe_ratio, market_cap
            else:
                print(f"Failed to fetch data for {symbol}, status code: {response.status_code}")
                return None, None, None
        except Exception as e:
            print(f"Error fetching additional info for {symbol}: {str(e)}")
            return None, None, None

    @staticmethod
    def fetch_last_closing_price(symbol):
        try:
            stock = yf.Ticker(symbol)
            stock_data = stock.history(period="1d", interval="1d")
            if not stock_data.empty:
                last_close_price = stock_data["Close"].iloc[-1]
                return Decimal(last_close_price).quantize(Decimal('0.01'))
            else:
                return None
        except Exception as e:
            print(f"Error fetching last closing price for {symbol}: {str(e)}")
            return None

    @staticmethod
    def fetch_data_for_all_symbols(symbols, start_date, end_date):
        stock_data_dict = {}
        for symbol in symbols:
            stock_data = DataFetcher.fetch_stock_data(symbol, start_date, end_date)
            if stock_data is not None:
                stock_data_dict[symbol] = stock_data
        return stock_data_dict

    @staticmethod
    def fetch_and_store_stock_data_in_db(db, symbol, start_date, end_date):
        try:
            stock_data = DataFetcher.fetch_stock_data(symbol, start_date, end_date)
            if stock_data is not None:
                stock_name, pe_ratio, market_cap = DataFetcher.fetch_additional_info(symbol)

                #close_prices = [{"date": str(date), "close_price": Decimal(str(round(close, 1)))} 
                #                for date, close in zip(stock_data.index, stock_data["Close"])]
                #last_close_price = Decimal(str(round(stock_data["Close"].iloc[-1], 2)))

                # Convert close prices to Decimal and check
                close_prices = []
                for date, close in zip(stock_data.index, stock_data["Close"]):
                    try:
                        decimal_close = Decimal(str(round(close, 2)))
                        close_prices.append({"date": str(date), "close_price": decimal_close})
                    except InvalidOperation:
                        print(f"Error converting close price to Decimal for date {date}")
                        continue

                # Convert last close price to Decimal and check
                try:
                    last_close_price = Decimal(str(round(stock_data["Close"].iloc[-1], 2)))
                except InvalidOperation:
                    print("Error converting last close price to Decimal")
                    last_close_price = None

                # Convert pe_ratio to Decimal and check
                try:
                    decimal_pe_ratio = Decimal(str(pe_ratio))
                except InvalidOperation:
                    print(f"Error converting PE ratio to Decimal. Value: {pe_ratio}")
                    decimal_pe_ratio = None
                
                # Convert market_cap to Decimal and check
                try:
                    decimal_market_cap = Decimal(str(market_cap))
                except InvalidOperation:
                    print(f"Error converting market cap to Decimal. Value: {market_cap}")
                    decimal_market_cap = None
                response = db.get_item(Key={'symbol': symbol})
                existing_stock = response.get('Item')

                if existing_stock:
                    # Update existing stock
                    db.update_item(
                        Key={'symbol': symbol},
                        UpdateExpression="SET #data = list_append(if_not_exists(#data, :empty_list), :new_data), "
                                         "#name = :name, #pe_ratio = :pe_ratio, "
                                         "#market_cap = :market_cap, #last_close_price = :last_close",
                        ExpressionAttributeNames={
                            "#data": "data",
                            "#name": "name",
                            "#pe_ratio": "pe_ratio",
                            "#market_cap": "market_cap",
                            "#last_close_price": "last_close_price"
                        },
                        ExpressionAttributeValues={
                            ":new_data": close_prices,
                            ":name": stock_name,
                            ":pe_ratio": pe_ratio,
                            ":market_cap": market_cap,
                            ":last_close": last_close_price,
                            ":empty_list": []
                        }
                    )
                else:
                    # Insert new stock
                    db.put_item(
                        Item={
                            "symbol": symbol,
                            "data": close_prices,
                            "name": stock_name,
                            "pe_ratio": pe_ratio,
                            "market_cap": market_cap,
                            "last_close_price": last_close_price
                        }
                    )
        except Exception as e:
            print(f"Error fetching and storing data for {symbol}: {str(e)}")


    # Example usage:
    # data_fetcher = DataFetcher()
    # stock_data = data_fetcher.fetch_stock_data("AAPL", "2020-01-01", "2020-12-31")
    # stock_name, pe_ratio, market_cap = data_fetcher.fetch_additional_info("AAPL")
    # last_close_price = data_fetcher.fetch_last_closing_price("AAPL")
    # stock_data_dict = data_fetcher.fetch_data_for_all_symbols(["AAPL", "MSFT"], "2020-01-01", "2020-12-31")
    # annual_earnings, quarterly_earnings = data_fetcher.fetch_earnings_data("AAPL")
    # data_fetcher.fetch_and_store_stock_data_in_db(db, "AAPL", "2020-01-01", "2020-12-31")
