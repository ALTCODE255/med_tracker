import sys
import sqlite3
from dateutil import relativedelta
from datetime import datetime
import json


def loadConfig(file_path):
	with open(file_path, "r") as f:
		return json.load(f)


def createTable(db: str):
	sqliteConnection = sqlite3.connect(db)
	cursor = sqliteConnection.cursor()
	cursor.execute("CREATE TABLE IF NOT EXISTS Med_Log (id INTEGER PRIMARY KEY, date TEXT, time TEXT)")
	sqliteConnection.commit()
	cursor.close()
	sqliteConnection.close()


def getLog(records: int, db: str) -> str:
	sqliteConnection = sqlite3.connect(db)
	cursor = sqliteConnection.cursor()
	cursor.execute(f"SELECT date, time FROM Med_Log ORDER BY id DESC LIMIT {records}")
	output_list = [" - ".join(result) for result in cursor.fetchall()]
	output_list.reverse()
	cursor.close()
	sqliteConnection.close()
	return "\n".join(output_list)


def getLastDose(db: str) -> datetime:
	sqliteConnection = sqlite3.connect(db)
	cursor = sqliteConnection.cursor()
	cursor.execute(f"SELECT date, time FROM Med_Log ORDER BY id DESC LIMIT 1")
	last_dose = [" - ".join(result) for result in cursor.fetchall()]
	cursor.close()
	sqliteConnection.close()
	dt_last_dose = datetime.strptime(last_dose[0], "%m/%d/%Y - %I:%M%p")
	return dt_last_dose


def getTimeSinceLastDose(last_dose: datetime) -> relativedelta:
	return relativedelta.relativedelta(datetime.now(), last_dose)


def doTally(time: str, db: str, max: int):
	today = datetime.now().strftime("%m/%d/%Y")
	sqliteConnection = sqlite3.connect(db)
	cursor = sqliteConnection.cursor()
	cursor.execute(f"SELECT time FROM Med_Log WHERE date='{today}'")
	output_list = ["".join(result) for result in cursor.fetchall()]
	if len(output_list) < max:
		cursor.execute(f"INSERT INTO Med_Log (date, time) VALUES ('{today}', '{time}')")
	sqliteConnection.commit()
	cursor.close()
	sqliteConnection.close()


def undoTally(db):
	sqliteConnection = sqlite3.connect(db)
	cursor = sqliteConnection.cursor()
	cursor.execute(
		f"DELETE FROM Med_Log where id IN (SELECT id FROM Med_Log ORDER BY id DESC LIMIT 1)"
	)
	sqliteConnection.commit()
	cursor.close()
	sqliteConnection.close()


if __name__ == "__main__":
	config = loadConfig("config.json")
	max_daily = config["max_daily_dose"] if type(config["max_daily_dose"]) is int else 2
	db_name = config["database_name"] + ".db"
	createTable(db_name)
	
	if len(sys.argv) < 2:
		time = datetime.now().strftime("%I:%M%p")
		doTally(time, db_name, max_daily)
		print("Logged! Time is {time}.")
	elif sys.argv[1] == "undo":
		undoTally(db_name)
		print("Done! Previous entry has been undone.")
	elif sys.argv[1] == "log":
		if len(sys.argv) < 3 or not sys.argv[2].isdigit:
			n = max_daily
		else:
			n = int(sys.argv[2])
		time_diff = getTimeSinceLastDose(getLastDose(db_name))
		last_dose_msg = f"Last dose was {time_diff.days} day{'' if time_diff.days == 1 else 's'}, {time_diff.hours} hour{'' if time_diff.hours == 1 else 's'}, and {time_diff.minutes} minute{'' if time_diff.minutes == 1 else 's'} ago."
		print("Medication Log\n---\n" + getLog(n, db_name) + "\n---\n" + last_dose_msg)
	else:
		try:
			datetime.strptime(sys.argv[1], "%I:%M%p")
			time = sys.argv[1]
			doTally(time, db_name, max_daily)
			print(f"Logged! Time is {time}.")
		except ValueError:
			print("Invalid time! Please use HH:MM(AM/PM) format. Ex. 05:13PM", file=sys.stderr)