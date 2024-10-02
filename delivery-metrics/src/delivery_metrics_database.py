import sqlite3
import sys
from delivery_metrics_config import DeliveryMetricsConfig

class DeliveryMetricsDatabase:

	def __init__(self, config: DeliveryMetricsConfig):

		self.config = config
		self._dbConnection = None


	def connection(self) -> sqlite3.Connection:

		if not self._dbConnection:
			try:
				print("connecting to database '{}'".format(self.config.DB_PATH))
				self._dbConnection = sqlite3.connect(self.config.DB_PATH)
			except sqlite3.Error as error:
				print("WARNING: {}: {}".format(error, self.config.DB_PATH))

		return self._dbConnection
	

	def cursor(self) -> sqlite3.Cursor:

		db_cursor = None
		try:
			db_cursor = self.connection().cursor()
		except:
			print("FATAL: cannot get database cursor")
			sys.exit()

		return db_cursor


	def closeConnection(self) -> None:
	
		if self._dbConnection is not None:
			print("closing db connection")
			try:
				self._dbConnection.close()
			except:
				pass

	
	def __del__(self):

		if self._dbConnection:
			self._dbConnection.close()



