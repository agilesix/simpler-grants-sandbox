from delivery_metrics_model import DeliveryMetricsModel

class DeliveryMetricsSprintModel(DeliveryMetricsModel):

	def __init__(self, dbh):
		self.dbh = dbh


	def syncSprint(self, sprint: dict) -> int:

		# validation
		if not isinstance(sprint, dict):
			return None

		guid = sprint.get('guid')
		name = sprint.get('name')
		start = self.formatDate(sprint.get('start_date'))
		end = self.formatDate(sprint.get('end_date'))
		duration = sprint.get('duration')

		sql = "insert into sprint(guid, name, start_date, end_date, duration) values (?, ?, ?, ?, ?) on conflict(guid) do update set (name, start_date, end_date, duration, t_modified) = (?, ?, ?, ?, current_timestamp) returning id"
		data = (guid, name, start, end, duration, name, start, end, duration)
		row_id = self._execute(sql, data)

		return row_id

