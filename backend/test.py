import requests
import pandas as pd

# Получаем данные с API
data = requests.get("https://api.meridian.trade/api/trades/test_data").json()

# Создаем DataFrame
df = pd.DataFrame(data)

# Преобразуем столбец 'time' в datetime для сортировки
df['time'] = pd.to_datetime(df['time'])

# Сортируем по дате выполнения сделки
df = df.sort_values(by='time')

# Выполняем агрегацию по orderno
aggregated_df = df.groupby('orderno').agg({
    'quantity': 'sum',  # Суммируем количество
    'price': 'mean',  # Средняя цена для всех частично исполненных сделок
    'buysell': 'first',  # Первый тип операции (Buy/Sell)
    'comission': 'sum',  # Общая комиссия
    'time': 'first'  # Время первой сделки по ордеру
}).reset_index()

# Инициализация списка для результатов сделок
strategies = []

# Проходим по ордерам и определяем стратегии
for idx, row in aggregated_df.iterrows():
    orderno = row['orderno']
    time_first = row['time']
    total_quantity = abs(row['quantity'])  # Без округления
    avg_price = row['price']  # Без округления
    buysell = row['buysell']
    total_commission = row['comission']  # Без округления
    total_value = row['price'] * abs(row['quantity'])  # Без округления

    # Проверяем стратегию
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

            # Расчет прибыли/убытка с округлением только в самом конце
            if strategy_type == 'long':
                profit_loss = (close_value - open_value) - (open_commission + close_commission)
            else:
                profit_loss = (open_value - close_value) - (open_commission + close_commission)

            profit_loss = round(profit_loss, 2)  # Округление прибыли/убытка

            # Добавляем информацию о сделке
            strategies.append({
                "id": len(strategies) + 1,
                "strategy": strategy_type,
                "open_time": open_time,
                "close_time": close_time,
                "open_price": round(avg_price, 2),  # Округляем для вывода
                "close_price": round(next_row['price'], 2),  # Округляем для вывода
                "profit_loss": profit_loss
            })

# Инициализируем переменные для метрик
total_profit = 0
total_loss = 0
start_capital = 100000  # Стартовый капитал

# Вывод информации о стратегиях и расчеты метрик
for strategy in strategies:
    print(f"Была совершена сделка, присвоен ID = {strategy['id']}")
    print(f"Стратегия = {strategy['strategy']}")
    print(f"Дата открытия сделки = {strategy['open_time']}")
    print(f"Дата закрытия сделки = {strategy['close_time']}")
    print(f"Цена открытия = {strategy['open_price']:.2f}")
    print(f"Цена закрытия = {strategy['close_price']:.2f}")
    print(f"Прибыль/убыток = {strategy['profit_loss']:.2f}")
    print("-" * 60)

    # Обновляем суммы прибыли и убытка
    if strategy['profit_loss'] > 0:
        total_profit += strategy['profit_loss']
    else:
        total_loss += abs(strategy['profit_loss'])

# Рассчитываем метрики
profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
return_value = total_profit - total_loss
return_percent = (return_value / start_capital) * 100 if start_capital > 0 else 0

# Округляем метрики перед выводом
metrics = {
    "profit_factor": round(profit_factor, 2),
    "return": round(return_value, 2),
    "return_percent": round(return_percent, 2)
}

# Выводим метрики
print(f"\nМетрики:\n{'-' * 60}")
print(f"Profit Factor: {metrics['profit_factor']:.2f}")
print(f"Return: {metrics['return']:.2f}")
print(f"Return %: {metrics['return_percent']:.2f}%")

