# coding: utf-8
from sqlalchemy import Table, MetaData, create_engine, select, func, and_
from sqlalchemy.sql.expression import label
from decouple import config
from sqlalchemy.dialects.mysql import insert

engine = create_engine(config('MYSQL_URI'))
financial_data = Table("financial_data", MetaData(), autoload_with=engine)


class FinancialDataDAO:
    table = financial_data
    columns = [
        table.c.id,
        table.c.symbol,
        table.c.date,
        table.c.open_price,
        table.c.close_price,
        table.c.volume,
        table.c.created,
        table.c.updated,
    ]

    @classmethod
    def batch_upsert(cls, data_list):
        for each in data_list:
            each['open_price'] = float(each['open_price']) * 100
            each['close_price'] = float(each['close_price']) * 100

        t = cls.table
        insert_stmt = insert(t).values(data_list)
        on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(
            open_price=insert_stmt.inserted.open_price,
            close_price=insert_stmt.inserted.close_price,
            volume=insert_stmt.inserted.volume,
        )

        with engine.connect() as conn:
            res = conn.execute(on_duplicate_key_stmt)
            conn.commit()
        return res.rowcount

    @classmethod
    def get_stock_data_list(cls, symbol=None, start_date=None, end_date=None, page=0, limit=5):
        t = cls.table
        sql = select(
            t.c.id,
            t.c.symbol,
            t.c.date,
            label('close_price', t.c.close_price / 100),
            label('open_price', t.c.open_price / 100),
            t.c.volume,
            t.c.created,
            t.c.updated,
        ).order_by(t.c.date.asc())

        if symbol is not None:
            sql = sql.where(t.c.symbol == symbol)
        if start_date is not None:
            sql = sql.where(t.c.date >= start_date)
        if end_date is not None:
            sql = sql.where(t.c.date <= end_date)
        sql = sql.offset(page).limit(limit)

        with engine.connect() as conn:
            return conn.execute(sql).fetchall()

    @classmethod
    def get_statistics(cls, symbol, start_date, end_date):
        """Get average value of close_price/open_price/volume based on query args"""
        t = cls.table
        sql = select(
            t.c.symbol,
            label('average_daily_open_price', func.avg(t.c.open_price) / 100),
            label('average_daily_close_price', func.avg(t.c.close_price) / 100),
            label('average_daily_volume', func.avg(t.c.volume)),
        ).where(
            and_(
                t.c.symbol == symbol,
                t.c.date >= start_date,
                t.c.date <= end_date
            )
        )
        with engine.connect() as conn:
            return conn.execute(sql).fetchone()
