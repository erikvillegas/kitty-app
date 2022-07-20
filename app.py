from flask import Flask, render_template, request
import datetime
import pytz
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

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