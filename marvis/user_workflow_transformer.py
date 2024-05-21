import requests
import re


def format_action_details(details):
    formatted_details = details.strip().replace('\n', ' ')
    formatted_details = formatted_details.strip().replace('\"', "'")
    formatted_details = re.sub(' +', ' ', formatted_details)
    formatted_details = formatted_details.replace("DIV", "ELEMENT").replace("A", "LINK")
    return formatted_details


def transform_workflow_data(workflow_data):
    """Transform the workflow data to the required format."""
    workflow_list = []

    for workflow in workflow_data:
        workflow_detail = []
        for action_group in workflow.get('action_groups', []):
            for action in action_group.get('actions', []):
                action_details = action.get('action_details', '').strip()
                action_details = format_action_details(action_details)

                action_performed = action.get('action_performed', '').strip()

                if action_performed.lower() == 'click':
                    workflow_detail.append({
                        "act": "click_element",
                        "step": action_details or "Perform click action"
                    })
                elif action_performed.lower() == 'type':
                    workflow_detail.append({
                        "act": "text_entry",
                        "step": action_details or "Type text"
                    })
                elif action_performed.lower() == 'wait':
                    workflow_detail.append({
                        "act": "time_sleep",
                        "step": action_details or "Wait for action"
                    })
                else:
                    workflow_detail.append({
                        "act": action_performed.lower(),
                        "step": action_details or "Perform action"
                    })
        workflow_list.append({f"workflow_{workflow.get('workflow_number')}": workflow_detail})

    return workflow_list






