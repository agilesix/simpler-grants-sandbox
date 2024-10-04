from delivery_metrics_model import DeliveryMetricsModel

class DeliveryMetricsSprintModel(DeliveryMetricsModel):

	def syncSprint(self, sprint: dict) -> int:

		# validation
		if not isinstance(sprint, dict):
			return None

		guid = sprint.get('guid')
		name = sprint.get('name')
		start = self.formatDate(sprint.get('start_date'))
		end = self.formatDate(sprint.get('end_date'))
		duration = sprint.get('duration')
		quad_id = sprint.get('quad_id')

		sql = "insert into sprint(guid, name, start_date, end_date, duration, quad_id) values (?, ?, ?, ?, ?, ?) on conflict(guid) do update set (name, start_date, end_date, duration, quad_id, t_modified) = (?, ?, ?, ?, ?, current_timestamp) returning id"
		data = (guid, name, start, end, duration, quad_id, name, start, end, duration, quad_id)
		row_id = self.execute(sql, data)

		return row_id

