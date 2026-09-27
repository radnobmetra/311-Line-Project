import sqlite3


"""
DATABASE SCHEMA:
TABLES:
app_states (empty)
	app_name
	state
	update_time

user_states (empty)
	app_name
	user_id
	state
	update_time

sessions
	app_name (primary key)
	user_id (primary key)
	id (session id primary key)
	state (info set by us)
	create_time 
	update_time

	
events
	id (primary and foreign key from sessions)
	app_name (same as id)
	user_id (same as id)
	session_id (same as user id)
	invocation_id
	timestamp
	event_data



"""



databasepath = "../../my_agent/.adk/session.db"



def latest_x_sessions(record_amount:int):
	"""
    Returns the lastest X number of sessions from the sessions table.

    Args:
        record_amount (int): Number of records to pull.

    Returns:
        array containing the lastest records
    """

	localdb = sqlite3.connect(databasepath)
	dbcursor = localdb.cursor()
	
	records = dbcursor.execute("SELECT * from sessions")
	values = records.fetchmany(record_amount)
	return values

def sessions_between_two_dates(start_date:int, end_date:int):
	"""
	Returns records between 2 dates. 
	
	Args:
		start_date (int) & end_date (int): date time in seconds

	Returns:
        array containing the lastest records
	"""
	localdb = sqlite3.connect(databasepath)
	dbcursor = localdb.cursor()

	params = (start_date, end_date)
	records = dbcursor.execute("SELECT * from sessions where create_time > ? AND create_time < ?", params)
	values = records.fetchall()
	return values

def custom_query_limited_records(record_amount:int, query:str, params:dict):
	"""
	Returns record_amount of records via a custom query with string. 
	
	Args:
		record_amount (int): Number of records to pull
		query (str): Query in string pattern, use ? for varaibles
		params (dict): parameters for the query ?

	Returns:
        array containing the lastest records
	"""
	localdb = sqlite3.connect(databasepath)
	dbcursor = localdb.cursor()
	records = dbcursor.execute(query, params)
	values = records.fetchmany(record_amount)
	return values

def custom_query_all_records(query:str, params:dict):
	"""
	Returns all records via a custom query with string.
	
	Args:
		query (str): Query in string pattern, use ? for varaibles
		params (dict): parameters for the query ?

	Returns:
        array containing the lastest records
	"""
	localdb = sqlite3.connect(databasepath)
	dbcursor = localdb.cursor()
	records = dbcursor.execute(query, params)
	values = records.fetchall()
	return values

