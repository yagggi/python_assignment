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
    date_str_mapping_data = content['Time Series (Daily)']
    symbol = content['Meta Data']['2. Symbol']
    now = datetime.now().date()
    date_ = now
    result_list = []

    while date_ >= now - timedelta(days=days_needed):
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
    return FinancialDataDAO.batch_upsert(result_list)


def fetch_stock_data_and_save_to_db():
    symbols = ['IBM', 'AAPL']
    result_list = []
    for symbol in symbols:
        content = fetch_stock_data(symbol)
        result_list.extend(parse_content(content))
    save_stock_data_into_db(result_list)


if __name__ == '__main__':
    fetch_stock_data_and_save_to_db()
