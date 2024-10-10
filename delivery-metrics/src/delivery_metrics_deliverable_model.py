from delivery_metrics_model import DeliveryMetricsChangeType
from delivery_metrics_model import DeliveryMetricsModel

class DeliveryMetricsDeliverableModel(DeliveryMetricsModel):

	def syncDeliverable(self, deliverable: dict) -> int:
		
		# validation
		if not isinstance(deliverable, dict):
			return None

		# initialize return value
		change_type = DeliveryMetricsChangeType.NONE

		# get values needed for sql statement
		guid = deliverable.get('guid')
		title = deliverable.get('title')
		pillar = deliverable.get('pillar')
		quad_id = deliverable.get('quad_id')
		effective = self.getEffectiveDate()

		# get cursor to keep open across transactions
		cursor = self.cursor()

		# insert into dimension table: deliverable
		sql_dim = "insert into deliverable(guid, title, pillar) values (?, ?, ?) on conflict(guid) do nothing returning id"
		data_dim = (guid, title, pillar)
		deliverable_id = self.insertWithCursor(cursor, sql_dim, data_dim)

		# update return value
		if deliverable_id is not None:
			change_type = DeliveryMetricsChangeType.INSERT

		# TODO: select and update
		if deliverable_id is None:
			deliverable_id = None
			#change_type = DeliveryMetricsChangeType.UPDATE

		# insert into fact table: deliverable_quad_map
		if deliverable_id is not None:
			sql_fact = "insert into deliverable_quad_map(deliverable_id, quad_id, d_effective) values (?, ?, ?) on conflict(deliverable_id, d_effective) do update set (quad_id, t_modified) = (?, current_timestamp) returning id"
			data_fact = (deliverable_id, quad_id, effective, quad_id)
			map_id = self.insertWithCursor(cursor, sql_fact, data_fact)

		# close cursor
		cursor.close()

		return deliverable_id, change_type



		'''
		# TO DO: select and update
		sql_dim = "insert into deliverable(guid, title, pillar) values (?, ?, ?) on conflict(guid) do update set (title, pillar, t_modified) = (?, ?, current_timestamp) returning id"
		'''

