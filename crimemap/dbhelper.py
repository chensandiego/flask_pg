import pymysql
import dbconfig



class DBHelper:
    def connect(self,database="crimemap"):
        return pymysql.connect(host='localhost',
            user=dbconfig.db_user,
            password=dbconfig.db_password,
            db=database)

    def get_all_input(self):
        connection=seslf.connect()
        try:
            query="select description from crimes;"
            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()
        finally:
            connection.close()

    def add_input(self,data):
        connection=self.connect()
        try:
            #this should be done through input filter and avoid
            # sql injection
            #query="insert into crimes (description) values ('{}');".format(data)
            #prevent sql injection
            query="insert into crimes (description) values (%s);"
            with connection.cursor() as cursor:
                cursor.execute(query,data)
                connection.commit()
        finally:
            connection.close()

    def clear_all(self):
        connection= self.connect()
        try:
            query="DELETE from crimes;"
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
        finally:
            connection.close()
