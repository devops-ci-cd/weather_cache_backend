import logging
import sys

import azure.functions as func

import datetime
import pymssql
import requests
from statistics import mean  # mean(list) returns avarage value
from datetime import date
from time import sleep
from dateutil.relativedelta import relativedelta
from os import getenv


db_server = getenv('azure_db_server_name')
db_user = getenv('DB_USER')
db_password = getenv('password')
db = getenv('azure_db_name')


def build_values_line(response):
    min_temp, max_temp, humidity = [], [], []
    for item in response.json():    
        min_temp.append(item['min_temp'])
        max_temp.append(item['max_temp'])
        humidity.append(item['humidity'])
    return (response.json()[0]['applicable_date'], round(mean(max_temp)), round(mean(min_temp)), round(mean(humidity)))


def main(msg: func.ServiceBusMessage):
    # server='devops-db-server.database.windows.net', user='devops', password='ljksadfhjuyerGFd65', database='weatherdb'
    # St. Petersburg woeid by default
    woeid = 2123260
    # city = 'St Petersburg'
    # fetch "today" for the woeid timezone
    # relativedelta to deal with leap years
    
    try:
      req_day = datetime.datetime.strptime(msg.get_body().decode('utf-8'), '%d%m%Y').date()
    except (ValueError, TypeError):
      logging.error("Errorneous request. Perform highload scale test.")
      logging.info('Python ServiceBus queue trigger processed message: %s', msg.get_body().decode('utf-8'))
      sys.exit(0)

    day_yesterday = (req_day - relativedelta(days=1)).strftime("%Y/%m/%d")
    day_yesterday_year_ago = (req_day - relativedelta(days=1) - relativedelta(years=1)).strftime("%Y/%m/%d")

    # https://www.metaweather.com/api/location/<woeid>/<year>/<month>/<day>/
    resp_yesterday = requests.get(f"https://www.metaweather.com/api/location/{woeid}/{day_yesterday}/")
    resp_yesterday_year_ago = requests.get(f"https://www.metaweather.com/api/location/{woeid}/{day_yesterday_year_ago}/")

    # try to connect to the paused SQL server
    while not ('conn' in locals()):
        try:
            conn = pymssql.connect(server=db_server, user=db_user, password=db_password, database=db)
        except pymssql.StandardError as e:
            logging.error(e.args)
            sleep(3)

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT WeatherCache (Date, MaxTemp, MinTemp, Humidity) VALUES (%s, %d, %d, %d);", build_values_line(resp_yesterday))
        conn.commit()
    except pymssql.StandardError as e:
        logging.error(e.args)

    try:
        cursor.execute(
            "INSERT WeatherCache (Date, MaxTemp, MinTemp, Humidity) VALUES (%s, %d, %d, %d);", build_values_line(resp_yesterday_year_ago))
        conn.commit()
    except pymssql.StandardError as e:
        logging.error(e.args)
    conn.close()

    logging.info('Python ServiceBus queue trigger processed message: %s',
                 day_yesterday)
