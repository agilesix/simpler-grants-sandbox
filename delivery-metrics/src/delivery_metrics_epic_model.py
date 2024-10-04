from delivery_metrics_model import DeliveryMetricsModel

class DeliveryMetricsEpicModel(DeliveryMetricsModel):

	def syncEpic(self, epic: dict) -> int:

		# validation
		if not isinstance(epic, dict):
			return None

		guid = epic.get('guid')
		title = epic.get('title')
		deliverable_id = epic.get('deliverable_id')

		sql = "insert into epic(guid, title, deliverable_id) values (?, ?, ?) on conflict(guid) do update set (title, deliverable_id, t_modified) = (?, ?, current_timestamp) returning id"
		data = (guid, title, deliverable_id, title, deliverable_id)
		row_id = self.execute(sql, data)

		return row_id


