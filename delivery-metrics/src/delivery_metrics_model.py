
class DeliveryMetricsModel:

	def __init__(self, dbh):
		self.dbh = dbh


	def syncSprint(self, sprint: dict) -> int | None:

		# validation
		if not isinstance(sprint, dict):
			return None

		guid = sprint.get('guid')
		name = sprint.get('name')
		start = sprint.get('start_date')
		end = sprint.get('end_date')
		duration = sprint.get('duration')

		sql = "insert into sprint(guid, name, start_date, end_date, duration) values (?, ?, ?, ?, ?) on conflict(guid) do update set name = ?, start_date = ?, end_date = ?, duration = ?"

		data = (guid, name, start, end, duration, name, start, end, duration)

		cursor = self.dbh.cursor()
		cursor.execute(sql, data)
		last_row_id = cursor.lastrowid
		self.dbh.commit()
		cursor.close()

		return last_row_id


	def syncEpic(self, epic: dict) -> int | None:

		# validation
		if not isinstance(epic, dict):
			return None

		guid = epic.get('guid')
		title = epic.get('title')

		sql = "insert into epic(guid, title) values (?, ?) on conflict(guid) do update set title = ?"
		 
		data = (guid, title, title)

		cursor = self.dbh.cursor()
		cursor.execute(sql, data)
		last_row_id = cursor.lastrowid
		self.dbh.commit()
		cursor.close()

		return last_row_id


	def syncIssue(self, issue: dict) -> int | None:

		# validation
		if not isinstance(issue, dict):
			return None

		guid = issue.get('guid')
		title = issue.get('title')
		t = issue.get('type')
		points = issue.get('points')
		status = issue.get('status')
		opened_date = issue.get('opened_date')
		closed_date = issue.get('closed_date')
		is_closed = issue.get('is_closed')
		parent_guid = issue.get('parent_guid')
		epic_id = issue.get('epic_id')
		sprint_id = issue.get('sprint_id')

		sql = "insert into issue (guid, title, type, points, status, opened_date, closed_date, is_closed, parent_issue_guid, epic_id, sprint_id) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) on conflict(guid) do update set title = ?, type = ?, points = ?, status = ?, opened_date = ?, closed_date = ?, is_closed = ?, parent_issue_guid = ?, epic_id = ?, sprint_id = ?"

		data = (guid, title, t, points, status, opened_date, closed_date, is_closed, parent_guid, epic_id, sprint_id, title, t, points, status, opened_date, closed_date, is_closed, parent_guid, epic_id, sprint_id)

		#print("****\nSQL = {}".format(sql))
		#print("data = {}".format(data))

		cursor = self.dbh.cursor()
		cursor.execute(sql, data)
		last_row_id = cursor.lastrowid
		self.dbh.commit()
		cursor.close()

		return last_row_id
