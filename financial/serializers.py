# coding: utf-8
from marshmallow import Schema, fields, ValidationError, post_load
from marshmallow.validate import Range, Validator
from datetime import datetime


class DateFormatValidator(Validator):
    """For date string format validation"""

    def __init__(self, format_str='%Y-%m-%d', strict=False):
        self.strict = strict
        self.format = format_str
        self.error = '{input} does not conform to format: {format}.'

    def _repr_args(self):
        return f"DateTime format: {self.format}"

    def _format_error(self, value, message=''):
        return (self.error or message).format(input=value, format=self.format)

    def __call__(self, value):
        if not self.strict and value == '':
            return None
        try:
            datetime.strptime(value, '%Y-%m-%d')
        except Exception:
            raise ValidationError(self._format_error(value))
        return value


class DateRangeValidationMixin:
    """Validate start_date is less or equal to end_date"""
    @post_load
    def validate_date_range(self, data, **kwargs):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise ValidationError(
                f'start_date ({start_date}) is not allowed to be greater than end_date ({end_date})'
            )
        return data


class FinancialDataQueryDeserializer(Schema, DateRangeValidationMixin):
    """For financial_data query params validation & deserialization"""
    limit = fields.Int(load_default=5, validate=Range(min=1))
    page = fields.Int(load_default=0, validate=Range(min=0))
    start_date = fields.Str(validate=DateFormatValidator())
    end_date = fields.Str(validate=DateFormatValidator())
    symbol = fields.Str()


class SingleFinancialDataSerializer(Schema):
    """For single financial_data serialization"""
    symbol = fields.Str(required=True)
    date = fields.Date(required=True)
    open_price = fields.Str(required=True)
    close_price = fields.Str(required=True)
    volume = fields.Str(required=True)


class PaginationSerializer(Schema):
    """For pagination data serialization"""
    count = fields.Int(required=True, validate=Range(min=0))
    page = fields.Int(required=True, validate=Range(min=0))
    limit = fields.Int(required=True, validate=Range(min=0))
    pages = fields.Int(required=True, validate=Range(min=0))


class ErrorInfoSerializer(Schema):
    """For error data serialization"""
    error = fields.Str(allow_none=False)


class FinancialDataListSerializer(Schema):
    """For financial_data response serialization"""
    data = fields.Nested(SingleFinancialDataSerializer, many=True, required=True)
    pagination = fields.Nested(PaginationSerializer, required=True)
    info = fields.Nested(ErrorInfoSerializer, required=True)


class FinancialStatisticsQueryDeserializer(Schema, DateRangeValidationMixin):
    """For statistics query params validation & deserialization"""
    start_date = fields.Str(required=True, validate=DateFormatValidator(strict=True))
    end_date = fields.Str(required=True, validate=DateFormatValidator(strict=True))
    symbol = fields.Str(required=True)


class FinancialStatisticsDataSerializer(FinancialStatisticsQueryDeserializer):
    """For statistics data serialization"""
    average_daily_open_price = fields.Float(required=True, allow_none=False)
    average_daily_close_price = fields.Float(required=True, allow_none=False)
    average_daily_volume = fields.Int(required=True, allow_none=False)


class FinancialStatisticsResponseSerializer(Schema):
    """For /api/statistics response serialization"""
    data = fields.Nested(FinancialStatisticsDataSerializer)
    info = fields.Nested(ErrorInfoSerializer, required=True)
