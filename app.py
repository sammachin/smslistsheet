import os
import tornado.httpserver
import tornado.ioloop
import tornado.web
from twilio import twiml
import gspread
from twilio.rest import TwilioRestClient
import re
import json
from oauth2client.client import SignedJwtAssertionCredentials
from twilio.util import RequestValidator


json_key = json.load(open('creds.json'))
scope = ['https://spreadsheets.google.com/feeds']
credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)

def isadmin(sender, number):
	gc = gspread.authorize(credentials)
	worksheet = gc.open(number).worksheet("admins")
	try:
		member = worksheet.find(sender)
	except:
		member = None
	if member == None:
		return False
	else:
		return True

def get_creds(number):
	gc = gspread.authorize(credentials)
	worksheet = gc.open(number).worksheet("creds")
	creds = worksheet.col_values(2)
	creds = filter(None, creds)
	return creds


class MainHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		self.content_type = 'text/plain'
		self.write("SMS List Sheet")
		self.finish()

		
class MsgHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def post(self):
		text = self.get_argument("Body")
		sender = self.get_argument("From").lstrip("+")
		number = self.get_argument("To").lstrip("+")
		signature = self.request.headers.get('X-Twilio-Signature')
		proto = self.request.headers.get('X-Forwarded-Proto', self.request.protocol ) 
		url = proto + "://"+ self.request.host + self.request.path
		var = self.request.arguments
		for x in var:
			var[x] = ''.join(var[x])
		creds = get_creds(number)
		validator = RequestValidator(creds[1])
		if validator.validate(url, var, signature):
			r = twiml.Response()
			if isadmin(sender, number):
				client = TwilioRestClient(creds[0], creds[1])
				gc = gspread.authorize(credentials)
				worksheet = gc.open(number).worksheet("members")
				members = worksheet.col_values(1)
				members = filter(None, members)
				for member in members:
					client.messages.create(body=text, to_=member, from_=number)
				r.message("Mesaage sent to %s recipients" % len(members))
			else:
				if re.match("^start*", text.lower()):
					gc = gspread.authorize(credentials)
					membersheet = gc.open(number).worksheet("members")
					name = text.lower().lstrip("start").lstrip().capitalize()
					membersheet.append_row([sender, name])
					r.message("Thankyou, you have been added to the list")
				elif re.match("^stop*", text.lower()):
					gc = gspread.authorize(credentials)
					membersheet = gc.open(number).worksheet("members")
					try:
						cell = membersheet.find(sender)
						membersheet.update_cell(cell.row, cell.col, '')
						r.message("You have been removed")
					except:
						r.message("Sorry you are not subscribed with this number")
				else:
					r.message("Sorry message %s not recognised" % text)
			self.content_type = 'text/xml'
			self.write(str(r))
			self.finish()
		else:
			self.clear()
			self.set_status(403)
			self.finish("INVALID SOURCE")
			
			


class ValidateHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def post(self):
		signature = self.request.headers.get('X-Twilio-Signature')
		proto = self.request.headers.get('X-Forwarded-Proto', self.request.protocol ) 
		url = proto + "://" + self.request.host + self.request.path
		var = self.request.arguments
		for x in var:
			var[x] = ''.join(var[x])
		token = "b66cc1f276e50a849da90c9a864cf046"
		validator = RequestValidator(token)
		if validator.validate(url, var, signature):
			r = twiml.Response()
			r.say("Request Validation Passed")
			self.content_type = 'text/xml'
			self.write(str(r))
			self.finish()
		else:
			self.set_status(403)
			self.content_type = 'text/plain'
			self.finish(signature+"\n"+url+"\n"+var)

def main():
	static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
	print static_path
	application = tornado.web.Application([(r"/", MainHandler),
											(r"/message", MsgHandler),
											(r"/validate", ValidateHandler),
											(r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path}),
											])
	http_server = tornado.httpserver.HTTPServer(application)
	port = int(os.environ.get("PORT", 5000))
	http_server.listen(port)
	tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
	main()
	
	

