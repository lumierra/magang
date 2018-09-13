import MySQLdb as mdb
import os
import yaml
import mysql.connector

filename_config = os.path.abspath("Config/config.yml")
config = yaml.load(open(filename_config, "r"))

class Database():
    def __init__(self):
        self.host = config['database']['local']['host']
        self.user = config['database']['local']['user']
        self.password = config['database']['local']['password']
        self.database = config['database']['local']['database']
        self.port = config['database']['local']['port']
        self.config = config

    def test_connection(self):
        db = mdb.connect(self.host, self.user, self.password, self.database)
        cursor = db.cursor()
        cursor.execute("SELECT VERSION()")
        data = cursor.fetchone()

        if data:
            print("Koneksi Berhasil" + ' ' + data[0])
        else:
            print("Koneksi Gagal!!")

        db.close()

    def _single_execute(self, query):
        con = mdb.connect(self.host, self.user, self.password, self.database, self.port)
        cursor = con.cursor()
        cursor.execute(query)
        con.commit()
        con.close()

    def _many_execute(self, query, attr):
        con = mdb.connect(self.host, self.user, self.password, self.database, self.port)
        cursor = con.cursor()
        cursor.executemany(query, attr)
        con.commit()
        con.close()

    def update_data_content(self, title, content):
        connection = mdb.connect(self.host, self.user, self.password, self.database)
        cursor = connection.cursor()

        query = "UPDATE scraper_old SET content = '%s'  \
                WHERE title = '%s'" % \
                (content, title)

        try:
            cursor.execute(query)
            connection.commit()
        #             print("Update Data Successful")
        except:
            connection.rollback()
        #             print("Insert Data Failed")

        if connection:
            connection.close()

    def show_data(self):
        connection = mdb.connect(self.host, self.user, self.password, self.database)
        cursor = connection.cursor()

        query = "SELECT * from scraper"

        cursor.execute(query)
        result = cursor.fetchall()
        for items in result:
            print(items)

    def insert_content(self, category=None, title=None, description=None, url=None,
                       sub_category=None, publishedAt=None, img=None, content=None, clean_content=None, status_data=None):
        connection = mdb.connect(self.host, self.user, self.password, self.database)
        cursor = connection.cursor()

        query = "INSERT INTO scraper(category, title, description, url, sub_category, publishedAt, img, content, clean_content, status_data) \
                       VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
                (category, title, description, url, sub_category, publishedAt, img, content, clean_content, status_data)

        try:
            cursor.execute(query)
            connection.commit()
            print("Insert Data Successful")
        except:
            connection.rollback()
            print("Insert Data Failed")

        if connection:
            connection.close()


    def insert_data(self, category, sub_category, url, title, publishedAt, img, content, status_data):
        connection = mdb.connect(self.host, self.user, self.password, self.database)
        cursor = connection.cursor()

        query = "INSERT INTO scraper_old(category, sub_category, url, title, publishedAt, img, status_data) \
               VALUES (%s, %s, %s, %s, %s, %s, %s)" % \
                (category, sub_category, url, title, publishedAt, img, status_data)

        update_data_content(title, content)

        try:
            cursor.execute(query)
            connection.commit()
            print("Insert Data Successful")
        except:
            connection.rollback()
            print("Insert Data Failed")

        if connection:
            connection.close()

    def insert_many(self,table, attr):

        query = "INSERT INTO {}(category, title, description, url, sub_category, publishedAt, img, content, status_data, clean_content) \
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(table)

        try:
            self._many_execute(query, attr)
            print("Insert Data Successful")
        except:
            print("Insert Data Failed")






