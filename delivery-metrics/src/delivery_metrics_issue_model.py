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
		status = issue.get('status')
		is_closed = issue.get('is_closed')
		sprint = issue.get('sprint')
		effective = self.getEffectiveDate()

		# insert into history dimension table
		sql_dim = "insert into issue (guid, title, type, points, opened_date, closed_date, parent_issue_guid, epic_id) values (?, ?, ?, ?, ?, ?, ?, ?) on conflict(guid) do update set (title, type, points, opened_date, closed_date, parent_issue_guid, epic_id, t_modified) = (?, ?, ?, ?, ?, ?, ?, current_timestamp) returning id"
		data_dim = (guid, title, t, points, opened_date, closed_date, parent_guid, epic_id, title, t, points, opened_date, closed_date, parent_guid, epic_id)

		# execute sql but keep cursor open
		cursor = self.cursor()
		issue_id = self.executeWithCursor(cursor, sql_dim, data_dim)

		# insert into history fact table
		sql_fact = "insert into issue_history (issue_id, status, is_closed, effective) values (?, ?, ?, ?) on conflict (issue_id, effective) do update set (status, is_closed, t_modified) = (?, ?, current_timestamp) returning id" 
		data_fact = (issue_id, status, is_closed, effective, status, is_closed) 

		# execute sql and close cursor 
		history_id = self.executeWithCursor(cursor, sql_fact, data_fact)
		cursor.close()
		
		return issue_id


