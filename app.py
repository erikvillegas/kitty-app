from unicodedata import decimal
from flask import Flask, render_template, request
import datetime
import pytz
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import math

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

### Routes ###

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/submit', methods = ['POST'])
def submit():
    red = request.form.get("red")
    orange = request.form.get("orange")
    yellow = request.form.get("yellow")
    green = request.form.get("green")
    blue = request.form.get("blue")
    purple = request.form.get("purple")

    print(purple)

    if red == '' and orange == '' and yellow == '' and green == '' and blue == '' and purple == '':
        return "Please enter at least one weight!"

    # Submit elements to Google Sheets
    now = datetime.datetime.now(pytz.timezone('US/Pacific'))   
    timestamp = now.strftime("%-m/%d %-I:%M %p") 
    insertRow = [timestamp, red, orange, yellow, green, blue, purple]
    weights.append_row(insertRow, value_input_option='USER_ENTERED')

    return render_template("submit.html")

@app.route('/profiles')
def profiles():

    # use worksheet to calculate everything
    chart_data = sheet.get_worksheet(1)
    time_strings = chart_data.col_values(1)
    time_codes = chart_data.col_values(2)
    red_weights = chart_data.col_values(5)
    orange_weights = chart_data.col_values(10)
    yellow_weights = chart_data.col_values(14)
    green_weights = chart_data.col_values(18)
    blue_weights = chart_data.col_values(22)
    purple_weights = chart_data.col_values(26)

    kitten_strings = []

    (w, t) = calculate(time_codes, red_weights, 1.0)
    kitten_strings.append(kitten_string(w, t, 'Red'))

    (w, t) = calculate(time_codes, red_weights, 0.5)
    kitten_strings.append(kitten_string(w, t, 'Red'))

    (w, t) = calculate(time_codes, orange_weights, 1.0)
    kitten_strings.append(kitten_string(w, t, 'Orange'))

    (w, t) = calculate(time_codes, orange_weights, 0.5)
    kitten_strings.append(kitten_string(w, t, 'Orange'))

    (w, t) = calculate(time_codes, yellow_weights, 1.0)
    kitten_strings.append(kitten_string(w, t, 'Yellow'))

    (w, t) = calculate(time_codes, yellow_weights, 0.5)
    kitten_strings.append(kitten_string(w, t, 'Yellow'))

    (w, t) = calculate(time_codes, green_weights, 1.0)
    kitten_strings.append(kitten_string(w, t, 'Green'))

    (w, t) = calculate(time_codes, green_weights, 0.5)
    kitten_strings.append(kitten_string(w, t, 'Green'))

    (w, t) = calculate(time_codes, blue_weights, 1.0)
    kitten_strings.append(kitten_string(w, t, 'Blue'))

    (w, t) = calculate(time_codes, blue_weights, 0.5)
    kitten_strings.append(kitten_string(w, t, 'Blue'))

    (w, t) = calculate(time_codes, purple_weights, 1.0)
    kitten_strings.append(kitten_string(w, t, 'Purple'))

    (w, t) = calculate(time_codes, purple_weights, 0.5)
    kitten_strings.append(kitten_string(w, t, 'Purple'))

    return render_template("profiles.html", strings=kitten_strings)

def is_float(element: str):
    try:
        float(element)
        return True
    except ValueError:
        return False

def kitten_string(weight_difference, time_difference, kitten):
    gain_loss = 'gained' if weight_difference >= 0 else 'lost'
    return f'{kitten} has {gain_loss} {abs(weight_difference)} grams in the last {math.trunc(time_difference)} hours'

def calculate(times, weights: 'list[str]', time_diff):

    # clean values
    times = list(map(lambda time:  float(time) if (is_float(time)) else 0, times))
    weights = list(map(lambda weight:  int(weight) if (weight.isnumeric()) else 0, weights))

    # truncate any times that don't have any weights
    times = times[0 : len(weights)]

    print(f'length of weights: {len(weights)}')
    print(f'length of times: {len(times)}')

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
