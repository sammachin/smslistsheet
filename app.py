import os
import tornado.httpserver
import tornado.ioloop
import tornado.web
from twilio import twiml
import gspread
from twilio.rest import TwilioRestClient

twilio_sid = "AC7c58ee44ba5745d0942ddbe0238cf7f2"
twilio_token = "b66cc1f276e50a849da90c9a864cf046"

user = 'sam.machin@gmail.com'
pw = "mechjkhfxdvbszng"

def isadmin(number):
	gc = gspread.login(user, pw)
	worksheet = gc.open("smslist").worksheet("admins")
	try:
		sender = worksheet.find(number)
	except:
		sender = None
	if sender == None:
		return False
	else:
		return True



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
		r = twiml.Response()
		if isadmin(sender):
			gc = gspread.login(user, pw)
			membersheet = gc.open("smslist").worksheet("members")
			members = membersheet.col_values(1)
			members = filter(None, members)
			client = TwilioRestClient(twilio_sid, twilio_token)
			for member in members:
					message = client.messages.create(body=text, to_=member, from_="+447903575680")
			r.message("Mesaage sent to %s recipients" % len(members))
		else:
			if text.split(" ")[0].lower == "join":
				gc = gspread.login(user, pw)
				membersheet = gc.open("smslist").worksheet("members")
				name = text.lower().lstrip("start").lstrip().capitalize()
				membersheet.append_row([sender, name])
				r.message("Thankyou, you have been added to the list")
			elif text.split(" ")[0].lower == "leave":
				gc = gspread.login(user, pw)
				membersheet = gc.open("smslist").worksheet("members")
				try:
					cell = membersheet.find(sender)
					membersheet.update_cell(cell.row, cell.col, '')
					r.message = "You have been removed"
				except:
					r.message = "Sorry you are not subscribed with this number"
			else:
				r.message("Sorry message not recognised")
		self.content_type = 'text/xml'
		self.write(str(r))
		self.finish()


def main():
	static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
	print static_path
	application = tornado.web.Application([(r"/", MainHandler),
											(r"/message", MsgHandler),
											(r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path}),
											])
	http_server = tornado.httpserver.HTTPServer(application)
	port = int(os.environ.get("PORT", 5000))
	http_server.listen(port)
	tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
	main()
	
	

