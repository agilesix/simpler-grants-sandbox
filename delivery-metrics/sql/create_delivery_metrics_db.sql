# drop tables

DROP TABLE IF EXISTS deliverable;
DROP TABLE IF EXISTS epic;
DROP TABLE IF EXISTS issue;
DROP TABLE IF EXISTS issue_history;
DROP TABLE IF EXISTS issue_sprint_map;
DROP TABLE IF EXISTS sprint;
DROP TABLE IF EXISTS quad;

# create tables

CREATE TABLE deliverable (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	guid TEXT UNIQUE NOT NULL,
	title TEXT NOT NULL,
	pillar TEXT, 
	quad_id INTEGER,
	t_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	t_modified TIMESTAMP 
);

CREATE TABLE epic (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	guid TEXT UNIQUE NOT NULL,
	title TEXT NOT NULL,
	deliverable_id INTEGER,
	t_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	t_modified TIMESTAMP 
);

CREATE TABLE issue (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	guid TEXT UNIQUE NOT NULL,
	title TEXT NOT NULL,
	type TEXT NOT NULL,
	points INTEGER NOT NULL DEFAULT 0,
	opened_date DATE,
	closed_date DATE,
	parent_issue_guid TEXT,
	epic_id INTEGER,
	t_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	t_modified TIMESTAMP 
);

CREATE TABLE issue_history (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	issue_id INTEGER NOT NULL,
	status TEXT NOT NULL,
	is_closed INTEGER NOT NULL,
	d_effective DATE NOT NULL,
	t_modified TIMESTAMP,
	UNIQUE(issue_id, d_effective)
);

CREATE TABLE issue_sprint_map (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	issue_id INTEGER NOT NULL,
	sprint_id INTEGER NOT NULL,
	d_effective DATE NOT NULL,
	t_modified TIMESTAMP,
	UNIQUE(issue_id, d_effective)
);

CREATE TABLE sprint (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	guid TEXT UNIQUE NOT NULL,
	name TEXT NOT NULL,
	start_date DATE,
	end_date DATE,
	duration INTEGER,
	quad_id INTEGER,
	t_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	t_modified TIMESTAMP 
);

CREATE TABLE quad (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	guid TEXT UNIQUE NOT NULL,
	name TEXT NOT NULL,
	start_date DATE,
	end_date DATE,
	duration INTEGER,
	t_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	t_modified TIMESTAMP 
);
 
