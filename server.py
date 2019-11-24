from flask import Flask, request

from urllib.request import urlopen
from datetime import datetime

import datetime

import firebase_admin
from firebase_admin import credentials, firestore

import json

import requests

app = Flask(__name__)

def getName(og_url):
	if og_url[:4] == "htt":
		og_url = og_url[og_url.find("://")+3:]

	extension = [".com",".co",".org",".edu"]
	for i in extension:
		f = og_url.find(i)
		if f != -1:
			return og_url[:f]
	return og_url

def readData(inp):

	print(inp)
	# scrape all the things

	database = firestore.client()
	col_ref = database.collection('sources') # col_ref is CollectionReference

	doc = col_ref.document(u"{}".format(getName(inp))).get()

	source = doc.to_dict()

	need_update = (source == None) or (datetime.datetime.now() - datetime.timedelta(days=7) > datetime.datetime.strptime(source['date'],"%m/%d/%Y, %H:%M:%S"))

	print(need_update)

	if need_update: # then update information

		url = "https://mediabiasfactcheck.com/?s="+getName(inp)

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

		new_url = "https://www.alexa.com/siteinfo/"+inp
		print(new_url)
		page = urlopen(new_url)
		byte_version = page.read()
		html = byte_version.decode()

		html = html[html.find("ThirdFull thissite"):]
		html = html[html.find("<span>")+6:]
		linkins = html[:html.find("<")]
		linkins = int(linkins.replace(',', ''))

		html = html[html.find('rankmini-rank">')+15:]
		html = html[html.find('</span>')+7:]
		ranking = int(html[:html.find("\n")].replace(',', ''))

		html = html[html.find('class="interests"')+7:]
		html = html[html.find('descriptionText">')+17:]
		category = html[:html.find('</div>')]

		r = requests.get(url = "https://archive.org/wayback/available?url="+inp)
		data = r.json()

		last_updated = datetime.datetime.strptime(data["archived_snapshots"]["closest"]["timestamp"], "%Y%m%d%H%M%S").strftime("%m/%d/%Y, %H:%M:%S")

		vals = {
		   "bias": bias,
		   "reporting": reporting,
		   "country": country,
		   "press_freedom": press_freedom,
		   "links": linkins,
		   "ranking": ranking,
		   "category": category,
		   "last_updated": last_updated,
		   "date": datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
		}
		col_ref.document(u"{}".format(getName(inp))).set(vals)

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
	if request.args.get('login') != None:

		database = firestore.client()
		col_ref = database.collection('users') # col_ref is CollectionReference

		results = col_ref.where('username', '==', request.args.get('login')).stream()

		if results[0]['hash'] == request.args.get('hash'):
			return "1"
		else:
			return "0"


	elif request.args.get('signup') != None:

		database = firestore.client()
		col_ref = database.collection('users') # col_ref is CollectionReference

		vals = {
			"username":request.args.get('signup'),
			"password":request.args.get('hash')
		}

		col_ref.document().set(vals)

		return "1"

	else:

		og_url = request.args.get('url')

		if "/" in og_url:
			og_url = og_url[:og_url.rfind("/")]

		url = getName(og_url)

		print(og_url)

		try:
			int(request.args.get('stars'))
			return setUserReviews(url, request.args.get('stars'), request.args.get('review'), request.args.get('username'))
		except:
			return json.dumps([readData(og_url), getUserReview(url)], separators=(',', ':'))

if __name__ == "__main__":
	databaseURL = {
	     'databaseURL': "https://reliabilitychecker.firebaseio.com"
	}
	cred = credentials.Certificate("/Users/home/Desktop/firebase-cred.json")
	firebase_admin.initialize_app(cred, databaseURL)

	app.run(host="0.0.0.0", debug=True)

