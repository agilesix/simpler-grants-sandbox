import json
import sys
from delivery_metrics_config import DeliveryMetricsConfig
from delivery_metrics_database import DeliveryMetricsDatabase
from delivery_metrics_deliverable_model import DeliveryMetricsDeliverableModel
from delivery_metrics_epic_model import DeliveryMetricsEpicModel
from delivery_metrics_issue_model import DeliveryMetricsIssueModel
from delivery_metrics_sprint_model import DeliveryMetricsSprintModel
from delivery_metrics_quad_model import DeliveryMetricsQuadModel
from typing import TextIO


class DeliveryMetricsDataLoader:

	def __init__(self, config: DeliveryMetricsConfig, file_path: str):
		self.config = config
		self.file_path = file_path
		self.data = None
		self.unique_quads = {}
		self.unique_deliverables = {}
		self.unique_sprints = {}
		self.unique_epics = {}
		self.unique_issues = {}


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
		self._parseData()

		# write to database
		self._persistData()


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
		
		self.unique_quads = {}
		self.unique_deliverables = {}
		self.unique_sprints = {}
		self.unique_epics = {}
		self.unique_issues = {}

		print("parsing json")
		for item in self.data:

			# validate
			if not isinstance(item, dict):
				continue 
			
			# parse and de-duplicate quads, deliverables, sprints, epics
			quad_guid = self._extractQuad(item)
			deliverable_guid = self._extractDeliverable(item)
			sprint_guid = self._extractSprint(item)
			epic_guid = self._extractEpic(item)

			# parse and de-duplicate issues
			issue_guid = self._extractIssue(item)
			if issue_guid in self.unique_issues:
				self.unique_issues[issue_guid]['quad_guid'] = quad_guid
				self.unique_issues[issue_guid]['deliverable_guid'] = deliverable_guid
				self.unique_issues[issue_guid]['sprint_guid'] = sprint_guid
				self.unique_issues[issue_guid]['epic_guid'] = epic_guid

		self.data = None


	def _extractQuad(self, item: dict) -> str:

		# validation
		if not isinstance(item, dict):
			return None

		# extraction
		quad_guid = item.get('quad_id')
		quad = {
			'guid': quad_guid,
			'name': item.get('quad_name'),
			'start_date': item.get('quad_start'),
			'end_date': item.get('quad_end'),
			'duration': item.get('quad_length')
		}

		# save to unique map
		if quad_guid is not None:
			self.unique_quads[quad_guid] = quad

		return quad_guid


	def _extractDeliverable(self, item: dict) -> str:

		# validation
		if not isinstance(item, dict):
			return None

		# extraction
		deliverable_guid = self.removePrefixFromGuid(item.get('deliverable_url'))
		deliverable = {
			'guid': deliverable_guid,
			'title': item.get('deliverable_title'),
			'pillar': item.get('deliverable_pillar') 
		}

		# save to unique map
		if deliverable_guid is not None:
			self.unique_deliverables[deliverable_guid] = deliverable

		return deliverable_guid
	

	def _extractSprint(self, item: dict) -> str:

		# validation
		if not isinstance(item, dict):
			return None

		# extraction
		sprint_guid = item.get('sprint_id')
		sprint = {
			'guid': sprint_guid,
			'name': item.get('sprint_name'), 
			'start_date': item.get('sprint_start'), 
			'end_date': item.get('sprint_end'),
			'duration': item.get('sprint_length')
		}

		# save to unique map
		if sprint_guid is not None:
			self.unique_sprints[sprint_guid] = sprint

		return sprint_guid


	def _extractEpic(self, item: dict) -> str:

		# validation
		if not isinstance(item, dict):
			return None

		# extraction
		epic_guid = self.removePrefixFromGuid(item.get('epic_url'))
		epic = {
			'guid': epic_guid,
			'title': item.get('epic_title') 
		}

		# save to unique map
		if epic_guid is not None:
			self.unique_epics[epic_guid] = epic

		return epic_guid


	def _extractIssue(self, item: dict) -> str:

		# validation
		if not isinstance(item, dict):
			return None

		# extraction
		issue_guid = self.removePrefixFromGuid(item.get('issue_url'))
		issue_type = item.get('issue_type') or 'Undefined'
		issue = {
			'guid': issue_guid,
			'type': issue_type,
			'title': item.get('issue_title'),
			'points': item.get('issue_points'),
			'status': item.get('issue_status'), 
			'opened_date': item.get('issue_opened_at'), 
			'closed_date': item.get('issue_closed_at'), 
			'is_closed': item.get('issue_is_closed'), 
			'parent_guid': self.removePrefixFromGuid(item.get('issue_parent')),
			'quad_guid': None,
			'deliverable_guid': None,
			'sprint_guid': None,
			'epic_guid': None
		}

		# save to unique map
		if issue_guid is not None:
			if issue_type in ['Task', 'Bug', 'Enhancement', 'Undefined']:
				self.unique_issues[issue_guid] = issue

		return issue_guid


	def _persistData(self):

		db = DeliveryMetricsDatabase(self.config)
		deliverableModel = DeliveryMetricsDeliverableModel(db)
		epicModel = DeliveryMetricsEpicModel(db)
		issueModel = DeliveryMetricsIssueModel(db)
		sprintModel = DeliveryMetricsSprintModel(db)
		quadModel = DeliveryMetricsQuadModel(db)

		quad_guid_map = {}
		deliverable_guid_map = {}
		sprint_guid_map = {}
		epic_guid_map = {}

		update_count = {
			'quads': 0,
			'deliverables': 0,
			'sprints': 0,
			'epics': 0,
			'issues': 0
		}

		print("persisting data")

		# write each quad to the db
		for guid, quad in self.unique_quads.items():
			quad_id = quadModel.syncQuad(quad)
			if quad_id is not None:
				quad_guid_map[guid] = quad_id
				update_count['quads'] += 1
				#print("quad '{}' mapped to local db row id {}".format(guid, quad_id))

		print("{} quad row(s) updated".format(update_count['quads']))

		# write each deliverable to the db
		for guid, deliverable in self.unique_deliverables.items():
			new_deliverable = deliverable
			deliverable_id = deliverableModel.syncDeliverable(deliverable)
			if deliverable_id is not None:
				deliverable_guid_map[guid] = deliverable_id
				update_count['deliverables'] += 1
				#print("deliverable '{}' mapped to local db row id {}".format(guid, deliverable_id))

		print("{} deliverable row(s) updated".format(update_count['deliverables']))

		# write each sprint to the db
		for guid, sprint in self.unique_sprints.items():
			sprint_id = sprintModel.syncSprint(sprint)
			if sprint_id is not None:
				sprint_guid_map[guid] = sprint_id
				update_count['sprints'] += 1
				#print("sprint '{}' mapped to local db row id {}".format(guid, sprint_id))

		print("{} sprint row(s) updated".format(update_count['sprints']))

		# write each epic to the db
		for guid, epic in self.unique_epics.items():
			epic_id = epicModel.syncEpic(epic)
			if epic_id is not None:
				epic_guid_map[guid] = epic_id
				update_count['epics'] += 1
				#print("epic '{}' mapped to local db row id {}".format(guid, epic_id))

		print("{} epic row(s) updated".format(update_count['epics']))

		# write each issue to the db
		for guid, issue in self.unique_issues.items():

			new_issue = dict(issue)

			# convert guids to ids
			epic_guid = issue.get('epic_guid')
			sprint_guid = issue.get('sprint_guid')
			new_issue['epic_id'] = epic_guid_map.get(epic_guid)
			new_issue['sprint_id'] = sprint_guid_map.get(sprint_guid)
			del new_issue['epic_guid']
			del new_issue['sprint_guid']

			issue_id = issueModel.syncIssue(new_issue)
			if issue_id is not None:
				update_count['issues'] += 1
				#print("issue guid '{}' mapped to local db row id {}".format(new_issue.get('guid'), issue_id))

		print("{} issue row(s) updated".format(update_count['issues']))

		# close db connection
		db.disconnect()

