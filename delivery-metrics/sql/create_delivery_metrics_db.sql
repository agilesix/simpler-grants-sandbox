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
	points INTEGER NOT NULL DEFAULT 0,
	status TEXT,
	opened_date DATE,
	closed_date DATE,
	is_closed INTEGER,
	parent_issue_guid TEXT,
	epic_id TEXT,
	sprint_id TEXT
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
 