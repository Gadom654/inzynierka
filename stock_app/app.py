from stock_app import app, db  # Import the app, db, and data_fetcher from __init__.py
from stock_app import routes
from data_updater.data_updater import DataUpdater

# Create an instance of DataUpdater and schedule data updates
data_updater = DataUpdater(db)
data_updater.schedule_data_update()

app.register_blueprint(routes.routes_bp)

if __name__ == "__main__":
    app.run()

