import requests
import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for the React frontend

@app.route("/api/get_test_data", methods=["GET"])
def get_test_data():
    # Fetch data from the API
    data = requests.get("https://api.meridian.trade/api/trades/test_data").json()

    # Create DataFrame
    df = pd.DataFrame(data)

    # Convert 'time' column to datetime
    df['time'] = pd.to_datetime(df['time'], errors='coerce')  # Ensure invalid dates are handled as NaT

    # Sort by trade time
    df = df.sort_values(by='time')

    # Aggregate by 'orderno'
    aggregated_df = df.groupby('orderno').agg({
        'quantity': 'sum',
        'price': 'mean',
        'buysell': 'first',
        'comission': 'sum',
        'time': 'first'
    }).reset_index()

    # List to store strategies
    strategies = []

    # Loop over orders to determine strategies
    for idx, row in aggregated_df.iterrows():
        orderno = row['orderno']
        time_first = row['time']
        total_quantity = abs(row['quantity'])
        avg_price = row['price']
        buysell = row['buysell']
        total_commission = row['comission']
        total_value = row['price'] * abs(row['quantity'])

        # Check strategy by comparing the next order
        if idx + 1 < len(aggregated_df):
            next_row = aggregated_df.iloc[idx + 1]
            if total_quantity == abs(next_row['quantity']) and row['buysell'] != next_row['buysell']:
                strategy_type = 'long' if buysell == 'B' else 'short'
                open_time = time_first
                close_time = next_row['time']
                open_value = total_value
                close_value = next_row['price'] * abs(next_row['quantity'])
                open_commission = total_commission
                close_commission = next_row['comission']

                # Calculate profit/loss based on strategy type
                if strategy_type == 'long':
                    profit_loss = (close_value - open_value) - (open_commission + close_commission)
                else:
                    profit_loss = (open_value - close_value) - (open_commission + close_commission)

                profit_loss = round(profit_loss, 2)  # Round profit/loss

                # Add trade information
                strategies.append({
                    "id": len(strategies) + 1,
                    "strategy": strategy_type,
                    "open_time": open_time,
                    "close_time": close_time,
                    "open_price": round(avg_price, 2),
                    "close_price": round(next_row['price'], 2),
                    "profit_loss": profit_loss
                })

    # Initialize variables for metrics
    total_profit = 0
    total_loss = 0
    start_capital = 100000  # Starting capital

    # Loop over strategies to calculate profit/loss and metrics
    for strategy in strategies:
        if strategy['profit_loss'] > 0:
            total_profit += strategy['profit_loss']
        else:
            total_loss += abs(strategy['profit_loss'])

    # Calculate metrics
    profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
    return_value = total_profit - total_loss
    return_percent = (return_value / start_capital) * 100 if start_capital > 0 else 0

    # Round metrics before sending them
    metrics = {
        "profit_factor": round(profit_factor, 2),
        "return": round(return_value, 2),
        "return_percent": round(return_percent, 2)
    }

    # Send back the aggregated data with strategies and metrics
    aggregated_data = {
        "closed_trades": strategies,
        "metrics": metrics
    }

    return jsonify([aggregated_data])

if __name__ == "__main__":
    app.run(debug=True)
