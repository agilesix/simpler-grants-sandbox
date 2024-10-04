from delivery_metrics_model import DeliveryMetricsModel

class DeliveryMetricsDeliverableModel(DeliveryMetricsModel):

	def syncDeliverable(self, deliverable: dict) -> int:
		
		# validation
		if not isinstance(deliverable, dict):
			return None

		guid = deliverable.get('guid')
		title = deliverable.get('title')
		pillar = deliverable.get('pillar')
		quad_id = deliverable.get('quad_id')

		sql = "insert into deliverable(guid, title, pillar, quad_id) values (?, ?, ?, ?) on conflict(guid) do update set (title, pillar, quad_id, t_modified) = (?, ?, ?, current_timestamp) returning id"
		data = (guid, title, pillar, quad_id, title, pillar, quad_id)
		row_id = self.execute(sql, data)

		return row_id


