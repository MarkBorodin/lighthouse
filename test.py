import json
import os
import time
import uuid

import psycopg2


class GetData(object):
    file = 'report.json'

    def __init__(self, url):
        """get url and create commands"""
        self.url = url
        self.command_desktop = f'lighthouse {self.url} --only-categories=performance,accessibility,best-practices,seo --preset=desktop --chrome-flags="--headless" --output=json --output-path=./{self.file}'
        self.command_mobile = f'lighthouse {self.url} --only-categories=performance,accessibility,best-practices,seo --form-factor=mobile --chrome-flags="--headless" --output=json --output-path=./{self.file}'

    def get_data(self, command):
        """get data and write to db"""
        os.system(command)
        time.sleep(20)

        with open(f'{self.file}', 'r') as f:
            js = f.read()
            result = json.loads(js)

        data = {
            'performance': int(result['categories']['performance']['score'] * 100),
            'accessibility': int(result['categories']['accessibility']['score'] * 100),
            'best_practices': int(result['categories']['best-practices']['score'] * 100),
            'seo': int(result['categories']['seo']['score'] * 100)
        }

        print(data.items())

        self.open_db()

        # write to db Home_Page
        home_page_id = str(uuid.uuid1())
        self.cur.execute(
            """INSERT INTO Home_Page (id, url, sitemap_exists)
               VALUES (%s, %s, %s)""", (
                home_page_id,
                str(self.url),
                't',
            )
        )

        # write data to db
        self.cur.execute(
            """INSERT INTO lighthousebasic (performance, accessibility, best_practices, seo, home_page)
               VALUES (%s, %s, %s, %s, %s)""", (
                data['performance'],
                data['accessibility'],
                data['best_practices'],
                data['seo'],
                home_page_id,
            )
        )

        self.connection.commit()
        self.close_db()

        return data

    def open_db(self):
        """open db"""
        hostname = '127.0.0.1'
        username = 'parsing_admin'
        password = 'parsing_adminparsing_admin'
        database = 'parsing'
        port = "5444"
        self.connection = psycopg2.connect( # noqa
            host=hostname,
            user=username,
            password=password,
            dbname=database,
            port=port)
        self.cur = self.connection.cursor() # noqa

    def close_db(self):
        """close db"""
        self.cur.close()
        self.connection.close()


if __name__ == '__main__':
    # url for check
    url = 'https://www.sos-kinderdorf.ch/'

    # create object
    data = GetData(url)

    # get data for desktop
    data.get_data(data.command_desktop)

    # get data fo mobile
    data.get_data(data.command_mobile)
