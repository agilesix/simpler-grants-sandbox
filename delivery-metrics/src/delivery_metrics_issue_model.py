from delivery_metrics_model import DeliveryMetricsModel

class DeliveryMetricsIssueModel(DeliveryMetricsModel):

	def __init__(self, dbh):
		self.dbh = dbh


	def syncIssue(self, issue: dict) -> int:

		# validation
		if not isinstance(issue, dict):
			return None

		guid = issue.get('guid')
		title = issue.get('title')
		t = issue.get('type')
		points = issue.get('points') or 0
		status = issue.get('status')
		opened_date = self.formatDate(issue.get('opened_date'))
		closed_date = self.formatDate(issue.get('closed_date'))
		is_closed = issue.get('is_closed')
		parent_guid = issue.get('parent_guid')
		epic_id = issue.get('epic_id')
		sprint_id = issue.get('sprint_id')

		sql = "insert into issue (guid, title, type, points, status, opened_date, closed_date, is_closed, parent_issue_guid, epic_id, sprint_id) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) on conflict(guid) do update set (title, type, points, status, opened_date, closed_date, is_closed, parent_issue_guid, epic_id, sprint_id, t_modified) = (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, current_timestamp) returning id"
		data = (guid, title, t, points, status, opened_date, closed_date, is_closed, parent_guid, epic_id, sprint_id, title, t, points, status, opened_date, closed_date, is_closed, parent_guid, epic_id, sprint_id)
		row_id = self._execute(sql, data)

		return row_id


