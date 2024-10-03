
class DeliveryMetricsModel:

	def __init__(self, dbh):
		self.dbh = dbh


	def syncQuad(self, quad: dict) -> int:
	
		# validation
		if not isinstance(quad, dict):
			return None

		guid = quad.get('guid')
		name = quad.get('name')
		start = quad.get('start_date')
		end = quad.get('end_date')
		duration = quad.get('duration')

		sql = "insert into quad(guid, name, start_date, end_date, duration) values (?, ?, ?, ?, ?) on conflict(guid) do update set name = ?, start_date = ?, end_date = ?, duration = ? returning id"
		data = (guid, name, start, end, duration, name, start, end, duration)
		row_id = self._execute(sql, data)

		return row_id


	def syncDeliverable(self, deliverable: dict) -> int:
		
		# validation
		if not isinstance(deliverable, dict):
			return None

		guid = deliverable.get('guid')
		title = deliverable.get('title')
		pillar = deliverable.get('pillar')

		sql = "insert into deliverable(guid, title, pillar) values (?, ?, ?) on conflict(guid) do update set title = ?, pillar = ? returning id"
		data = (guid, title, pillar, title, pillar)
		row_id = self._execute(sql, data)

		return row_id


	def syncSprint(self, sprint: dict) -> int:

		# validation
		if not isinstance(sprint, dict):
			return None

		guid = sprint.get('guid')
		name = sprint.get('name')
		start = sprint.get('start_date')
		end = sprint.get('end_date')
		duration = sprint.get('duration')

		sql = "insert into sprint(guid, name, start_date, end_date, duration) values (?, ?, ?, ?, ?) on conflict(guid) do update set name = ?, start_date = ?, end_date = ?, duration = ? returning id"
		data = (guid, name, start, end, duration, name, start, end, duration)
		row_id = self._execute(sql, data)

		return row_id


	def syncEpic(self, epic: dict) -> int:

		# validation
		if not isinstance(epic, dict):
			return None

		guid = epic.get('guid')
		title = epic.get('title')

		sql = "insert into epic(guid, title) values (?, ?) on conflict(guid) do update set title = ? returning id"
		data = (guid, title, title)
		row_id = self._execute(sql, data)

		return row_id


	def syncIssue(self, issue: dict) -> int:

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

		sql = "insert into issue (guid, title, type, points, status, opened_date, closed_date, is_closed, parent_issue_guid, epic_id, sprint_id) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) on conflict(guid) do update set title = ?, type = ?, points = ?, status = ?, opened_date = ?, closed_date = ?, is_closed = ?, parent_issue_guid = ?, epic_id = ?, sprint_id = ? returning id"
		data = (guid, title, t, points, status, opened_date, closed_date, is_closed, parent_guid, epic_id, sprint_id, title, t, points, status, opened_date, closed_date, is_closed, parent_guid, epic_id, sprint_id)
		row_id = self._execute(sql, data)

		return row_id


	def _execute(self, sql: str, data: tuple):

		cursor = self.dbh.cursor()
		last_row_id_tuple = cursor.execute(sql, data).fetchone()
		self.dbh.commit()
		cursor.close()

		return last_row_id_tuple[0]

