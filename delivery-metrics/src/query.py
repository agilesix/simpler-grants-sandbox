#!/usr/bin/env python3

import sys
sys.path.insert(0, './loader')

from delivery_metrics_config import DeliveryMetricsConfig
from delivery_metrics_database import DeliveryMetricsDatabase
import functools 
import time


class DeliveryMetricsCalculator:

	def __init__(self, dbh):
		self.dbh = dbh


	def getPercentComplete(self):

		deliverable_sql = ''' 
			select 
				d.id, 
				d.title, 
				m.d_effective,
				q.name
			from 
				deliverable d 
			inner join deliverable_quad_map m on m.deliverable_id = d.id
			inner join quad q on q.id = m.quad_id
			where
				m.d_effective <= ?
			order by d_effective desc;
		'''

		epic_sql = '''
			select 
				e.id, 
				e.title, 
				m.d_effective
			from 
				epic e
			inner join epic_deliverable_map m on m.epic_id = e.id
			where 
				m.deliverable_id = ? and
				m.d_effective <= ?
			order by d_effective desc
		'''

		issue_sql = '''
			select 
				i.id, 
				i.title, 
				h.points, 
				h.status, 
				h.is_closed,
				h.d_effective 
			from 
				issue i 
			inner join issue_history h on h.issue_id = i.id
			where 
				i.epic_id = ? and
				h.d_effective <= ?
			order by d_effective 
		'''

		# init vars
		quad_is_displayed = dict()
		max_effective_date = self.dbh.getEffectiveDate()
		unique_issues = dict()

		# get deliverables in each quad
		cursor = self.dbh.cursor()
		cursor.execute(deliverable_sql, (max_effective_date,))
		deliverables = cursor.fetchall()
		for d_row in deliverables: 

			# parse results
			d_id = d_row[0]
			d_title = d_row[1]
			d_effective = d_row[2]
			quad_name = d_row[3]
			
			# output
			if quad_is_displayed.get(quad_name) is None:
				print("QUAD: {}".format(quad_name))
				quad_is_displayed[quad_name] = True
			print("\tDELIVERABLE: {} :: {}".format(d_title, d_effective ))
			
			# get epics in each deliverable
			cursor.execute(epic_sql, (d_id, max_effective_date))
			epics = cursor.fetchall()
			for e_row in epics:

				# output
				e_id = e_row[0]
				e_title = e_row[1]
				e_effective = e_row[2]
				print("\t\tEPIC: {} :: {}".format(e_title, e_effective ))
				
				# get issues in each epic
				cursor.execute(issue_sql, (e_id, max_effective_date))
				issues = cursor.fetchall()
				for i_row in issues:

					# output
					i_id = i_row[0]
					i_title = i_row[1]
					i_points = i_row[2]
					i_status = i_row[3]
					i_closed = bool(i_row[4])
					i_effective = i_row[5]
					#print("\t\t\tISSUE: {} :: {} :: {} :: {}".format(i_title, i_points, i_status, i_effective))

					# aggregate results for processing outside these nested loops
					if i_id not in unique_issues:
						unique_issues[i_id] = {
							'is_closed': False,
							'points': 0
						}
					unique_issues[i_id]['is_closed'] = i_closed
					unique_issues[i_id]['points'] = i_points

		cursor.close()

		# calculate % complete (issues)
		total_issues = len(unique_issues)
		total_issues_closed = functools.reduce(
			lambda x, y: x+1 if y['is_closed'] is True else x,
			unique_issues.values(),
			0
		)
		percent_complete_issues = round(100*(total_issues_closed / total_issues), 1)

		# calculate % complete (points)
		total_points = functools.reduce(lambda x, y: x+int(y['points']), unique_issues.values(), 0)
		total_points_closed = functools.reduce(
			lambda x, y: x+y['points'] if y['is_closed'] is True else x,
			unique_issues.values(),
			0
		)
		percent_complete_points = round(100*(total_points_closed / total_points), 1)

		# output summarized results
		print("RESULTS")
		print("Total Issues Closed: {}".format(str(total_issues_closed)))
		print("Total Issues: {}".format(str(total_issues)))
		print("Issues Complete: {}%".format(str(percent_complete_issues)))
		print("Total Points Closed: {}".format(str(total_points_closed)))
		print("Total Points: {}".format(str(total_points)))
		print("Points Complete: {}%".format(str(percent_complete_points)))
		print("---")




if __name__ == "__main__":

	#effective = time.strptime('20241007', '%Y%m%d')
	effective = None

	config = DeliveryMetricsConfig(effective)
	dbh = DeliveryMetricsDatabase(config)

	calc = DeliveryMetricsCalculator(dbh)
	calc.getPercentComplete()

	dbh.disconnect()


