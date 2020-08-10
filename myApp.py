#!/usr/bin/env python3
import argparse
import sys
import sqlite3
from datetime import datetime
from datetime import date
import random
import string
import time


help_message = "Required and integer argument to specify an action!\n\
1 for creation of the database\n\
2 for insertion of a record in format \"Surname Name Second Name Birthdate Gender\"\n\
3 show unique names and birthdates, sort by names, with age\n\
4 autofill 1,000,000 lines with dummy data\n\
5 show all males with surname starts with 'F'"


def connect_db(name):
	return sqlite3.connect(name)


def get_cursor(connection):
	return connection.cursor()


def close_db(connection):
	connection.close()


def show_help():
	print(help_message)
	exit(1)


def create_db(connection, cursor):
	print("Creating table...")
	cursor.execute("CREATE TABLE names\
                      (name text, birthdate text, gender text)")

	print("Done!")


def insert_records(connection, cursor, records):
	# TODO: no input filtering, danger of SQL Injection
	cursor.executemany("INSERT INTO names VALUES (?, ?, ?)", records)
	connection.commit()
	print("New record inserted.")


def show_unique(cursor):
	for row in cursor.execute("SELECT * FROM names GROUP BY name, birthdate ORDER BY name"):
		birthdate = datetime.strptime(row[1], '%d.%m.%Y')
		current = date.today()
		age = current.year - birthdate.year - ((current.month, current.day) <
		                                       (birthdate.month, birthdate.day))
		print(row[0] + "\t" + row[1] + "\t" + row[2] + "\t" + str(age))


def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def generate_record():
	name = (get_random_string(8).capitalize() + " " +
	        get_random_string(6).capitalize() + " " +
	        get_random_string(9).capitalize())

	birthdate = (str(random.randrange(1, 28)) + "." +
	             str(random.randrange(1, 12)) + "." +
	             str(random.randrange(1900, 2019)))

	gender = random.choice(('F', 'M'))

	return (name, birthdate, gender)


def autofill_dummy(connection, cursor):
	records = []
	for i in range (1000000):
		records.append(generate_record())

	insert_records(connection, cursor, records)
	print("Done, 1,000,000 names inserted")


def show_males_with_f(cursor):
	timestamp = time.time()
	for row in cursor.execute("SELECT * FROM names WHERE gender='M' AND name LIKE 'f%'"):
		print(row[0] + "\t" + row[1] + "\t" + row[2])

	time_elapsed = time.time() - timestamp
	print("Done in " + str(time_elapsed) + "s")

def main():
	# check if a mode to run is specified
	try:
		mode = int(sys.argv[1])
	except (ValueError, IndexError):
		show_help()

	if mode < 1 or mode > 5:
		show_help()

	# Open connection to the DB
	connection = connect_db('names.db')
	cursor = get_cursor(connection)


	# Do the specified action
	if mode == 1:
		create_db(connection, cursor) # Create DB
	elif mode == 2:
		try:
			insert_records(connection, cursor, [(str(sys.argv[2]) + " " + str(sys.argv[3]) +
			               " " + str(sys.argv[4]), str(sys.argv[5]),
			               str(sys.argv[6]))]) # Insert record
		except IndexError:
			print("You need to specify the data in the following format:\n\
<SURNAME> <NAME> <SECOND NAME> <BIRTH DATE> <GENDER>\n\
Birht date must be in format DD.MM.YYYY, e.g. 23.08.1986\n\
Gender can be M or F.\n\
Example input: Zhukov Oleg Petrovich 23.08.1986 M")

	elif mode == 3:
		show_unique(cursor) # Select unique
	elif mode == 4:
		autofill_dummy(connection, cursor) # Fill dummy data
	elif mode == 5:
		show_males_with_f(cursor) # Show males with names from F


	close_db(connection)
	exit(0)


if __name__ == '__main__':
	main()
