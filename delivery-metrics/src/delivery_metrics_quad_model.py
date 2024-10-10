from delivery_metrics_model import DeliveryMetricsModel

class DeliveryMetricsQuadModel(DeliveryMetricsModel):

	def syncQuad(self, quad: dict) -> int:
	
		# validation
		if not isinstance(quad, dict):
			return None

		guid = quad.get('guid')
		name = quad.get('name')
		start = self.formatDate(quad.get('start_date'))
		end = self.formatDate(quad.get('end_date'))
		duration = quad.get('duration')

		sql = "insert into quad(guid, name, start_date, end_date, duration) values (?, ?, ?, ?, ?) on conflict(guid) do update set (name, start_date, end_date, duration, t_modified) = (?, ?, ?, ?, current_timestamp) returning id"
		data = (guid, name, start, end, duration, name, start, end, duration)
		row_id = self.execute(sql, data)

		return row_id


