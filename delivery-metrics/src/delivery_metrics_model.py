
class DeliveryMetricsModel:

	def __init__(self, dbh):
		self._dbh = dbh


	def formatDate(self, date: str) -> str:

		if date is None:
			return None

		if len(date) > 10:
			date = date[:10]

		return date

	
	def cursor(self):
		
		return self._dbh.cursor()


	def execute(self, sql: str, data: tuple) -> int:

		cursor = self._dbh.cursor()
		last_row_id_tuple = cursor.execute(sql, data).fetchone()
		self._dbh.commit()
		cursor.close()

		return last_row_id_tuple[0]


	def executeWithCursor(self, cursor, sql: str, data: tuple) -> int:

		last_row_id_tuple = cursor.execute(sql, data).fetchone()
		self._dbh.commit()

		return last_row_id_tuple[0]
		

	def getEffectiveDate(self) -> str:

		return self._dbh.getEffectiveDate()
