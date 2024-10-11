from delivery_metrics_model import DeliveryMetricsChangeType
from delivery_metrics_model import DeliveryMetricsModel

class DeliveryMetricsIssueModel(DeliveryMetricsModel):

	def syncIssue(self, issue: dict) -> (int, DeliveryMetricsChangeType):

		# validation
		if not isinstance(issue, dict):
			return None, DeliveryMetricsChangeType.NONE

		# initialize return value
		change_type = DeliveryMetricsChangeType.NONE

		# get cursor to keep open across transactions
		cursor = self.cursor()

		# attempt insert into dimension table
		issue_id = self._insertDimensions(cursor, issue)
		if issue_id is not None:
			change_type = DeliveryMetricsChangeType.INSERT

		# TODO: if insert failed, select and update
		if issue_id is None:
			issue_id = None
			#change_type = DeliveryMetricsChangeType.UPDATE

		# insert into fact table
		if issue_id is not None:
			history_id, map_id = self._insertFacts(cursor, issue_id, issue)

		# close cursor
		cursor.close()
		
		return issue_id, change_type


	def _insertDimensions(self, cursor, issue: dict) -> int:

		# get values needed for sql statement
		guid = issue.get('guid')
		title = issue.get('title')
		t = issue.get('type')
		opened_date = self.formatDate(issue.get('opened_date'))
		closed_date = self.formatDate(issue.get('closed_date'))
		parent_guid = issue.get('parent_guid')
		epic_id = issue.get('epic_id')

		# insert into dimension table: issue
		sql_dim = "insert into issue (guid, title, type, opened_date, closed_date, parent_issue_guid, epic_id) values (?, ?, ?, ?, ?, ?, ?) on conflict(guid) do nothing returning id"
		data_dim = (guid, title, t, opened_date, closed_date, parent_guid, epic_id)
		issue_id = self.insertWithCursor(cursor, sql_dim, data_dim)

		return issue_id


	def _insertFacts(self, cursor, issue_id: int, issue: dict) -> (int, int):

		# get values needed for sql statement
		status = issue.get('status')
		is_closed = issue.get('is_closed')
		points = issue.get('points') or 0
		sprint_id = issue.get('sprint_id')
		effective = self.getEffectiveDate()

		# insert into fact table: issue_history
		sql_fact1 = "insert into issue_history (issue_id, status, is_closed, points, d_effective) values (?, ?, ?, ?, ?) on conflict (issue_id, d_effective) do update set (status, is_closed, points, t_modified) = (?, ?, ?, current_timestamp) returning id" 
		data_fact1 = (issue_id, status, is_closed, points, effective, status, is_closed, points) 
		history_id = self.insertWithCursor(cursor, sql_fact1, data_fact1)

		# insert into fact table: issue_sprint_map
		sql_fact2 = "insert into issue_sprint_map (issue_id, sprint_id, d_effective) values (?, ?, ?) on conflict (issue_id, d_effective) do update set (sprint_id, t_modified) = (?, current_timestamp) returning id"
		data_fact2 = (issue_id, sprint_id, effective, sprint_id) 
		map_id = self.insertWithCursor(cursor, sql_fact2, data_fact2)

		return history_id, map_id



		'''
		# TO DO: select and update
		sql_dim = "insert into issue (guid, title, type, opened_date, closed_date, parent_issue_guid, epic_id) values (?, ?, ?, ?, ?, ?, ?) on conflict(guid) do update set (title, type, opened_date, closed_date, parent_issue_guid, epic_id, t_modified) = (?, ?, ?, ?, ?, ?, current_timestamp) returning id"
		'''

