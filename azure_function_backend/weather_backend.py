import pymssql
import requests
from statistics import mean  # mean(list) returns avarage value
from datetime import date
from time import sleep
from dateutil.relativedelta import relativedelta
from os import getenv

# server='devops-db-server.database.windows.net', user='devops', password='ljksadfhjuyerGFd65', database='weatherdb'
db_server = getenv('DB_SERVER') or 'devops-db-server.database.windows.net'
db_user = getenv('DB_USER') or 'devops'
db_password = getenv('DB_PASSWORD') or 'ljksadfhjuyerGFd65'
db = getenv('DATABASE') or 'weatherdb'


def build_values_line(response):
    min_temp, max_temp, humidity = [], [], []
    for item in response.json():    
        min_temp.append(item['min_temp'])
        max_temp.append(item['max_temp'])
        humidity.append(item['humidity'])
    return (response.json()[0]['applicable_date'], round(mean(max_temp)), round(mean(min_temp)), round(mean(humidity)))


# connection_string = getenv("DATABASE_CONNECTION")
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
while not ('conn' in globals()):
    try:
        conn = pymssql.connect(server=db_server, user=db_user, password=db_password, database=db)
    except pymssql.StandardError as e:
        # Azure !!! log the err
        print("-=-=-=-=-=-=-Log ERROR ERROR ERROR connecting the database-=-=-=-=-=-=-")
        print(e.args)
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
    # Azure !!! log the err
    print("-=-=-=-=-=-=-Log ERROR ERROR ERROR inserting values the database-=-=-=-=-=-=-")
    print(e.args)
conn.close()
