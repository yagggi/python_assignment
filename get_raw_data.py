# coding: utf-8
import json
from datetime import datetime, timedelta
from decouple import config
import requests

from models import FinancialDataDAO


class WrongStatusCodeException(OSError):
    def __init__(self, response):
        msg = f'Got unexpected status_code: {response.status_code} with content: {response.content}'
        super().__init__(msg)


class ParseResponseException(OSError):
    def __init__(self, response):
        msg = f'Got unknown response: {response.content}'
        super().__init__(msg)


def fetch_stock_data(symbol):
    """Use alpha vantage API to get stock daily price data
    Doc: https://www.alphavantage.co/documentation/#dailyadj
    """
    url = 'https://www.alphavantage.co/query'
    params = dict(
        function='TIME_SERIES_DAILY_ADJUSTED',
        symbol=symbol,
        apikey=config('ALPHA_VANTAGE_API_KEY')
    )
    r = requests.get(url, params)
    if r.status_code != requests.codes.ok:
        raise WrongStatusCodeException(r)

    content = json.loads(r.content)
    return content


def parse_content(content, days_needed=14):
    """
    :param content:
    {
        "Meta Data": {
            "1. Information": "Daily Time Series with Splits and Dividend Events",
            "2. Symbol": "IBM",
            "3. Last Refreshed": "2023-03-17",
            "4. Output Size": "Compact",
            "5. Time Zone": "US/Eastern"
        },
        "Time Series (Daily)": {
            "2023-03-17": {
                "1. open": "124.08",
                "2. high": "124.52",
                "3. low": "122.93",
                "4. close": "123.69",
                "5. adjusted close": "123.69",
                "6. volume": "37400167",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0"
            },
            ...
        }
    }

    :param days_needed: int > 0
    :return:
    [
        {
            "symbol": "IBM",
            "date": "2023-02-14",
            "open_price": "153.08",
            "close_price": "154.52",
            "volume": "62199013",
        },
        ...
    ]
    """
    date_str_mapping_data = content['Time Series (Daily)']
    symbol = content['Meta Data']['2. Symbol']
    now = datetime.now().date()
    date_ = now
    result_list = []

    while date_ > now - timedelta(days=days_needed):
        date_str = date_.strftime('%Y-%m-%d')
        data = date_str_mapping_data.get(date_str)
        date_ -= timedelta(days=1)
        if not data:
            continue

        result_list.append(
            dict(
                symbol=symbol,
                date=date_str,
                open_price=data['1. open'],
                close_price=data['4. close'],
                volume=data['6. volume']
            )
        )
    return result_list


def save_stock_data_into_db(result_list):
    """Split results into smaller chunks to avoid connection overload
    """
    chunk_size = 300
    for idx in range(0, len(result_list), chunk_size):
        partial_result = result_list[idx: idx + chunk_size]
        FinancialDataDAO.batch_upsert(partial_result)


def fetch_stock_data_and_save_to_db():
    """Fetch data -> parse data -> save to db
    :return: None
    """
    symbols = ['IBM', 'AAPL']
    result_list = []
    for symbol in symbols:
        content = fetch_stock_data(symbol)
        result_list.extend(parse_content(content))
    save_stock_data_into_db(result_list)


if __name__ == '__main__':
    fetch_stock_data_and_save_to_db()
