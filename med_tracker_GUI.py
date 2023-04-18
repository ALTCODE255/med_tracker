from tkinter import *
from med_tracker import *
from datetime import datetime

config = loadConfig("config.json")
max_daily = config["max_daily_dose"] if type(config["max_daily_dose"]) is int else 2
db_name = config["database_name"] + ".db"
createTable(db_name)

window = Tk()
window.geometry("500x300")
window.title("Medication Dose Tracker")

def getLastDoseMsg(db: str, label: Label):
	time_diff = getTimeSinceLastDose(getLastDose(db))
	last_dose_msg = f"Last dose was {time_diff.days} day{'' if time_diff.days == 1 else 's'}, {time_diff.hours} hour{'' if time_diff.hours == 1 else 's'}, and {time_diff.minutes} minute{'' if time_diff.minutes == 1 else 's'} ago."
	label.config(text=last_dose_msg)
	label.grid(row=0, column=0, columnspan=2, pady=5)
	window.after(10000, lambda: getLastDoseMsg(db, label))


last_dose = Label()
getLastDoseMsg(db_name, last_dose)

record_current = Button(text="Record Dose at Current Time", command=lambda: doTally(datetime.now().strftime("%I:%M%p"), db_name, max_daily))
record_current.grid(row=1, column=0, pady=5, padx=10)

undo_record = Button(text="Undo Previous Entry", command=lambda: undoTally(db_name))
undo_record.grid(row=1, column=1, sticky="W", pady=5)

def grabTime(input: Entry):
	time = input.get()
	try:
		datetime.strptime(time, "%I:%M%p")
		doTally(time, db_name, max_daily)
		input.delete(0, END)
	except ValueError:
		input.delete(0, END)
		input.insert(0, "Please use HH:MM(AM/PM) format. Ex. 05:13PM")
	

input_time = Entry(width=50)
record_custom = Button(text="Record Dose at Custom Time:", command=lambda: grabTime(input_time))
record_custom.grid(row=2, column=0, sticky='E', pady=5, padx=10)
input_time.grid(row=2, column=1, sticky="W", pady=5)


def getLogMsg(db: str, label: Label):
	label.config(text="Dose Log (last 10 entries):\n" + getLog(10, db))
	label.grid(row=3, column=0, columnspan=2, pady=15)
	window.after(10000, lambda: getLogMsg(db, label))


log = Label()
getLogMsg(db_name, log)

window.mainloop()