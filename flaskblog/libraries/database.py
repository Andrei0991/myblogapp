#!/usr/bin/python3
import pymysql as MySQLdb
from flaskblog.config import config

class Database:
    def __init__(self):
        try:
            self.connection = MySQLdb.connect(
                host=config.db_host["host"],
                port=config.db_host["port"],
                user=config.db_host["username"],
                passwd=config.db_host["password"],
                database=config.db_host["dbname"],
                charset='utf8',
                use_unicode=True
            )
            self.connection.ping(True)
            self.connection.autocommit(True)
            self.cursor = self.connection.cursor()

        except Exception as e:
            raise Exception( 'ERROR DATABASE:: Mysql is not connected!' )

    def query( self, query, show=False ):
        try:
            if show:
                return query
            else:
                self.connection.ping(True)
                self.cursor.execute(query)
                count = self.cursor.rowcount
                return count
        except Exception as e:
            if config.environment == 'development':
                print( "MYSQL_EXCEPTION:\n{0}\nQuery:\n{1}".format( e, query.strip() ) )
            self.connection.rollback()

    def select( self, query, selectOnce = True, show = False ):
        try:
            if show :
                return query
            else:
                self.connection.ping(True)
                cursor = self.connection.cursor( MySQLdb.cursors.DictCursor )
                cursor.execute( query )

                if selectOnce:
                    return cursor.fetchone()
                else:
                    return cursor.fetchall()
        except Exception as e:
            if config.environment == 'development':
                print( "MYSQL_EXCEPTION:\n{0}\nQuery:\n{1}".format( e, query.strip() ) )
            self.connection.rollback()

    def insert( self, query, show=False ):
        try:
            if show:
                return query
            else:
                self.connection.ping(True)
                self.cursor.execute(query)
                insert_id = self.cursor.lastrowid
                return insert_id
        except Exception as e:
            if config.environment == 'development':
                print( "MYSQL_EXCEPTION:\n{0}\nQuery:\n{1}".format( e, query.strip() ) )
            self.connection.rollback()

    def update(self, query, show=False):
        try:
            if show:
                return query
            else:
                self.connection.ping(True)
                self.cursor.execute(query)
                count = self.cursor.rowcount
                return count
        except Exception as e:
            if config.environment == 'development':
                print( "MYSQL_EXCEPTION:\n{0}\nQuery:\n{1}".format( e, query.strip() ) )
            self.connection.rollback()

    def delete(self, query, show = False):
        try:
            if show:
                return query
            else:
                self.connection.ping(True)
                self.cursor.execute(query)
                count = self.cursor.rowcount
                return count
        except Exception as e:
            if config.environment == 'development':
                print( "MYSQL_EXCEPTION:\n{0}\nQuery:\n{1}".format( e, query.strip() ) )
            self.connection.rollback()

    def transaction( self, query, show = False ):
        try:
            if show:
                return query
            else:
                count = True
                self.connection.ping(True)
                self.connection.autocommit( False )
                query = query.split( ';' )
                for i in query:
                    self.cursor.execute( i )
                    count = self.cursor.rowcount

                if count:
                    self.connection.commit()
                else:
                    self.connection.rollback()

                return count
        except Exception as e:
            if config.environment == 'development':
                print( "MYSQL_EXCEPTION:\n{0}\nQuery:\n{1}".format( e, query.strip() ) )
            self.connection.close()

    def escape_string( self, data ):
        return MySQLdb.escape_string( data )

    def __del__(self):
        self.connection.close()

