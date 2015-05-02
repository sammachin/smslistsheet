import gspread
import json
from oauth2client.client import SignedJwtAssertionCredentials



json_key = json.load(open('creds.json'))
scope = ['https://spreadsheets.google.com/feeds']
credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)

number = "442033226517"

gc = gspread.authorize(credentials)
worksheet = gc.open(number).worksheet("creds")
creds = worksheet.col_values(2)
creds = filter(None, creds)
