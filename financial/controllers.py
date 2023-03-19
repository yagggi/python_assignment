# coding: utf-8
from financial.serializers import FinancialDataQueryDeserializer, FinancialDataListSerializer, FinancialStatisticsQueryDeserializer, \
    FinancialStatisticsResponseSerializer
from models import FinancialDataDAO
from math import ceil

DEFAULT_LIMIT_PER_PAGE = 5


def _parse_url_params(url_params, schema):
    """Validate and serialize url params using specific schema"""
    error = ''
    try:
        query = schema.load(url_params)
    except Exception as e:
        error = str(e)
        query = {}
    return error, query


def _generate_pagination_info(total_cnt, current_page, limit_per_page=DEFAULT_LIMIT_PER_PAGE):
    """
    :param total_cnt: int
    :param current_page: int
    :param limit_per_page: int
    :return: {
        page: int,
        limit: int,
        pages: int,
        count: int
    }
    """
    pagination = dict(
        page=current_page,
        limit=limit_per_page,
        pages=ceil(total_cnt / limit_per_page) if limit_per_page != 0 else total_cnt,
        count=total_cnt,
    )
    return pagination


def get_financial_data(url_params):
    """Generate financial data response data (in dict representation) according to url params"""
    error, query = _parse_url_params(url_params, FinancialDataQueryDeserializer())
    if error:
        data = []
    else:
        data = FinancialDataDAO.get_stock_data_list(**query)

    pagination = _generate_pagination_info(
        total_cnt=len(data),
        current_page=query.get('page', 0),
        limit_per_page=query.get('limit', DEFAULT_LIMIT_PER_PAGE)
    )
    result = dict(
        data=data,
        pagination=pagination,
        info=dict(error=error)
    )
    response_schema = FinancialDataListSerializer()
    return response_schema.dump(result)


def get_financial_statistics(url_params):
    """Generate statistics response data (in dict representation) according to url params"""
    error, query = _parse_url_params(url_params, FinancialStatisticsQueryDeserializer())

    if error:
        data = {}
    else:
        data = dict(start_date=query['start_date'], end_date=query['end_date'])
        statistics = FinancialDataDAO.get_statistics(**query)
        data.update(statistics._mapping)

    result = dict(
        data=data,
        info=dict(error=error)
    )
    response_schema = FinancialStatisticsResponseSerializer()
    return response_schema.dump(result)
