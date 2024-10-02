#!/usr/bin/env python3

from argparse import ArgumentParser, FileType
from delivery_metrics_config import DeliveryMetricsConfig
from delivery_metrics_loader import DeliveryMetricsDataLoader

if __name__ == "__main__":

	# define command line args
	parser = ArgumentParser(description="Load a json file into the delivery metrics database")
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("file", type=FileType("r"), nargs="?", metavar="FILEPATH", help="path of json file to load")

	# get command line args
	args = parser.parse_args()
	args.file.close()

	# initialize config object
	config = DeliveryMetricsConfig()

	# load data
	print("running data loader...")
	loader = DeliveryMetricsDataLoader(config, args.file.name)
	loader.loadData()
	print("data loader is done")

