from delivery_metrics_model import DeliveryMetricsChangeType
from delivery_metrics_model import DeliveryMetricsModel

class DeliveryMetricsEpicModel(DeliveryMetricsModel):

	def syncEpic(self, epic: dict) -> (int, DeliveryMetricsChangeType):

		# validation
		if not isinstance(epic, dict):
			return None, DeliveryMetricsChangeType.NONE

		# initialize return value
		change_type = DeliveryMetricsChangeType.NONE

		# get cursor to keep open across transactions
		cursor = self.cursor()

		# attempt insert into dimension table
		epic_id = self._insertDimensions(cursor, epic)
		if epic_id is not None:
			change_type = DeliveryMetricsChangeType.INSERT

		# TODO: if insert failed, select and update
		if epic_id is None:
			epic_id = None
			#change_type = DeliveryMetricsChangeType.UPDATE

		# insert into fact table
		if epic_id is not None:
			fact_id = self._insertFacts(cursor, epic_id, epic)

		# close cursor
		cursor.close()

		return epic_id, change_type


	def _insertDimensions(self, cursor, epic: dict) -> int:

		# get values needed for sql statement
		guid = epic.get('guid')
		title = epic.get('title')
		deliverable_id = epic.get('deliverable_id')
		effective = self.getEffectiveDate()

		# insert into dimension table: epic
		sql_dim = "insert into epic(guid, title) values (?, ?) on conflict(guid) do nothing returning id"
		data_dim = (guid, title)
		epic_id = self.insertWithCursor(cursor, sql_dim, data_dim)

		return epic_id
	

	def _insertFacts(self, cursor, epic_id: int, epic: dict) -> int:

		# get values needed for sql statement
		deliverable_id = epic.get('deliverable_id')
		effective = self.getEffectiveDate()

		# insert into fact table: epic_deliverable_map
		sql_fact = "insert into epic_deliverable_map(epic_id, deliverable_id, d_effective) values (?, ?, ?) on conflict(epic_id, d_effective) do update set (deliverable_id, t_modified) = (?, current_timestamp) returning id"
		data_fact = (epic_id, deliverable_id, effective, deliverable_id)
		fact_id = self.insertWithCursor(cursor, sql_fact, data_fact)

		return fact_id 






		'''
		# TO DO: select and update
		sql_dim = "insert into epic(guid, title) values (?, ?) on conflict(guid) do update set (title, t_modified) = (?, current_timestamp) returning id"
		'''

