# coding: utf-8
from flask import Flask, request
from financial.controllers import get_financial_data, get_financial_statistics

app = Flask('financial')
DEFAULT_LIMIT_PER_PAGE = 5


@app.get("/api/financial_data")
def financial_data_list_handler():
    return get_financial_data(request.args)


@app.get("/api/statistics")
def financial_data_statistics_handler():
    return get_financial_statistics(request.args)
