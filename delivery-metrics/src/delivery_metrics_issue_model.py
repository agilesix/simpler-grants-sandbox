from delivery_metrics_model import DeliveryMetricsModel

class DeliveryMetricsIssueModel(DeliveryMetricsModel):

	def syncIssue(self, issue: dict) -> int:

		# validation
		if not isinstance(issue, dict):
			return None

		# get values needed for sql statement
		guid = issue.get('guid')
		title = issue.get('title')
		t = issue.get('type')
		points = issue.get('points') or 0
		opened_date = self.formatDate(issue.get('opened_date'))
		closed_date = self.formatDate(issue.get('closed_date'))
		parent_guid = issue.get('parent_guid')
		epic_id = issue.get('epic_id')
		sprint_id = issue.get('sprint_id')
		status = issue.get('status')
		is_closed = issue.get('is_closed')
		effective = self.getEffectiveDate()

		# get cursor to keep open across transactions
		cursor = self.cursor()

		# insert into dimension table: issue
		sql_dim = "insert into issue (guid, title, type, points, opened_date, closed_date, parent_issue_guid, epic_id) values (?, ?, ?, ?, ?, ?, ?, ?) on conflict(guid) do update set (title, type, points, opened_date, closed_date, parent_issue_guid, epic_id, t_modified) = (?, ?, ?, ?, ?, ?, ?, current_timestamp) returning id"
		data_dim = (guid, title, t, points, opened_date, closed_date, parent_guid, epic_id, title, t, points, opened_date, closed_date, parent_guid, epic_id)
		issue_id = self.executeWithCursor(cursor, sql_dim, data_dim)

		# insert into fact table: issue_history
		# TODO: do not insert if most recent fact record has same values other than effective date
		sql_fact1 = "insert into issue_history (issue_id, status, is_closed, d_effective) values (?, ?, ?, ?) on conflict (issue_id, d_effective) do update set (status, is_closed, t_modified) = (?, ?, current_timestamp) returning id" 
		data_fact1 = (issue_id, status, is_closed, effective, status, is_closed) 
		history_id = self.executeWithCursor(cursor, sql_fact1, data_fact1)

		# insert into fact table: issue_sprint_map
		# TODO: do not insert if most recent fact record has same values other than effective date
		if sprint_id is not None:
			sql_fact2 = "insert into issue_sprint_map (issue_id, sprint_id, d_effective) values (?, ?, ?) on conflict (issue_id, d_effective) do update set (sprint_id, t_modified) = (?, current_timestamp) returning id"
			data_fact2 = (issue_id, sprint_id, effective, sprint_id) 
			map_id = self.executeWithCursor(cursor, sql_fact2, data_fact2)

		# close cursor
		cursor.close()
		
		return issue_id


