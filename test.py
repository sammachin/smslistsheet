import gspread
from twilio import twiml
from twilio.rest import TwilioRestClient

twilio_sid = "AC7c58ee44ba5745d0942ddbe0238cf7f2"
twilio_token = "b66cc1f276e50a849da90c9a864cf046"

user = 'sam.machin@gmail.com'
pw = "mechjkhfxdvbszng"

gc = gspread.login(user, pw)
membersheet = gc.open("smslist").worksheet("members")
members = membersheet.col_values(1)
members = filter(None, members)
client = TwilioRestClient(twilio_sid, twilio_token)
for member in members:
	print member
	message = client.messages.create(body="test", to_=member, from_="+447903575680")