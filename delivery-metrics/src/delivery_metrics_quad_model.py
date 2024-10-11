from delivery_metrics_model import DeliveryMetricsChangeType
from delivery_metrics_model import DeliveryMetricsModel

class DeliveryMetricsQuadModel(DeliveryMetricsModel):

	def syncQuad(self, quad: dict) -> (int, DeliveryMetricsChangeType):
	
		# validation
		if not isinstance(quad, dict):
			return None, DeliveryMetricsChangeType.NONE

		# initialize return value
		change_type = DeliveryMetricsChangeType.NONE 

		# attempt insert
		quad_id = self._insertDimensions(quad)
		if quad_id is not None:
			change_type = DeliveryMetricsChangeType.INSERT 
			
		# TODO: if insert failed, then select and update
		if quad_id is None:
			quad_id = None
			#change_type = DeliveryMetricsChangeType.UPDATE

		return quad_id, change_type


	def _insertDimensions(self, quad: dict) -> int:

		# get values needed for sql statement
		guid = quad.get('guid')
		name = quad.get('name')
		start = self.formatDate(quad.get('start_date'))
		end = self.formatDate(quad.get('end_date'))
		duration = quad.get('duration')

		# insert into dimension table: quad
		sql = "insert into quad(guid, name, start_date, end_date, duration) values (?, ?, ?, ?, ?) on conflict(guid) do nothing returning id"
		data = (guid, name, start, end, duration)
		quad_id = self.insertWithoutCursor(sql, data)

		return quad_id



		'''
		# TODO: select and update
		sql = "insert into quad(guid, name, start_date, end_date, duration) values (?, ?, ?, ?, ?) on conflict(guid) do update set (name, start_date, end_date, duration, t_modified) = (?, ?, ?, ?, current_timestamp) returning id"
		data = (guid, name, start, end, duration, name, start, end, duration)
		row_id = self.execute(sql, data)
		'''
