from delivery_metrics_model import DeliveryMetricsModel

class DeliveryMetricsEpicModel(DeliveryMetricsModel):

	def __init__(self, dbh):
		self.dbh = dbh


	def syncEpic(self, epic: dict) -> int:

		# validation
		if not isinstance(epic, dict):
			return None

		guid = epic.get('guid')
		title = epic.get('title')

		sql = "insert into epic(guid, title) values (?, ?) on conflict(guid) do update set (title, t_modified) = (?, current_timestamp) returning id"
		data = (guid, title, title)
		row_id = self._execute(sql, data)

		return row_id


