import copy
import json
from typing import Dict, List, Tuple

from autogpt.config import Config
from autogpt.llm.llm_utils import create_chat_completion

cfg = Config()


def get_newly_trimmed_messages(
    full_message_history: List[Dict[str, str]],
    current_context: List[Dict[str, str]],
    last_memory_index: int,
) -> Tuple[List[Dict[str, str]], int]:
    new_messages = [
        copy.copy(msg)
        for i, msg in enumerate(full_message_history)
        if i > last_memory_index
    ]
    new_messages_not_in_context = [
        msg for msg in new_messages if msg not in current_context
    ]

    new_index = last_memory_index
    if new_messages_not_in_context:
        last_message = new_messages_not_in_context[-1]
        new_index = full_message_history.index(last_message)

    return new_messages_not_in_context, new_index


def update_running_summary(current_memory: str, new_events: List[Dict]) -> str:
    for event in new_events:
        if event["role"].lower() == "assistant":
            event["role"] = "you"
            content_dict = json.loads(event["content"])
            if "thoughts" in content_dict:
                del content_dict["thoughts"]
            event["content"] = json.dumps(content_dict)
        elif event["role"].lower() == "system":
            event["role"] = "your computer"

    new_events = [event for event in new_events if event["role"] != "user"]

    if not new_events:
        new_events = "Nothing new happened."

    prompt = f'''Your task is to create a concise running summary of actions and information results in the provided text, focusing on key and potentially important information to remember.

You will receive the current summary and the your latest actions. Combine them, adding relevant key information from the latest development in 1st person past tense and keeping the summary concise.

Summary So Far:
"""
{current_memory}
"""

Latest Development:
"""
{new_events}
"""
'''

    messages = [
        {
            "role": "user",
            "content": prompt,
        }
    ]

    current_memory = create_chat_completion(messages, cfg.fast_llm_model)

    message_to_return = {
        "role": "system",
        "content": f"This reminds you of these events from your past: \n{current_memory}",
    }

    return message_to_return
