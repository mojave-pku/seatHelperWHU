# -*- coding:utf-8 -*- 

# Developed by Hlz, 2017.04.28
# Mod by Hlz, 2017.05.06
# Version: 1.3
# Email: lzhwang@whu.edu.cn

import pymysql
from DBUtils.PooledDB import PooledDB
from . import sql_config as Config


class SQLManager(object):
    __pool = None

    def __enter__(self):
        self._conn = SQLManager.__getConn()
        self._cursor = self._conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_tb == None:
            self._cursor.close()
            self._conn.commit()
            self._conn.close()
        else:
            self._cursor.close()
            self._conn.rollback()
            self._conn.close()

    @staticmethod
    def __getConn():
        if SQLManager.__pool is None:
            __pool = PooledDB(creator=pymysql, mincached=1,
                              maxcached=20, host=Config.SQL_HOST,
                              port=Config.SQL_PORT, user=Config.DB_USER,
                              passwd=Config.DB_PASSWD, charset=Config.DB_CHARSET,
                              db=Config.DB_NAME
                              )
        return __pool.connection()

    def select(self, table, info=None, args=None, size=None, likeArgs={}, debug=False, orderBy=None):
        if info is None:
            sql = 'select * from ' + table
        # print sql
        else:
            sql = 'select '
            sql = sql + ','.join(info) + ' '
            sql = sql + 'from' + ' ' + table
        if args is None:
            sql = sql + ';'
            count = self._cursor.execute(sql)
        else:
            sql = sql + ' where '
            keys = args.keys()
            sql = sql + '=%s and '.join(keys) + '=%s'
            # print sql
            if len(likeArgs) != 0:
                likeKeys = likeArgs.keys()
                sql = sql + ' and ' + ' like %s and '.join(likeKeys) + ' like %s'

            if orderBy is not None:
                sql = sql + ' order by ' + orderBy
            sql = sql + ';'
            if debug:
                print(sql)
                print(args.values())
            count = self._cursor.execute(sql, list(args.values()) + list(likeArgs.values()))

        if count > 0:
            if size:
                return self._cursor.fetchmany(size)
            else:
                return self._cursor.fetchall()
        else:
            return False

    def delete(self, table, args):
        sql = 'delete from ' + table + ' where '
        keys = args.keys()
        sql = sql + '=%s and '.join(keys) + '=%s;'
        # print sql
        # print args.values()
        self._cursor.execute(sql, list(args.values()))
        affected = self._cursor.rowcount
        return affected

    def add(self, table, args, operation='replace'):
        # operation is either insert or replace
        sql = operation + ' into ' + table + ' ('
        sql = sql + ','.join(args.keys()) + ') values ('
        argFormat = []
        for i in range(0, len(args)):
            argFormat.append('%s')
        sql = sql + ','.join(argFormat) + ');'
        # if returnid is not False:
        # 	sql = sql + ''
        # 	self._cursor.execute(sql, args.values())
        # 	# print self._cursor.fetchall()
        # 	return self._cursor.fetchall()
        # print sql
        # print args.values()
        self._cursor.execute(sql, list(args.values()))
        affected = self._cursor.rowcount
        return affected

    def update(self, table, modArgs, selectArgs):
        sql = 'update ' + table + ' set '
        keys = modArgs.keys()
        sql = sql + '=%s ,'.join(keys) + '=%s where '

        keys = selectArgs.keys()
        sql = sql + '=%s and '.join(keys) + '=%s;'
        # print sql
        # # print args.values()
        # print modArgs.values()+selectArgs.values()
        self._cursor.execute(sql, list(modArgs.values()) + list(selectArgs.values()))
        affected = self._cursor.rowcount
        return affected

    def getId(self):
        sql = 'SELECT LAST_INSERT_ID();'
        self._cursor.execute(sql)
        return self._cursor.fetchall()


if __name__ == '__main__':
    info = ['iduser', 'username']
    args = {'creator': 'hlz'}
    likeArgs = {'content': '%A%B%'}
    selectArgs = {'iduser': '2334'}
    modArgs = {'username': 'test'}
    with SQLManager() as conn:
        print (conn.select(args=args, table='prob'))
