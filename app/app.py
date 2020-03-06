import json
import os
import sqlite3
import time
import warnings
# We disable FutureWarnings caused by Pandas 0.25.3 instructing us to replace our msgpack based deserialization with
# pyarrow. Unfortunately, pyarrow has a bug making its usage impossible for our use cases, so we stick to msgpack, but
# don't want to flood ourselves with warnings.
warnings.simplefilter(action='ignore', category=FutureWarning)

from flask import Flask, request

from .cache import get_forecast, get_model
from .model import best_hour, overview_next_day
from . import push


app = Flask(__name__,
            static_url_path='',
            static_folder='static')


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/api/v1/current-emission-intensity')
def current_emission_intensity():
    model = get_model()
    return model


@app.route('/api/v1/greenest-period/<period>/<horizon>', methods=['GET'])
def greenest_hour(period, horizon):
    period = int(period)
    horizon = int(horizon)
    forecast = get_forecast()
    return best_hour(forecast, period, horizon)


@app.route('/api/v1/next-day')
def next_day():
    forecast = get_forecast()
    return overview_next_day(forecast)


@app.route('/api/v1/save-subscription', methods=['POST'])
def save_subscription():
    try:
        push.save_subscription(request.data.decode('ascii'))
        return {'success': True}
    except Exception as e:
        print(e)
        return {'success': False}


@app.route('/api/v1/remove-subscription', methods=['POST'])
def remove_subscription():
    try:
        push.remove_subscription(request.data.decode('ascii'))
        return {'success': True}
    except Exception as e:
        print(e)
        return {'success': False}
