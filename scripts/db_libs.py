# -*- coding: utf-8 -*-
"""
@Date: 2020.12.12
@Author: wangzhongmin
@Desc: 数据库连接类
"""
import arrow
import pandas as pd
from sqlalchemy import create_engine

mysql_config = {
    'host': '{ip}',
    'port': 3306,
    'user': 'root',
    'password': '{pwd}',
    'database': '{dbName}',
}


class MysqlDB(object):
    """
    sqlalchemy 连接池参数说明：

    @:param: pool_size
    设置连接池中，保持的连接数。初始化时，并不产生连接。只有慢慢需要连接时，才会产生连接。
    例如我们的连接数设置成pool_size=10。如果我们的并发量一直最高是5。
    那么我们的连接池里的连接数也就是5。当我们有一次并发量达到了10。
    以后并发量虽然下去了，连接池中也会保持10个连接。

    @:param: max_overflow
    当连接池里的连接数已达到，pool_size时，且都被使用时。又要求从连接池里获取连接时，max_overflow就是允许再新建的连接数。
    例如pool_size=10，max_overlfow=5。当我们的并发量达到12时，当第11个并发到来后，就会去再建一个连接，第12个同样。
    当第11个连接处理完回收后，若没有在等待进程获取连接，这个连接将会被立即释放。

    @:param: pool_timeout
    从连接池里获取连接，如果此时无空闲的连接。且连接数已经到达了pool_size+max_overflow。
    此时获取连接的进程会等待pool_timeout秒。如果超过这个时间，还没有获得将会抛出异常。
    sqlalchemy默认30秒

    @:param: pool_recycle
    指一个数据库连接的生存时间。
    若 pool_recycle = 3600。也就是当这个连接产生1小时后，再获得这个连接时，会丢弃这个连接，重新创建一个新的连接。
    若 pool_recycle = -1，也就是连接池不会主动丢弃这个连接。永久可用。但是有可能数据库server设置了连接超时时间。
    例如mysql，设置的有wait_timeout默认为28800，8小时。当连接空闲8小时时会自动断开。8小时后再用这个连接也会被重置。
    """

    def __init__(self, db_config, mode='mysql+pymysql', pool_config=None):
        if not pool_config:
            pool_config = {
                'max_overflow': 5,  # 超过连接池大小外最多创建的连接数
                'pool_size': 10,  # 连接池大小，默认连接池中的连接数
                'pool_timeout': 60,  # 秒。池中没有线程最多等待的时间，否则报错
                'pool_recycle': -1,  # 秒。多久之后对线程池中的线程进行一次连接的回收（重置）
            }
        self.mysql_engine = self.__engine(db_config, mode, pool_config)

    def __engine(self, db_config, mode, pool_config):
        db_config['mode'] = mode
        sql_connection_str = '{mode}://{user}:{password}@{host}:{port}/{database}?charset=utf8'.format(**db_config)
        return create_engine(sql_connection_str, **pool_config, echo=False)

    def execute_sql(self, sql, n: int = 0):
        """ 执行SQL """
        if n == 1:
            return self.mysql_engine.execute(sql).fetchone()  # 或 self.mysql_engine.execute(sql).first()
        if n >= 2:
            return self.mysql_engine.execute(sql).fetchmany(n)
        return self.mysql_engine.execute(sql).fetchall()

    def trans_decorator(self, *args):
        """ 封装事务装饰器 """
        pass

    def query(self, sql, n: int = 0):
        """ 执行sql """
        with self.mysql_engine.connect() as connection:
            if n == 1:
                return connection.execute(sql).fetchone()
            if n >= 2:
                return connection.execute(sql).fetchmany(n)
            return self.mysql_engine.execute(sql).fetchall()
    
    def transaction(self, *args):
        """
        :param args: 多个sql语句，构成一个事务
        :return: 返回结果
        """
        with self.mysql_engine.connect() as connection:
            trans = connection.begin()
            try:
                for sql in args:
                    connection.execute(sql)
                # 所有sql统一提交
                trans.commit()
                return 'success'
            except Exception as err:
                # 事务回滚
                trans.rollback()
                return err

    def cols(self, sql):
        """ 返回sql结果集的字段名列表 """
        return self.mysql_engine.execute(sql).keys()


class DB(object):
    def __init__(self, host, user, password, driver, *args, **kwargs):
        self.host = host
        self.user = user
        self.password = password
        self.driver = driver

    def __GetSqlConnect(self):
        """
        @desc: 根据 driver 获取数据库连接，返回游标
            mysql_conn = pymysql.connect()
            sqlServer_conn = pymssql.connect()
        author: wangzhongmin
        date: 2020.12.04
        """
        driver_dic = {
            'mysql+mysqldb': 'pymysql',
            'mssql+pymssql': 'pymssql',
        }
        pySqlType = globals()[driver_dic.get(self.driver, 'pymysql')]  # 默认是pymysql
        self.connection = pySqlType.connect(host=self.host, user=self.user, password=self.password)
        cur = self.connection.cursor()
        if not cur:
            return (NameError, f"{driver_dic.get(self.driver)}连接数据库失败")
        return cur

    def execute_sql(self, sql):
        """
        desc: 执行sql语句，执行完关闭数据库连接；返回执行结果
        author: wangzhongmin
        date: 2020.12.04
        """
        cursor = self.__GetSqlConnect()
        try:
            cursor.execute(sql)
            res = cursor.fetchall()
            self.connection.close()
            return res
        except:
            raise ("Error:sql unable to fetch data")

    def show_databases(self):
        dbs = self.execute_sql('SHOW DATABASES')
        return [db[0] for db in dbs] if len(dbs) > 0 else []

    def show_tables(self, db_name=None):
        if db_name is None:
            return []
        cursor = self.__GetSqlConnect()
        cursor.execute(f"USE {db_name}")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        self.connection.close()
        return [table[0] for table in tables] if len(tables) > 0 else []

    def table_update_time(self, db_name, table_name):
        """
        desc: 查询数据表最近的更新时间
            :param db_name: 数据库名
            :param table_name: 数据表名
        author: wangzhongmin
        date: 2020.12.04
        """
        return self.execute_sql(f"""
        SELECT `TABLE_NAME`, IFNULL(`UPDATE_TIME`, `CREATE_TIME`) `UPDATE_TIME`
        FROM `information_schema`.`TABLES` 
        WHERE `information_schema`.`TABLES`.`TABLE_SCHEMA` = '{db_name}' 
        AND `information_schema`.`TABLES`.`TABLE_NAME` = '{table_name}';
        """)[0]

    def table_size(self, db_name, table_name):
        """
        desc: 查询数据表的数据量
            :param db_name: 数据库名
            :param table_name: 数据表名
        author: wangzhongmin
        date: 2020.12.04
        """
        return self.execute_sql(f"""
        SELECT `TABLE_NAME`, IFNULL(`TABLE_ROWS`, 0) `TABLE_ROWS`
        FROM `information_schema`.`TABLES` 
        WHERE `TABLE_SCHEMA` = '{db_name}' AND `TABLE_NAME`='{table_name}'
        """)[0]


if __name__ == '__main__':
    # obj = MysqlDB(mysql_config)
    # res = obj.execute_sql("select col_k1, col_k2 from table1")
    # cols = obj.cols("select col_k1, col_k2 from table1")
    # print('....res:', res)
    # print('....cols:', cols)

    db = DB(host='{ip}', user='root', password='{pwd}', driver='mysql+mysqldb')
    # print(db.show_databases())
    # print(db.show_tables('systemdb_manage_db'))
    print(db.table_update_time('systemdb_manage_db', 't_db_config'))
    print(db.table_size('systemdb_manage_db', 't_db_config'))

    print('-- over! --')

