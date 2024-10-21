#! /bin/bash
# Set default values for sprint and points when those fields are unset
# Usage:
# ./linters/set_fields_on_close/run.sh \
#  --url "https://github.com/HHS/simpler-grants-gov/issues/123" \
#  --org "HHS" \
#  --project 13 \
#  --sprint-field "Sprint" \
#  --points-field "Points"


# #######################################################
# Parse command line args with format `--option arg`
# #######################################################

# see this stack overflow for more details:
# https://stackoverflow.com/a/14203146/7338319
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      echo "Running in dry run mode"
      dry_run=YES
      shift # past argument
      ;;
    --url)
      issue_url="$2"
      shift # past argument
      shift # past value
      ;;
    --org)
      org="$2"
      shift # past argument
      shift # past value
      ;;
    --project)
      project="$2"
      shift # past argument
      shift # past value
      ;;
    --sprint-field)
      sprint_field="$2"
      shift # past argument
      shift # past value
      ;;
    --points-field)
      points_field="$2"
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
raw_data_file="tmp/closed-issue-data-raw.json"
item_data_file="tmp/closed-issue-data.json"
field_data_file="tmp/field-data.json"
root="./linters/set_fields_on_close"
item_query=$(cat "${root}/getItemMetadata.graphql")
field_query=$(cat "${root}/getFieldMetadata.graphql")

# #######################################################
# Fetch issue metadata
# #######################################################

gh api graphql \
 --header 'GraphQL-Features:issue_types' \
 --field url="${issue_url}" \
 --field sprintField="${sprint_field}" \
 --field pointsField="${points_field}" \
 -f query="${item_query}" > $raw_data_file

# #######################################################
# Isolate the correct project item and issue type
# #######################################################

# Get project item
jq ".data.resource.projectItems.nodes[] |

 # filter for the item in the given project
 select(.project.number == ${project}) |

 # filter for items with the sprint or points fields unset
 select (.sprint == null or .points == null or .points.number == 0) |

 # format the output
 {
   itemId,
   projectId: .project.projectId,
   sprint: .sprint.iterationId,
   points: .points.number,
 }
 " $raw_data_file > $item_data_file  # read from raw and write to item_data_file

# Get issue type
issue_type=$(jq -r ".data.resource.issueType.name" $raw_data_file)

# #######################################################
# Fetch project metadata
# #######################################################

# if the output file contains a record
if [[ -s $item_data_file ]]; then
    # If issue is a Task, Bug, or Enhancement, fetch the project metadata
    case "${issue_type}" in 
    "Task"|"Bug"|"Enhancement")
        gh api graphql \
        --field org="${org}" \
        --field project="${project}" \
        --field sprintField="${sprint_field}" \
        --field pointsField="${points_field}" \
        -f query="${field_query}" \
        --jq ".data.organization.projectV2 |

        # reformat the field metadata
        {
        points,
        sprint: {
            fieldId: .sprint.fieldId,
            iterationId: .sprint.configuration.iterations[0].id,
        }
        }" > $field_data_file  # write output to a file
    ;;
    # If it's some other type, print a message and exit
    *)
        echo "Not updating because issue has type: ${issue_type}"
        exit 0
    ;;
    esac

    # get the itemId and the projectId
    item_id=$(jq -r '.itemId' "$item_data_file")
    project_id=$(jq -r '.projectId' "$item_data_file")

# otherwise print a success message and exit
else
    echo "Both sprint and points are set for issue: ${issue_url}"
    exit 0
fi 

# #######################################################
# Set the sprint value, if empty
# #######################################################

if jq -e ".points == null or .points == 0" $item_data_file > /dev/null; then

    echo "Updating points field for issue: ${issue_url}"
    point_field_id=$(jq -r '.points.fieldId' "$field_data_file")
    gh project item-edit \
     --id "${item_id}" \
     --project-id "${project_id}" \
     --field-id "${point_field_id}" \
     --number 1

else
    echo "Point value already set for issue: ${issue_url}"
fi

# #######################################################
# Set the sprint value, if empty
# #######################################################

if jq -e ".sprint == null" $item_data_file > /dev/null; then

    echo "Updating sprint field for issue: ${issue_url}"
    sprint_field_id=$(jq -r '.sprint.fieldId' "$field_data_file")
    iteration_id=$(jq -r '.sprint.iterationId' "$field_data_file")
    gh project item-edit \
     --id "${item_id}" \
     --project-id "${project_id}" \
     --field-id "${sprint_field_id}" \
     --iteration-id "${iteration_id}"

else
    echo "Sprint value already set for issue: ${issue_url}"
fi

# #######################################################
# Set the sprint value, if empty
# #######################################################

comment="Beep boop: Automatically setting the point and sprint values for this issue "
comment+="in project ${org}/${project} because they were unset when the issue was closed."

gh issue comment "${issue_url}" \
  --body "${comment}"
