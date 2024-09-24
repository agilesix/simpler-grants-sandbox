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
    --project)
      project="$2"
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
proj_items_file="./tmp/project-items-export.json"
to_update_file="./tmp/items-to-update.txt"
root="./linters/bulk_inherit_metadata"
query=$(cat "${root}/getProjectItems.graphql")
mutation=$(cat "${root}/updateProjectFields.graphql")

# #######################################################
# Export project items
# #######################################################

gh api graphql \
 --paginate \
 --field login="${org}" \
 --field project="${project}" \
 --field batch="${batch}" \
 --header 'GraphQL-Features:sub_issues' \
 --header 'GraphQL-Features:issue_types' \
 -f query="${query}" \
 --jq ".data.organization.projectV2.items.nodes" |\
 # combine results into a single array
 jq --slurp 'add' |\
 jq "[.[] |
 # filter for the issues with a parent
 select(.content.parent != null)]" > $proj_items_file  # write output to a file

# #######################################################
# Filter for items that need to be updated
# #######################################################

# Extract issues whose metadata conflicts with the metadata of their parent
# Use the -c flag to condense each item to a single row in the output file
jq -c "
 .[] |

# start editing parent object in place
(.content.parent) |= (

  # filter for the correct project
  .projectItems.nodes[] as \$node |
  select(\$node.project.number == ${project}) |

  # pluck projectId, pillar, and quad values from node
  {
    projectId: \$node.project.id,
    pillar: \$node.pillar,
    quad: \$node.quad
  }

) |
# end editing parent object in place

  # filter for items that have metadata conflicts with parent issue
  select((.content.parent.pillar != .pillar) or (.content.parent.quad != .quad)) |

  # pluck itemId, projectId, pillar, and quad values
  {
    itemId: .id,
    projectId: .content.parent.projectId,
    pillar: .content.parent.pillar,
    quad: .content.parent.quad,
  }
" $proj_items_file > $to_update_file

# #######################################################
# Create a function to update project fields
# #######################################################

function updateProjectItem()
{
  # assign positional args to named variables
  data=$1
  mutation=$2

  # parse additional variables from the row data   
  project_id=$(echo "$data" | jq --raw-output '.projectId')
  item_id=$(echo "$data" | jq --raw-output '.itemId')
  # pillar field and value
  pillar_field_id=$(echo "$data" | jq --raw-output '.pillar.field.id')
  pillar_val=$(echo "$data" | jq --raw-output '.pillar.optionId')
  # quad field and value
  quad_field_id=$(echo "$data" | jq --raw-output '.quad.field.id')
  quad_val=$(echo "$data" | jq --raw-output '.quad.iterationId')

  # make an API call to update project item
  echo $"Updating item: ${item_id}"
  gh api graphql \
   --field projectId="${project_id}" \
   --field itemId="${item_id}" \
   --field pillarFieldId="${pillar_field_id}" \
   --field pillarValue="${pillar_val}" \
   --field quadFieldId="${quad_field_id}" \
   --field quadValue="${quad_val}" \
   -f query="${mutation}"
}

# #######################################################
# Use this function to update each item
# #######################################################

while IFS= read -r row; do
    updateProjectItem "$row" "$mutation"
done < $to_update_file
