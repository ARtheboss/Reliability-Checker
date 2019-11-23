from flask import Flask, request

from urllib.request import urlopen
from datetime import datetime

import datetime

import firebase_admin
from firebase_admin import credentials, firestore

import json

app = Flask(__name__)

def getName(og_url):
	if og_url[:4] == "htt":
		og_url = og_url[og_url.find("://")+3:]

	extension = [".com",".co",".org",".edu"]
	for i in extension:
		f = og_url.find(".com")
		if f != -1:
			return og_url[:f]
	return og_url

def readData(inp):
	# scrape all the things

	database = firestore.client()
	col_ref = database.collection('sources') # col_ref is CollectionReference

	doc = col_ref.document(u"{}".format(inp)).get()

	source = doc.to_dict()

	need_update = False
	if source == None:
		need_update = True
	else:
		need_update = (datetime.datetime.now() - datetime.timedelta(days=7) > datetime.datetime.strptime(source['date'],"%m/%d/%Y, %H:%M:%S"))

	if need_update: # then update information

		url = "https://mediabiasfactcheck.com/?s="+inp

		page = urlopen(url)
		byte_version = page.read()
		html = byte_version.decode()

		html = html[html.find("<article class"):]
		new_url = html[html.find('href="')+6:]
		new_url = new_url[:new_url.find('"')]

		html = html[html.find('mh-excerpt">')+12:]

		bias = html[:html.find("These")-1].lower()
		if bias != "satire":
			bias = bias[:-5]

		page = urlopen(new_url)
		byte_version = page.read()
		html = byte_version.decode()

		html = html[html.find("Detailed Report</h3>"):]

		html = html[html.find("<strong>")+8:]
		if html[0] == "<":
			html = html[html.find(">")+1:]
		reporting = html[:html.find("<")].lower()

		html = html[html.find("<strong>")+8:]
		if html[0] == "<":
			html = html[html.find(">")+1:]
		country = html[:html.find("<")]

		html = html[html.find("<strong>")+8:]
		if html[0] == "<":
			html = html[html.find(">")+1:]
		press_freedom = html[:html.find("<")]

		press_freedom = int(press_freedom[press_freedom.find(" ")+1:press_freedom.find("/")])

		print("Bias:",bias)
		print("Factual Reporting:",reporting)
		print("Country Origin:",country)
		print("Press Freedom Rank:",press_freedom)

		url = "https://www.alexa.com/siteinfo/"+og_url
		page = urlopen(url)
		byte_version = page.read()
		html = byte_version.decode()

		html = html[html.find("ThirdFull thissite"):]
		html = html[html.find("<span>")+6:]
		visitors = html[:html.find("<")]
		visitors = str(visitors.replace(',', ''))

		print("Visitors:",visitors)

		vals = {
		   "bias": bias,
		   "reporting": reporting,
		   "country": country,
		   "press_freedom": press_freedom,
		   "visitors": visitors,
		   "date": datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
		}
		col_ref.document(u"{}".format(inp)).set(vals)

		return vals

	else:

		return source


def setUserReviews(url,stars,review,username):

	database = firestore.client()
	user_reviews = database.collection('user-reviews') # user reviews

	review = {
		"review": review,
		"stars": int(stars),
		"username": username,
		"website": url
	}

	user_reviews.document().set(review)

	return "1"

def getUserReview(url):
	database = firestore.client()
	col_ref = database.collection('user-reviews') # col_ref is CollectionReference

	results = col_ref.where('website', '==', url).stream() # one way to query

	d = [x.to_dict() for x in results]

	return d


@app.route('/get_info', methods=["GET"])
def root():
	url = request.args.get('url')
	url = getName(url)

	try:
		int(request.args.get('stars'))
		return setUserReviews(url, request.args.get('stars'), request.args.get('review'), request.args.get('username'))
	except:
		return json.dumps([readData(url), getUserReview(url)], separators=(',', ':'))

if __name__ == "__main__":
	databaseURL = {
	     'databaseURL': "https://reliabilitychecker.firebaseio.com"
	}
	cred = credentials.Certificate("/Users/home/Desktop/firebase-cred.json")
	firebase_admin.initialize_app(cred, databaseURL)

	app.run(host="0.0.0.0", debug=True)

