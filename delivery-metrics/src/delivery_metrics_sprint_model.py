from delivery_metrics_model import DeliveryMetricsChangeType
from delivery_metrics_model import DeliveryMetricsModel

class DeliveryMetricsSprintModel(DeliveryMetricsModel):

	def syncSprint(self, sprint: dict) -> int:

		# validation
		if not isinstance(sprint, dict):
			return None

		# initialize return value
		change_type = DeliveryMetricsChangeType.NONE

		# get values needed for sql statement
		guid = sprint.get('guid')
		name = sprint.get('name')
		start = self.formatDate(sprint.get('start_date'))
		end = self.formatDate(sprint.get('end_date'))
		duration = sprint.get('duration')
		quad_id = sprint.get('quad_id')

		# insert into dimension table: sprint
		sql = "insert into sprint(guid, name, start_date, end_date, duration, quad_id) values (?, ?, ?, ?, ?, ?) on conflict(guid) do nothing returning id"
		data = (guid, name, start, end, duration, quad_id)
		sprint_id = self.insertWithoutCursor(sql, data)

		# update return value
		if sprint_id is not None:
			change_type = DeliveryMetricsChangeType.INSERT

		# TODO: select and update
		if sprint_id is None:
			sprint_id = None
			#change_type = DeliveryMetricsChangeType.UPDATE

		return sprint_id, change_type


		'''
		# TO DO: select and update
		sql = "insert into sprint(guid, name, start_date, end_date, duration, quad_id) values (?, ?, ?, ?, ?, ?) on conflict(guid) do update set (name, start_date, end_date, duration, quad_id, t_modified) = (?, ?, ?, ?, ?, current_timestamp) returning id"
		'''

