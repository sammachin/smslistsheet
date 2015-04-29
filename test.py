import gspread
from twilio import twiml
from twilio.rest import TwilioRestClient

twilio_sid = "AC7c58ee44ba5745d0942ddbe0238cf7f2"
twilio_token = "b66cc1f276e50a849da90c9a864cf046"

user = 'sam.machin@gmail.com'
pw = "mechjkhfxdvbszng"

gc = gspread.login(user, pw)
membersheet = gc.open("smslist").worksheet("members")
try:
	cell = membersheet.find(number)
	membersheet.update_cell(cell.row, cell.col, '')
	message = "You have been removed"
except:
	message = "Sorry you are not subscribed with this number"
