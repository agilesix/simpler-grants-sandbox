"""Use the parent issue to join task-level tickets to the deliverable they support."""

import argparse
import json
from dataclasses import dataclass
from enum import Enum


class IssueType(Enum):
    """Supported issue types"""

    BUG = "Bug"
    TASK = "Task"
    EPIC = "Epic"
    ENHANCEMENT = "Enhancement"
    DELIVERABLE = "Deliverable"
    NONE = None


@dataclass
class IssueCommon:
    """Stores information about issue type and parent (if applicable)"""

    title: str
    url: str
    parent: str | None
    issue_type: IssueType


@dataclass
class SprintItem(IssueCommon):

    sprint_name: str | None
    sprint_start: str | None
    sprint_length: int | None
    sprint_end: str | None
    points: int | None


@dataclass
class RoadmapItem(IssueCommon):

    quad_name: str | None
    quad_start: str | None
    quad_length: int | None
    quad_end: str | None
    pillar: str | None


def load_json_file(path: str) -> list[dict]:
    """Load contents of a JSON file into a dictionary."""
    with open(path) as f:
        return json.load(f)


def dump_to_json(path: str, data: dict | list[dict]):
    """Write a dictionary or list of dicts to a json file."""
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def populate_issue_lookup_table(
    lookup: dict[str, IssueCommon],
    issues: list[dict],
) -> dict[str, IssueCommon]:
    """Populate a lookup table that maps issue URLs to their issue type and parent."""
    for issue in issues:
        url = issue.get("url")
        if not url:
            print(f"Skipping this issue because it doesn't have a URL: {issue}")
            continue
        entry = IssueCommon(
            title=issue.get("title", ""),
            url=url,
            parent=issue.get("parent"),
            issue_type=IssueType(issue.get("issue_type")),
        )
        lookup[url] = entry
    return lookup


def get_parent_deliverable(
    child_url: str,
    lookup: dict[str, IssueCommon],
) -> str | None:
    """Traverse the lookup table to find the parent deliverable for a given task."""
    # Get the initial child issue and its parent (if applicable) from the URL
    child = lookup.get(child_url)
    if not child:
        raise ValueError(f"Lookup doesn't contain issue with url: {child_url}")
    if not child.parent:
        return None

    # Travel up the issue hierarchy until we:
    #  - Find a parent issue with a "Deliverable" type
    #  - Get to an issue without a parent
    #  - Have traversed 5 issues (breaks out of issue cycles)
    parent_url = child.parent
    for _ in range(5):
        parent = lookup.get(parent_url)
        # If no parent is found, return None
        if not parent:
            return None
        # If the parent is a deliverable, return its URL
        if parent.issue_type == IssueType.DELIVERABLE:
            return parent_url
        # If the parent doesn't have a its own parent, return None
        if not parent.parent:
            return None
        # Otherwise update the parent_url to "grandparent" and continue
        parent_url = parent.parent

    # Return the URL of the parent deliverable (or None)
    return None


def filter_items(
    data: list[dict],
    schema: type[IssueCommon],
    valid_types: list[IssueType],
    parent_lookup: dict | None = None,
) -> list[dict]:
    """Filter data for the correct type and"""
    result = []
    for issue_data in data:
        issue = schema(**issue_data)
        # Drop deliverables and epics
        if IssueType(issue.issue_type) not in valid_types:
            continue
        entry = {**issue_data}
        if parent_lookup:
            entry["deliverable"] = get_parent_deliverable(
                child_url=issue.url,
                lookup=parent_lookup,
            )
        # Add the entry to the output list
        result.append(entry)
    return result


def transform_issue_data(
    sprint_file_in: str,
    roadmap_file_in: str,
    deliverable_file_out: str,
    epic_file_out: str,
    task_file_out: str,
) -> None:
    """Runs a transformation pipeline to transform issue data to the correct format."""
    # Load sprint and roadmap data
    sprint_data_in = load_json_file(sprint_file_in)
    roadmap_data_in = load_json_file(roadmap_file_in)
    # Populate a lookup table with this data
    lookup = {}
    lookup = populate_issue_lookup_table(lookup, sprint_data_in)
    lookup = populate_issue_lookup_table(lookup, roadmap_data_in)

    # Filter sprint data for tasks and write to JSON
    tasks_out = filter_items(
        data=sprint_data_in,
        schema=SprintItem,
        valid_types=[IssueType.BUG, IssueType.TASK, IssueType.NONE],
        parent_lookup=lookup,
    )
    dump_to_json(task_file_out, tasks_out)

    # Filter roadmap data for epics and write to JSON
    epics_out = filter_items(
        data=roadmap_data_in,
        schema=RoadmapItem,
        valid_types=[IssueType.EPIC],
        parent_lookup=lookup,
    )
    dump_to_json(epic_file_out, epics_out)

    # Filter roadmap data for deliverables and write to JSON
    deliverables_out = filter_items(
        data=roadmap_data_in,
        schema=RoadmapItem,
        valid_types=[IssueType.DELIVERABLE],
    )
    dump_to_json(deliverable_file_out, deliverables_out)


if __name__ == "__main__":

    # Create parser
    parser = argparse.ArgumentParser(
        prog="ProgramName",
        description="What the program does",
        epilog="Text at the bottom of help",
    )
    # Add arguments
    parser.add_argument(
        "--sprint-file-in",
        help="Path to JSON file with sprint data",
    )
    parser.add_argument(
        "--roadmap-file-in",
        help="Path to JSON file with roadmap data",
    )
    parser.add_argument(
        "--task-file-out",
        help="Path to output location for JSON of tasks",
    )
    parser.add_argument(
        "--epic-file-out",
        help="Path to output location for JSON of epics",
    )
    parser.add_argument(
        "--deliverable-file-out",
        help="Path to output location for JSON of deliverables",
    )
    # Parse arguments from the CLI
    args = parser.parse_args()
    # run transformation pipeline
    transform_issue_data(
        sprint_file_in=args.sprint_file_in,
        roadmap_file_in=args.roadmap_file_in,
        task_file_out=args.task_file_out,
        epic_file_out=args.epic_file_out,
        deliverable_file_out=args.deliverable_file_out,
    )
