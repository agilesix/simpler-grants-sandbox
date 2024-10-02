import json
import sys
from delivery_metrics_config import DeliveryMetricsConfig
from delivery_metrics_database import DeliveryMetricsDatabase
from delivery_metrics_model import DeliveryMetricsModel
from typing import TextIO


class DeliveryMetricsDataLoader:

	def __init__(self, config: DeliveryMetricsConfig, file_path: str):
		self.config = config
		self.file_path = file_path
		self.data = None


	""" public methods """


	def loadData(self) -> None:
		# read file
		try:
			print("opening file '{}'".format(self.file_path))
			with open(self.file_path, 'r') as f:
				self._readFile(f)
				f.close()
		except IOError:
			print("Fatal error: unable to read file: {}".format(self.file_path))
			sys.exit()

		# parse data
		sprints, epics, issues = self._parseData()

		# write to database
		self._persist(sprints, epics, issues)


	def removePrefixFromGuid(self, guid: str) -> str:

		if isinstance(guid, str) and guid is not None:
			prefix = 'https://github.com/'
			if guid.startswith(prefix):
				return guid.replace(prefix, '')

		return guid


	""" private methods """


	def _readFile(self, file_handle: TextIO) -> None:
		try:
			self.data = json.load(file_handle)
		except json.JSONDecodeError:
			print("FATAL: unable to read json")
			sys.exit()

	
	def _parseData(self) -> (dict, dict, dict):
		
		unique_sprints = {}
		unique_epics = {}
		unique_issues = {}

		print("parsing json")
		for item in self.data:

			# validate
			if not isinstance(item, dict):
				continue 
			
			# parse and de-duplicate sprint 
			sprint = self._extractSprint(item)
			if sprint['guid'] is not None:
				guid = sprint['guid']
				unique_sprints[guid] = sprint

			# parse and de-duplicate epic 
			epic = self._extractEpic(item)
			if epic['guid'] is not None:
				guid = epic['guid']
				unique_epics[guid] = epic

			# parse and de-duplicate issue
			issue = self._extractIssue(item)
			issue['sprint_guid'] = sprint['guid']
			issue['epic_guid'] = epic['guid']
			if issue['guid'] is not None and issue['type'] in ['Task', 'Bug', 'Enhancement']:
				guid = issue['guid']
				unique_issues[guid] = issue

		return (unique_sprints, unique_epics, unique_issues)
	

	def _extractSprint(self, item: dict) -> dict:

		# validation
		if not isinstance(item, dict):
			return {}

		# extraction
		sprint = {
			'guid': item.get('sprint_id'),
			'name': item.get('sprint_name'), 
			'start_date': item.get('sprint_start'), 
			'end_date': item.get('sprint_end'),
			'duration': item.get('sprint_length')
		}

		return sprint


	def _extractEpic(self, item: dict) -> dict:

		# validation
		if not isinstance(item, dict):
			return {}

		# extraction
		epic = {
			'guid': self.removePrefixFromGuid(item.get('epic_url')),
			'title': item.get('epic_title') 
		}

		return epic


	def _extractIssue(self, item: dict) -> dict:

		# validation
		if not isinstance(item, dict):
			return {}

		# extraction
		issue = {
			'guid': self.removePrefixFromGuid(item.get('issue_url')),
			'title': item.get('issue_title'),
			'type': item.get('issue_type'), 
			'points': item.get('issue_points'),
			'status': item.get('issue_status'), 
			'opened_date': item.get('issue_opened_at'), 
			'closed_date': item.get('issue_closed_at'), 
			'is_closed': item.get('issue_is_closed'), 
			'parent_guid': self.removePrefixFromGuid(item.get('issue_parent')),
			'epic_guid': self.removePrefixFromGuid(item.get('epic_url')),
			'sprint_guid': item.get('sprint_id')
		}

		return issue


	def _persist(self, unique_sprints: dict, unique_epics: dict, unique_issues: dict) -> None:

		db = DeliveryMetricsDatabase(self.config)
		model = DeliveryMetricsModel(db)

		sprint_guid_to_rowid_map = {}
		epic_guid_to_rowid_map = {}

		# write each sprint to the db
		print("persisting sprint data")
		for guid, sprint in unique_sprints.items():
			sprint_id = model.syncSprint(sprint)
			if sprint_id is not None:
				sprint_guid_to_rowid_map[guid] = sprint_id
				print("sprint '{}' mapped to local db row id {}".format(guid, sprint_id))

		# write each epic to the db
		print("persisting epic data")
		for guid, epic in unique_epics.items():
			epic_id = model.syncEpic(epic)
			if epic_id is not None:
				epic_guid_to_rowid_map[guid] = epic_id
				print("epic '{}' mapped to local db row id {}".format(guid, epic_id))

		# write each issue to the db
		print("persisting issue data")
		for guid, issue in unique_issues.items():

			new_issue = dict(issue)

			# get epic id from epic guid
			epic_guid = issue.get('epic_guid')
			new_issue['epic_id'] = epic_guid_to_rowid_map.get(epic_guid)
			del new_issue['epic_guid']

			# get sprint id from sprint guid
			sprint_guid = issue.get('sprint_guid')
			new_issue['sprint_id'] = sprint_guid_to_rowid_map.get(sprint_guid)
			del new_issue['sprint_guid']

			issue_id = model.syncIssue(new_issue)
			if issue_id is not None:
				print("issue guid '{}' mapped to local db row id {}".format(new_issue.get('guid'), issue_id))

		# close db connection
		db.disconnect()

