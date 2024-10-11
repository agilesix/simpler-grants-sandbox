from delivery_metrics_model import DeliveryMetricsChangeType
from delivery_metrics_model import DeliveryMetricsModel

class DeliveryMetricsDeliverableModel(DeliveryMetricsModel):

	def syncDeliverable(self, deliverable: dict) -> (int, DeliveryMetricsChangeType):
		
		# validation
		if not isinstance(deliverable, dict):
			return None, DeliveryMetricsChangeType.NONE

		# initialize return value
		change_type = DeliveryMetricsChangeType.NONE

		# get cursor to keep open across transactions
		cursor = self.cursor()

		# attempt insert into dimension table
		deliverable_id = self._insertDimensions(cursor, deliverable)
		if deliverable_id is not None:
			change_type = DeliveryMetricsChangeType.INSERT

		# TODO: if insert failed, select and update
		if deliverable_id is None:
			deliverable_id = None
			#change_type = DeliveryMetricsChangeType.UPDATE

		# insert into fact table
		if deliverable_id is not None:
			map_id = self._insertFacts(cursor, deliverable_id, deliverable)

		# close cursor
		cursor.close()

		return deliverable_id, change_type


	def _insertDimensions(self, cursor, deliverable: dict) -> int:

		# get values needed for sql statement
		guid = deliverable.get('guid')
		title = deliverable.get('title')
		pillar = deliverable.get('pillar')

		# insert into dimension table: deliverable
		sql_dim = "insert into deliverable(guid, title, pillar) values (?, ?, ?) on conflict(guid) do nothing returning id"
		data_dim = (guid, title, pillar)
		deliverable_id = self.insertWithCursor(cursor, sql_dim, data_dim)

		return deliverable_id


	def _insertFacts(self, cursor, deliverable_id: int, deliverable: dict) -> int:

		# get values needed for sql statement
		quad_id = deliverable.get('quad_id')
		effective = self.getEffectiveDate()

		# insert into fact table: deliverable_quad_map
		sql_fact = "insert into deliverable_quad_map(deliverable_id, quad_id, d_effective) values (?, ?, ?) on conflict(deliverable_id, d_effective) do update set (quad_id, t_modified) = (?, current_timestamp) returning id"
		data_fact = (deliverable_id, quad_id, effective, quad_id)
		map_id = self.insertWithCursor(cursor, sql_fact, data_fact)

		return map_id


		'''
		# TO DO: select and update
		sql_dim = "insert into deliverable(guid, title, pillar) values (?, ?, ?) on conflict(guid) do update set (title, pillar, t_modified) = (?, ?, current_timestamp) returning id"
		'''

