# delivery-metrics

## Getting Started

### Step 1 - Initialize a local instance of the database
```
$ cd simpler-grants-sandbox/delivery-metrics/
$ sqlite3 ./db/delivery_metrics.db < ./sql/create_delivery_metrics_db.sql
```

### Step 2 - Load test data into the database
```
$ cd simpler-grants-sandbox/delivery-metrics/src/
$ ./load_json.py ../json/example-01.json
```

### Step 3 - View test data
Use a SQLite browser, such as [https://sqlitebrowser.org](DB Browser for SQLite), to connect to `db/delivery_metrics.db`.

