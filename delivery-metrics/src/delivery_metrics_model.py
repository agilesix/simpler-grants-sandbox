
class DeliveryMetricsModel:

	def __init__(self, dbh):
		self.dbh = dbh


	def formatDate(self, date: str) -> str:

		if date is None:
			return None

		if len(date) > 10:
			date = date[:10]

		return date


	def _execute(self, sql: str, data: tuple) -> int:

		cursor = self.dbh.cursor()
		last_row_id_tuple = cursor.execute(sql, data).fetchone()
		self.dbh.commit()
		cursor.close()

		return last_row_id_tuple[0]

