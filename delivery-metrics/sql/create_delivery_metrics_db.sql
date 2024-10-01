# drop tables

DROP TABLE IF EXISTS issue;
DROP TABLE IF EXISTS epic;
DROP TABLE IF EXISTS sprint;
DROP TABLE IF EXISTS deliverable;
DROP TABLE IF EXISTS quad;

# create tables

CREATE TABLE issue (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	guid TEXT UNIQUE NOT NULL,
	title TEXT NOT NULL,
	type TEXT NOT NULL,
	points INTEGER,
	status TEXT,
	opened_at DATE,
	closed_at DATE,
	is_closed INTEGER,
	parent_guid TEXT,
	epic_guid TEXT,
	sprint_guid TEXT
);

CREATE TABLE epic (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	guid TEXT UNIQUE NOT NULL,
	title TEXT NOT NULL
);

CREATE TABLE sprint (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	guid TEXT UNIQUE NOT NULL,
	name TEXT NOT NULL,
	start_date DATE,
	end_date DATE,
	duration INTEGER
);

CREATE TABLE deliverable (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	guid TEXT UNIQUE NOT NULL,
	title TEXT NOT NULL,
	pillar TEXT 
);


CREATE TABLE quad (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	guid TEXT UNIQUE NOT NULL,
	name TEXT NOT NULL,
	start_date DATE,
	end_date DATE,
	duration INTEGER
);
 
