import time
import pandas as pd
import redis
from flask import Flask, render_template
import os
from dotenv import load_dotenv

load_dotenv() 
cache = redis.Redis(host=os.getenv('REDIS_HOST'), port=6379,  password=os.getenv('REDIS_PASSWORD'))
app = Flask(__name__)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    return render_template('hello.html', name= "BIPM", count = count)

@app.route('/titanic')
def titanic():
    count = get_hit_count()
    titanic_data = pd.read_csv('titanic.csv')
    titanic_data_head = titanic_data.head(5)

    titanic_survived = titanic_data['survived'].value_counts()
    titanic_survived_men = titanic_data.loc[
        (titanic_data['survived'] == 1) & (titanic_data['sex'] == 'male')
    ].shape[0]
    titanic_survived_women = titanic_data.loc[
        (titanic_data['survived'] == 1) & (titanic_data['sex'] == 'female')
    ].shape[0]

    return render_template(
        'titanic.html',
        count=count,
        titanic_data=titanic_data_head,
        titanic_survived_men=titanic_survived_men,
        titanic_survived_women=titanic_survived_women
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)