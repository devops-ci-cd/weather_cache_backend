import datetime
import logging
import azure.functions as func
import pymssql
import requests
from statistics import mean  # mean(list) returns avarage value
from datetime import date
from time import sleep
from dateutil.relativedelta import relativedelta
from os import getenv

db_server = "getenv"
db_user = "getenv"
db_password = "getenv"
db = "getenv"

def build_values_line(response):
    min_temp, max_temp, humidity = [], [], []
    for item in response.json():    
        min_temp.append(item['min_temp'])
        max_temp.append(item['max_temp'])
        humidity.append(item['humidity'])
    return (response.json()[0]['applicable_date'], round(mean(max_temp)), round(mean(min_temp)), round(mean(humidity)))

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

        # server='devops-db-server.database.windows.net', user='devops', password='ljksadfhjuyerGFd65', database='weatherdb'
    # St. Petersburg woeid by default
    woeid = 2123260
    # city = 'St Petersburg'
    # fetch "today" for the woeid timezone
    # relativedelta to deal with leap years
    day_yesterday = (date.today() - relativedelta(days=1)).strftime("%Y/%m/%d")
    day_yesterday_year_ago = (date.today() - relativedelta(days=1) - relativedelta(years=1)).strftime("%Y/%m/%d")

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
        cursor.executemany(
            "INSERT WeatherCache (Date, MaxTemp, MinTemp, Humidity) VALUES (%s, %d, %d, %d);",
            [
                build_values_line(resp_yesterday),
                build_values_line(resp_yesterday_year_ago)
            ]
        )
        conn.commit()

    except pymssql.StandardError as e:
        logging.error(e.args)
    conn.close()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)


