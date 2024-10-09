from delivery_metrics_model import DeliveryMetricsModel

class DeliveryMetricsEpicModel(DeliveryMetricsModel):

	def syncEpic(self, epic: dict) -> int:

		# validation
		if not isinstance(epic, dict):
			return None

		# get values needed for sql statement
		guid = epic.get('guid')
		title = epic.get('title')
		deliverable_id = epic.get('deliverable_id')
		effective = self.getEffectiveDate()

		# get cursor to keep open across transactions
		cursor = self.cursor()

		# insert into dimension table: epic
		sql_dim = "insert into epic(guid, title) values (?, ?) on conflict(guid) do update set (title, t_modified) = (?, current_timestamp) returning id"
		data_dim = (guid, title, title)
		epic_id = self.executeWithCursor(cursor, sql_dim, data_dim)

		# insert into fact table: epic_deliverable_map
		sql_fact = "insert into epic_deliverable_map(epic_id, deliverable_id, d_effective) values (?, ?, ?) on conflict(epic_id, d_effective) do update set (deliverable_id, t_modified) = (?, current_timestamp) returning id"
		data_fact = (epic_id, deliverable_id, effective, deliverable_id)
		map_id = self.executeWithCursor(cursor, sql_fact, data_fact)

		# close cursor
		cursor.close()

		return map_id

