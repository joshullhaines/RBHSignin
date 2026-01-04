"""
Database helpers.

This is intentionally small for now:
- open a sqlite connection
- ensure required tables exist

We are NOT redesigning the schema in this refactor PR. (A person_id-based schema is planned.)
+ Possiblities of MailChimp or Mailerlite
"""

import sqlite3


def connect(db_path: str = "Information.db") -> sqlite3.Connection:
	"""
	Open a connection to the local SQLite DB.

	Keeping this in one place will make it easier to change DB location later (packaging,
	per-user app data directories, cloud sync, etc.).
	"""
	return sqlite3.connect(db_path)


def ensure_schema(cur: sqlite3.Cursor) -> None:
	"""
	Ensure the core tables exist.

	These statements are intentionally kept identical to the original app's startup schema.
	"""
	cur.execute("CREATE TABLE IF NOT EXISTS VolunteerName(Name PRIMARY KEY, Email, Address, PhoneNumber, RockVilleRes)")
	cur.execute("CREATE TABLE IF NOT EXISTS ClientName(Name PRIMARY KEY, Email, PhoneNumber, RockVilleRes)")       
	cur.execute("CREATE TABLE IF NOT EXISTS ClientSISOLOG(Name, Date, HoursCount, Activity)")     
	cur.execute("CREATE TABLE IF NOT EXISTS SISOLOG(Name, Date, Timein, Timeout)") 


