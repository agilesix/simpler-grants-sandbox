class DeliveryMetricsConfig:

	def __init__(self):

		# path to sqlite db instance
		self.DB_PATH = "../db/delivery_metrics.db"

		# TODO: hard coded now; this will be set from command line arg
		self.EFFECTIVE_DATE = "2024-10-04"

