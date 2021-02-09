import psycopg2


class DB(object):
    def open(self):
        hostname = '127.0.0.1'
        username = 'parsing_admin'
        password = 'parsing_adminparsing_admin'
        database = 'parsing'
        port = "5444"
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database, port=port)
        self.cur = self.connection.cursor()

    def close(self):
        self.cur.close()
        self.connection.close()

    def drop_table(self):
        self.cur.execute(
            """DROP TABLE table_1"""
        )
        self.connection.commit()

    def create_tables(self):
        """create tables in the database if they are not contained"""

        self.cur.execute('''CREATE TABLE IF NOT EXISTS Home_Page
                     (
                     id TEXT PRIMARY KEY,
                     url TEXT,
                     sitemap_exists boolean
                     );''')

        self.cur.execute('''CREATE TABLE IF NOT EXISTS lighthousebasic
                             (
                     id SERIAL PRIMARY KEY,
                     performance INT,
                     accessibility INT,
                     best_practices INT,
                     seo INT,
                     home_page TEXT,
                     FOREIGN KEY (home_page) REFERENCES Home_Page (id) ON DELETE CASCADE
                     );''')

        self.cur.execute('''CREATE TABLE IF NOT EXISTS lighthousemodile
                                    (
                     id SERIAL PRIMARY KEY,
                     performance INT,
                     accessibility INT,
                     best_practices INT,
                     seo INT,
                     home_page TEXT,
                     FOREIGN KEY (home_page) REFERENCES Home_Page (id) ON DELETE CASCADE
                     );''')

        self.cur.execute('''CREATE TABLE IF NOT EXISTS pagespeedinsights
                                            (
                     id SERIAL PRIMARY KEY,
                     desktop_speed INT,
                     mobile_speed INT,
                     home_page TEXT,
                     FOREIGN KEY (home_page) REFERENCES Home_Page (id) ON DELETE CASCADE
                     );''')

        self.connection.commit()


db = DB()
db.open()
db.create_tables()
db.close()
