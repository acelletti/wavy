import collections
import wavy.detail

Tags = collections.namedtuple('Tags', wavy.detail.TAG_PROPS)
"""
Stores tags associated with a file.

Attributes:
    name (str): The name of the file (or *project*).
    subject (str): The subject.
    artist (str): The artist who created this.
    comment (str): A text comment.
    keywords (str): The keywords for the project or file.
    software (str): The software used to create the file.
    engineer (str): The engineer.
    technician (str): The technician.
    creation_date (str): The creation date.
    genre (str): Genre of content.
    copyright (str): The copyright information.
"""

# set all defaults to empty string
Tags.__new__.__defaults__ = ('',) * len(wavy.detail.TAG_PROPS)
