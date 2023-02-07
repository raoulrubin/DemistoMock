""" Markdown formatting definitions """
from typing import List
from enum import Enum

entryTypes = {"note": 1}
formats = {"markdown": 1, "json" : 2}


def tableToMarkdown(title: str, data: List, headers: List):
    return 'markdown'


class EntryType(Enum):
    FILE = 1,
    ENTRY_INFO_FILE = 2,
    IMAGE = 3,
    VIDEO_FILE = 4,
    STATIC_VIDEO_FILE = 5


class IncidentStatus(Enum):
    DONE = 0