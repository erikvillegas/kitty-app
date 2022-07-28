from unicodedata import decimal
from flask import Flask, render_template, request, url_for
import datetime
from datetime import timedelta
import pytz
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import math
import json
import statistics
from typing import Iterable 

app = Flask(__name__)

### Google Spreadsheet API setup ###

google_creds = {
  "type": "service_account",
  "project_id": "kittens-356816",
  "private_key_id": "56b95e3b27f31517a7da50c1819fea92b2670787",
  "private_key": os.environ['PRIVATE_KEY'].replace('\\n', '\n'),
  "client_email": os.environ['CLIENT_EMAIL'],
  "client_id": "102344037164205113348",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/kitten-tracker%40kittens-356816.iam.gserviceaccount.com"
}



scope = ['https://www.googleapis.com/auth/spreadsheets']
creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open_by_key('1XMPMgAW98UtbGX7EI0ovv8HQV3-cnXUaMB-xof9AgfI')
weights = sheet.get_worksheet(0)

scores = {}

### Routes ###

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/latest_weights')
def latest_weights():

    return json.dumps({
        'red': int(weights.col_values(2)[-1]),
        'orange': int(weights.col_values(3)[-1]),
        'yellow': int(weights.col_values(4)[-1]),
        'green': int(weights.col_values(5)[-1]),
        'blue': int(weights.col_values(6)[-1]),
        'purple': int(weights.col_values(7)[-1])
    }) 

@app.route('/weight_submit')
def weight_submit():

    # extremely hacky way to prevent others from using this feature 😵‍💫
    if request.remote_addr != '45.23.137.9' and request.remote_addr != '127.0.0.1':
        return
    
    red = request.args.get('red')
    orange = request.args.get('orange')
    yellow = request.args.get('yellow')
    green = request.args.get('green')
    blue = request.args.get('blue')
    purple = request.args.get('purple')

    if red == '' and orange == '' and yellow == '' and green == '' and blue == '' and purple == '':
        return "" # no-op
    else:
        # Submit elements to Google Sheets
        now = datetime.datetime.now(pytz.timezone('US/Pacific'))   
        timestamp = now.strftime("%-m/%d %-I:%M %p") 
        insertRow = [timestamp, red, orange, yellow, green, blue, purple]
        weights.append_row(insertRow, value_input_option='USER_ENTERED')        

    return url_for('profiles')

@app.route('/profiles')
def profiles():

    # use worksheet to calculate everything
    chart_data = sheet.get_worksheet(1)
    time_codes = chart_data.col_values(2)
    red_weights = chart_data.col_values(5)
    orange_weights = chart_data.col_values(10)
    yellow_weights = chart_data.col_values(14)
    green_weights = chart_data.col_values(18)
    blue_weights = chart_data.col_values(22)
    purple_weights = chart_data.col_values(26)

    red_gains_24 = calculate_gains(time_codes, red_weights, 1.0)
    red_gains_12 = calculate_gains(time_codes, red_weights, 0.5)

    red_strings = list(flatten([
        format_weight(red_gains_24),
        format_weight(red_gains_12),
        average_gains(time_codes, red_weights)
    ]))

    orange_gains_24 = calculate_gains(time_codes, orange_weights, 1.0)
    orange_gains_12 = calculate_gains(time_codes, orange_weights, 0.5)

    orange_strings = list(flatten([
        format_weight(orange_gains_24),
        format_weight(orange_gains_12),
        average_gains(time_codes, orange_weights)
    ]))

    yellow_gains_24 = calculate_gains(time_codes, yellow_weights, 1.0)
    yellow_gains_12 = calculate_gains(time_codes, yellow_weights, 0.5)

    yellow_strings = list(flatten([
        format_weight(yellow_gains_24),
        format_weight(yellow_gains_12),
        average_gains(time_codes, yellow_weights)
    ]))

    green_gains_24 = calculate_gains(time_codes, green_weights, 1.0)
    green_gains_12 = calculate_gains(time_codes, green_weights, 0.5)

    green_strings = list(flatten([
        format_weight(green_gains_24),
        format_weight(green_gains_12),
        average_gains(time_codes, green_weights)
    ]))

    blue_gains_24 = calculate_gains(time_codes, blue_weights, 1.0)
    blue_gains_12 = calculate_gains(time_codes, blue_weights, 0.5)

    blue_strings = list(flatten([
        format_weight(blue_gains_24),
        format_weight(blue_gains_12),
        average_gains(time_codes, blue_weights)
    ]))

    purple_gains_24 = calculate_gains(time_codes, purple_weights, 1.0)
    purple_gains_12 = calculate_gains(time_codes, purple_weights, 0.5)

    purple_strings = list(flatten([
        format_weight(purple_gains_24),
        format_weight(purple_gains_12),
        average_gains(time_codes, purple_weights)
    ]))

    scores = {
        'red': emoji_score(red_gains_24[0]),
        'orange': emoji_score(orange_gains_24[0]),
        'yellow': emoji_score(yellow_gains_24[0]),
        'green': emoji_score(green_gains_24[0]),
        'blue': emoji_score(blue_gains_24[0]),
        'purple': emoji_score(purple_gains_24[0])
    }

    last_weights = {
        'red': red_weights[-1],
        'orange': orange_weights[-1],
        'yellow': yellow_weights[-1],
        'green': green_weights[-1],
        'blue': blue_weights[-1],
        'purple': purple_weights[-1]
    }

    return render_template("profiles.html", 
        red=red_strings, 
        orange=orange_strings, 
        yellow=yellow_strings, 
        green=green_strings, 
        blue=blue_strings, 
        purple=purple_strings,
        scores=scores,
        last_weights=last_weights)

def is_float(element: str):
    try:
        float(element)
        return True
    except ValueError:
        return False

def emoji_score(gain):
    if gain >= 14:
        return '😎'
    elif gain >= 12:
        return '🙂'
    elif gain >= 10:
        return '🤔'
    elif gain >= 6:
        return '😟'
    else:
        return '🚨'

def format_weight(tuple):
    weight_difference, time_difference = tuple
    gain_loss = 'Gained' if weight_difference >= 0 else 'Lost'
    grams = 'grams' if abs(weight_difference) > 1 else 'gram'
    return f'{gain_loss} {abs(weight_difference)} {grams} since weigh-in {math.trunc(time_difference)} hours ago'

def calculate_gains(times, weights: 'list[str]', time_diff):

    # clean values
    times = list(map(lambda time:  float(time) if (is_float(time)) else 0, times))
    weights = list(map(lambda weight:  int(weight) if (weight.isnumeric()) else 0, weights))

    # truncate any times that don't have any weights
    times = times[0 : len(weights)]

    last_weight = 0
    last_weight_idx = 0
    for index, value in enumerate(weights):
        last_weight = value
        last_weight_idx = index

    last_weight_code = times[last_weight_idx]

    target_time = last_weight_code - time_diff 
    time_code_differences = list(map(lambda code: code - target_time, times))

    matched_time_code = 1000
    matched_time_code_idx = 0
    for index, value in enumerate(time_code_differences):
        weight = weights[index]

        if value < abs(matched_time_code) and weight != 0:
            matched_time_code = value
            matched_time_code_idx = index
            # print(f'closer time code found: {times[matched_time_code_idx]} ({matched_time_code}) -- weight: {weight}')

    # print(f'closest time code: {times[matched_time_code_idx]}')
    # print(f'matching weight: {weights[matched_time_code_idx]}')

    comparison_weight = weights[matched_time_code_idx]
    comparison_weight_code = times[matched_time_code_idx]

    weight_difference = last_weight - comparison_weight
    hour_difference = (last_weight_code - comparison_weight_code) * 24

    return (weight_difference, hour_difference)


def average_gains(times, weights):
    # clean values
    times = list(map(lambda time:  float(time) if (is_float(time)) else 0, times))
    weights = list(map(lambda weight:  int(weight) if (weight.isnumeric()) else 0, weights))

    weights_start_idx = next(i for i,v in enumerate(weights) if int(v) > 0)
    times = times[weights_start_idx : len(weights)]
    weights = weights[weights_start_idx :]

    # hack to get the last day to be read too
    times.append(1000)

    averages = []

    start_idx = 0
    current_day = math.trunc(times[0])
    for idx, value in enumerate(times):
        if value == 0: continue

        if math.trunc(value) != current_day and idx != 0:

            day_weights = list(filter(lambda w: w > 0, weights[start_idx : idx]))
            avg = statistics.fmean(day_weights)

            averages.append((current_day, round(avg, 2)))

            current_day = math.trunc(value)
            start_idx = idx

    # previous = averages[0][1]
    # for day, weight in averages[1:]:
    #     print(f'On day {day} gain was {round(weight - previous)} grams')
    #     previous = weight

    # def gain(averages, i, j):
    #     difference = averages[i][1] - averages[j][1]
    #     symbol = '+' if difference > 0 else '-'
    #     #return f'{symbol}{round(difference)} grams'
    #     return difference

    strings = []

    current_gain = averages[-1][1] - averages[-2][1]
    strings.append(f'Today: Gained {round(current_gain, 1)} grams from yesterday\'s average')

    previous_gain = averages[-2][1] - averages[-3][1]
    previous_day = (datetime.datetime.now() - timedelta(2)).strftime('%A')
    strings.append(f'Yesterday: Gained {round(previous_gain, 1)} grams from {previous_day}\'s average')

    previous_gain = averages[-3][1] - averages[-4][1]
    previous_previous_day = (datetime.datetime.now() - timedelta(3)).strftime('%A')
    strings.append(f'{previous_day}: Gained {round(previous_gain, 1)} grams from {previous_previous_day}\'s average')
    
    window = [
        averages[-1][1] - averages[-2][1],
        averages[-2][1] - averages[-3][1],
        averages[-3][1] - averages[-4][1],
        averages[-4][1] - averages[-5][1]
    ]
    window_avg = statistics.fmean(window)

    return strings

    # (w, t) = calculate(time_codes, raw_weights, 3.0)
    # snapshot_difference = w/3.0

    # print(f'72-hour jump on average is {snapshot_difference}')
    # print(f'Final 72-hour averages is {snapshot_difference + }')

def flatten(items):
    """Yield items from any nested iterable; see Reference."""
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            for sub_x in flatten(x):
                yield sub_x
        else:
            yield x