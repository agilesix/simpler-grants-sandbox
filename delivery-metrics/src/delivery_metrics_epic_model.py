from delivery_metrics_model import DeliveryMetricsChangeType
from delivery_metrics_model import DeliveryMetricsModel

class DeliveryMetricsEpicModel(DeliveryMetricsModel):

	def syncEpic(self, epic: dict) -> int:

		# validation
		if not isinstance(epic, dict):
			return None

		# initialize return value
		change_type = DeliveryMetricsChangeType.NONE

		# get values needed for sql statement
		guid = epic.get('guid')
		title = epic.get('title')
		deliverable_id = epic.get('deliverable_id')
		effective = self.getEffectiveDate()

		# get cursor to keep open across transactions
		cursor = self.cursor()

		# insert into dimension table: epic
		sql_dim = "insert into epic(guid, title) values (?, ?) on conflict(guid) do nothing returning id"
		data_dim = (guid, title)
		epic_id = self.insertWithCursor(cursor, sql_dim, data_dim)

		# update return value
		if epic_id is not None:
			change_type = DeliveryMetricsChangeType.INSERT

		# TODO: select and update
		if epic_id is None:
			epic_id = None
			#change_type = DeliveryMetricsChangeType.UPDATE

		# insert into fact table: epic_deliverable_map
		if epic_id is not None:
			sql_fact = "insert into epic_deliverable_map(epic_id, deliverable_id, d_effective) values (?, ?, ?) on conflict(epic_id, d_effective) do update set (deliverable_id, t_modified) = (?, current_timestamp) returning id"
			data_fact = (epic_id, deliverable_id, effective, deliverable_id)
			map_id = self.insertWithCursor(cursor, sql_fact, data_fact)

		# close cursor
		cursor.close()

		return epic_id, change_type


		'''
		# TO DO: select and update
		sql_dim = "insert into epic(guid, title) values (?, ?) on conflict(guid) do update set (title, t_modified) = (?, current_timestamp) returning id"
		'''

