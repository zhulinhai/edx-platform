import StringIO
from textwrap import dedent
import unittest

from openedx.stanford.lms.djangoapps.instructor.views.tools import generate_course_forums_d3


def _clean_text(text):
    text = text or ''
    text = dedent(text)
    text = text.strip()
    return text


class TestGenerateD3CourseForums(unittest.TestCase):
    """
    Tests generation of csv string for use in graphing course forums
    """
    def test_regular(self):
        """
        Test Generating d3 usable csvs
        """
        data_string = _clean_text(
            """
            Date,Activity Type,Number New,Votes
            2014-10-8,CommentThread,2,3
            2014-10-10,CommentThread,1,4
            2014-10-10,Response,1,3
            2014-10-11,CommentThread,1,0
            2014-10-11,Response,5,2
            2014-10-11,Comment,2,0
            2014-10-12,CommentThread,1,0
            2014-10-12,Response,1,0
            2014-10-12,Comment,1,0
            2014-10-13,CommentThread,16,5
            2014-10-13,Response,23,5
            2014-10-13,Comment,9,0
            2014-10-14,CommentThread,20,6
            2014-10-14,Response,51,4
            2014-10-14,Comment,17,0
            2014-10-15,CommentThread,18,1
            2014-10-15,Response,43,13
            2014-10-15,Comment,18,0
            2014-10-16,CommentThread,10,3
            """
        )
        to_match = _clean_text(
            """
            Date,New Threads,Responses,Comments
            2014-10-8,2,0,0
            2014-10-10,1,1,0
            2014-10-11,1,5,2
            2014-10-12,1,1,1
            2014-10-13,16,23,9
            2014-10-14,20,51,17
            2014-10-15,18,43,18
            2014-10-16,10,0,0
            """
        )
        memfile = StringIO.StringIO(data_string)
        output = generate_course_forums_d3(memfile)
        self.assertEquals(output, to_match)

    def test_edge_case(self):
        """
        Test Generating d3 usable csvs
        """
        data_string = _clean_text(
            """
            Date,Activity Type,Number New,Votes
            2014-10-8,CommentThread,2,3
            """
        )
        memfile = StringIO.StringIO(data_string)
        output = generate_course_forums_d3(memfile)
        to_match = _clean_text(
            """
            Date,New Threads,Responses,Comments
            2014-10-8,2,0,0
            """
        )
        self.assertEquals(output, to_match)

    def test_no_data(self):
        """
        Test Generating d3 usable csvs
        """
        data_string = 'Date,Activity Type,Number New,Votes'
        memfile = StringIO.StringIO(data_string)
        output = generate_course_forums_d3(memfile)
        self.assertIsNone(output)
