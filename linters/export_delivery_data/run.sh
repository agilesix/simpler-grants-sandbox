#! /bin/bash
# Propagate project metadata from parent issues to their children
# Usage:
# ./linters/bulk_inherit_metadata/run.sh \
#   --org HHS \
#   --project 12


# #######################################################
# Parse command line args with format `--option arg`
# #######################################################

# see this stack overflow for more details:
# https://stackoverflow.com/a/14203146/7338319
batch=100
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      echo "Running in dry run mode"
      dry_run=YES
      shift # past argument
      ;;
    --batch)
      batch="$2"
      shift # past argument
      shift # past value
      ;;
    --org)
      org="$2"
      shift # past argument
      shift # past value
      ;;
    --roadmap-project)
      roadmap_project="$2"
      shift # past argument
      shift # past value
      ;;
    --sprint-project)
      sprint_project="$2"
      shift # past argument
      shift # past value
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

# #######################################################
# Set script-specific variables
# #######################################################

mkdir -p tmp
roadmap_items_file="./tmp/roadmap-export.json"
sprint_items_file="./tmp/sprint-export.json"
tasks_file="./tmp/task-level-issues.json"
epics_file="./tmp/epic-level-issues.json"
deliverables_file="./tmp/deliverable-level-issues.json"
root="./linters/export_delivery_data"
roadmap_query=$(cat "${root}/getRoadmapData.graphql")
sprint_query=$(cat "${root}/getSprintData.graphql")

# #######################################################
# Export the roadmap data
# #######################################################

gh api graphql \
 --paginate \
 --field login="${org}" \
 --field project="${roadmap_project}" \
 --field batch="${batch}" \
 --header 'GraphQL-Features:sub_issues' \
 --header 'GraphQL-Features:issue_types' \
 -f query="${roadmap_query}" \
 --jq ".data.organization.projectV2.items.nodes" |\
 # combine results into a single array
 jq --slurp 'add' |\
 jq "[
 # iterate through each project item
 .[] |
 # reformat each item
 {
    issue_title: .content.title,
    issue_url: .content.url,
    issue_parent: .content.parent.url,
    issue_type: .content.issueType.name,
    issue_is_closed: .content.closed,
    issue_opened_at: .content.createdAt,
    issue_closed_at: .content.closedAt,
    deliverable_pillar: .pillar.name,
    quad_id: .quad.iterationId,
    quad_name: .quad.title,
    quad_start: .quad.startDate,
    quad_length: .quad.duration,
    quad_end: (
      if .quad.startDate == null 
      then null 
      else (
        (.quad.startDate | strptime(\"%Y-%m-%d\") | mktime) 
        + (.quad.duration * 86400) | strftime(\"%Y-%m-%d\")
      )
      end
    ),
 }
 
 ]" > $roadmap_items_file  # write output to a file

# #######################################################
# Export the sprint data
# #######################################################

gh api graphql \
 --paginate \
 --field login="${org}" \
 --field project="${sprint_project}" \
 --field batch="${batch}" \
 --header 'GraphQL-Features:sub_issues' \
 --header 'GraphQL-Features:issue_types' \
 -f query="${sprint_query}" \
 --jq ".data.organization.projectV2.items.nodes" |\
 # combine results into a single array
 jq --slurp 'add' |\
 jq "[
 # iterate through each project item
 .[] |
 # reformat each item
 {
    issue_title: .content.title,
    issue_url: .content.url,
    issue_parent: .content.parent.url,
    issue_type: .content.issueType.name,
    issue_is_closed: .content.closed,
    issue_opened_at: .content.createdAt,
    issue_closed_at: .content.closedAt,
    issue_status: .status.name,
    issue_points: .points.number,
    sprint_id: .sprint.iterationId,
    sprint_name: .sprint.title,
    sprint_start: .sprint.startDate,
    sprint_length: .sprint.duration,
    sprint_end: (
      if .sprint.startDate == null 
      then null 
      else (
        (.sprint.startDate | strptime(\"%Y-%m-%d\") | mktime) 
        + (.sprint.duration * 86400) | strftime(\"%Y-%m-%d\")
      )
      end
    ),
 } |
 # filter for task-level issues
 select(.issue_type != \"Deliverable\")
 
 ]" > $sprint_items_file  # write output to a file

# #######################################################
# Transform the exported data
# #######################################################

python "${root}/join_parent_issues.py" \
 --sprint-file-in $sprint_items_file \
 --roadmap-file-in $roadmap_items_file \
 --task-file-out $tasks_file
