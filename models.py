# coding: utf-8
from sqlalchemy import Table, MetaData, create_engine
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
    def get_stock_data_by_symbol(cls, symbol):
        t = cls.table
        sql = t.select().where(
            t.c.symbol == symbol
        )
        with engine.connect() as conn:
            return conn.execute(sql).fetchall()
