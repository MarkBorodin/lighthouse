import json
import os
import sys
import time
import uuid

import psycopg2
import requests


class GetData(object):
    file = 'report.json'

    def __init__(self, url):
        """get url and create commands"""
        self.url = url

    def write_home_page(self):
        # write to db Home_Page
        self.home_page_id = str(uuid.uuid1())

        self.open_db()

        self.cur.execute(
            """INSERT INTO Home_Page (id, url, sitemap_exists)
               VALUES (%s, %s, %s)""", (
                self.home_page_id,
                str(self.url),
                't',
            )
        )

        self.connection.commit()
        self.close_db()

    def get_data_for_mibile(self):
        """get data for mibile and write to db"""
        self.command_mobile = f'lighthouse {self.url} --only-categories=performance,accessibility,best-practices,seo -form-factor=mobile --screenEmulation.mobile --chrome-flags="--headless" --output=json --output-path=./{self.file}'

        os.system(self.command_mobile)
        time.sleep(30)

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

        # write data to db
        self.cur.execute(
            """INSERT INTO lighthousemodile (performance, accessibility, best_practices, seo, home_page)
               VALUES (%s, %s, %s, %s, %s)""", (
                data['performance'],
                data['accessibility'],
                data['best_practices'],
                data['seo'],
                self.home_page_id,
            )
        )

        self.connection.commit()
        self.close_db()

    def get_data_for_desctop(self):
        """get data for mibile and write to db"""
        self.command_desktop = f'lighthouse {self.url} --only-categories=performance,accessibility,best-practices,seo --preset=desktop --chrome-flags="--headless" --output=json --output-path=./{self.file}'

        os.system(self.command_desktop)
        time.sleep(30)

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

        # write data to db
        self.cur.execute(
            """INSERT INTO lighthousebasic (performance, accessibility, best_practices, seo, home_page)
               VALUES (%s, %s, %s, %s, %s)""", (
                data['performance'],
                data['accessibility'],
                data['best_practices'],
                data['seo'],
                self.home_page_id,
            )
        )

        self.connection.commit()
        self.close_db()

    def desk(self):
        """get desktop pagespeed insights data"""
        r = requests.get(
            f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={self.url}&strategy=desktop')
        if r.status_code == 429:
            print(f' {r.status_code} Too Many Requests. Resend request')
            time.sleep(10)
            self.desk()
        else:
            r = r.json()
            self.desktop = int(r['lighthouseResult']['categories']['performance']['score'] * 100)
            print(f'pagespeed insights desktop: {self.desktop}')

    def mob(self):
        """get mobile pagespeed insights data"""
        r = requests.get(
            f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={self.url}&strategy=mobile')
        if r.status_code == 429:
            print(f' {r.status_code} Too Many Requests. Resend request')
            time.sleep(10)
            self.mob()
        else:
            r = r.json()
            self.mobile = int(r['lighthouseResult']['categories']['performance']['score'] * 100)
            print(f'pagespeed insights mobile: {self.mobile}')

    def get_pagespeed_insights(self):
        """write to db pagespeed insights data for desktop and mobile"""

        # get data
        self.desk()
        self.mob()

        self.open_db()

        # write data to db
        self.cur.execute(
            """INSERT INTO pagespeedinsights (desktop_speed, mobile_speed, home_page)
               VALUES (%s, %s, %s)""", (
                str(self.desktop),
                str(self.mobile),
                self.home_page_id,
            )
        )

        self.connection.commit()
        self.close_db()

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
    # get url in command line
    url = sys.argv[1]

    # create object
    data = GetData(url)

    # write home_page
    data.write_home_page()

    # get data for desktop
    data.get_data_for_desctop()

    # get data fo mobile
    data.get_data_for_mibile()

    # get pagespeed insights
    data.get_pagespeed_insights()
