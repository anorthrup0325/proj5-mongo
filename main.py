"""
Flask web app connects to Mongo database.
Keep a simple list of dated memoranda.

Representation conventions for dates: 
   - In the session object, date or datetimes are represented as
   ISO format strings in UTC.  Unless otherwise specified, this
   is the format passed around internally. Note that ordering
   of ISO format strings is consistent with date/time order
   - User input/output is in local (to the server) time
   - Database representation is as MongoDB 'Date' objects
   Note that this means the database may store a date before or after
   the date specified and viewed by the user, because 'today' in
   Greenwich may not be 'today' here. 
"""

import flask
from flask import render_template
from flask import request
from flask import url_for
from flask import redirect

import json
import logging

# Date handling 
import arrow # Replacement for datetime, based on moment.js
import datetime # But we may still need time
from dateutil import tz  # For interpreting local times

# Mongo database
from pymongo import MongoClient
from bson.objectid import ObjectId

###
# Globals
###
import CONFIG

app = flask.Flask(__name__)

try: 
    dbclient = MongoClient(CONFIG.MONGO_URL)
    db = dbclient.memos
    collection = db.dated

except:
    print("Failure opening database.  Is Mongo running? Correct password?")
    sys.exit(1)

import uuid
app.secret_key = str(uuid.uuid4())

###
# Pages
###

@app.route("/")
@app.route("/index")
def index():
  app.logger.debug("Main page entry")
  flask.session['memos'] = get_memos()
  for memo in flask.session['memos']:
      break
      app.logger.debug("Got Memo: " + str(memo))
  return flask.render_template('index.html')


# We don't have an interface for creating memos yet
@app.route("/create")
def create():
	app.logger.debug("Create")
	return flask.render_template('create.html')

@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('page_not_found.html',
                                 badurl=request.base_url,
                                 linkback=url_for("index")), 404

#################
#
# Url scripts
#
#################

@app.route("/_create")
def func_create():
	app.logger.debug("Creating new memo")
	t_date = request.args.get('Date')
	t_memo = request.args.get('Memo')
	t_offset = request.args.get('offset', type=int)
	app.logger.debug("New memo: "+t_date+","+str(t_offset)+":"+t_memo)
	t_date = arrow.get(t_date, "MM/DD/YYYY hh:mm A")
	t_tz = timezoned(t_offset)
	app.logger.debug(t_tz)
	t_date = t_date.replace(tzinfo=t_tz)
	put_memo(t_date, t_memo)
	return redirect(url_for('index'))

@app.route("/_delete")
def func_delete():
	app.logger.debug("Deleting a memo")
	t_id = request.args.get('id')
	app.logger.debug("Deleting: "+t_id)
	remove_memo(t_id)
	return redirect(url_for('index'))

#################
#
# Functions used within the templates
#
#################

@app.template_filter( 'fmtdate' )
def format_arrow_date( date ):
	try:
		normal = arrow.get( date )
		return normal.to('local').format("ddd MM/DD/YYYY hh:mm A")
	except:
		return "(bad date)"

@app.template_filter( 'humanize' )
def humanize_arrow_date( date ):
    """
    Date is internal UTC ISO format string.
    Output should be "today", "yesterday", "in 5 days", etc.
    Arrow will try to humanize down to the minute, so we
    need to catch 'today' as a special case. 
    """
    try:
        then = arrow.get(date).to('local')
        now = arrow.utcnow().to('local')
        if then.date() == now.date():
            human = "Today"
        else: 
            human = then.humanize(now)
            if human == "in a day":
                human = "Tomorrow"
    except: 
        human = format_arrow_date(date)
    return human.capitalize()


#############
#
# Functions available to the page code above
#
##############
def get_memos():
    """
    Returns all memos in the database, in a form that
    can be inserted directly in the 'session' object.
    """
    records = [ ]
    for record in collection.find( { "type": "dated_memo" } ):
        record['date'] = arrow.get(record['date']).isoformat()
        record['time'] = arrow.get(record['date']).timestamp
        record['_id'] = str(record['_id'])
        record['text'] = str(record['text'].encode('ascii','xmlcharrefreplace'), "utf-8")
        records.append(record)
    records.sort(key=lambda x: x['time'])
    return records 


def put_memo(dt, mem):
	"""
	Place memo into database
	Args:
		dt: Datetime (arrow) object
		mem: Text of memo
	"""
	record = {
		"type": "dated_memo", 
		"date": dt.to('utc').naive,
		"text": mem
	}
	collection.insert(record)
	return 

def remove_memo(mid):
	"""
	Remove memo from database
	Args:
		mid: Memo _id attribute (string)
	"""
	record = {
		"_id": ObjectId(mid)
	}
	collection.remove(record)
	return 

def twoChars(num):
	if num < 10:
		return "0"+str(num)
	return str(num)

def timezoned(minutes):
	t_str = ""
	if minutes >= 0:
		t_str += "+"
	else:
		t_str += "-"
		minutes = abs(minutes)
	t_hours = minutes // 60
	t_str += twoChars(t_hours) + ":"
	minutes -= t_hours * 60
	t_str += twoChars(minutes)
	return t_str

if __name__ == "__main__":
    # App is created above so that it will
    # exist whether this is 'main' or not
    # (e.g., if we are running in a CGI script)
    app.debug=CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    # We run on localhost only if debugging,
    # otherwise accessible to world
    if CONFIG.DEBUG:
        # Reachable only from the same computer
        app.run(port=CONFIG.PORT)
    else:
        # Reachable from anywhere 
        app.run(port=CONFIG.PORT,host="0.0.0.0")

    
