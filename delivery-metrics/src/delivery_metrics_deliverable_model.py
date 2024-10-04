from delivery_metrics_model import DeliveryMetricsModel

class DeliveryMetricsDeliverableModel(DeliveryMetricsModel):

	def __init__(self, dbh):
		self.dbh = dbh


	def syncDeliverable(self, deliverable: dict) -> int:
		
		# validation
		if not isinstance(deliverable, dict):
			return None

		guid = deliverable.get('guid')
		title = deliverable.get('title')
		pillar = deliverable.get('pillar')

		sql = "insert into deliverable(guid, title, pillar) values (?, ?, ?) on conflict(guid) do update set (title, pillar, t_modified) = (?, ?, current_timestamp) returning id"
		data = (guid, title, pillar, title, pillar)
		row_id = self._execute(sql, data)

		return row_id


