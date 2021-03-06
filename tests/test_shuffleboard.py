#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_shuffleboard
----------------------------------

Tests for `shuffleboard` module.
"""

import json
import unittest
import re

from shuffleboard import github_api as gha
from shuffleboard import shuffleboard as sb

# setting a global var since I'm not sure how singletons work in Python
#  also this pattern is really sloppy but it does the job for now
MOCK_OUTPUT = {}


# Mock a csv class that overrides our methods so we don't actually write a
# file and can just capture the output
class MockCSVWriter:
    def __init__(self, csvfile=None, *args, **kwargs):
        if csvfile:
            parts = csvfile.name.split('/')[-1].split('_')
            MOCK_OUTPUT[parts[1]] = []
            self.sheet = MOCK_OUTPUT[parts[1]]
        else:
            self.sheet = []

    def writerow(self, i):
        self.sheet.append(i)


class MockTxtFileWriter:
    def __init__(self):
        self.data = None

    def write(self, data):
        self.data = data
        return


class TestShuffleboard(unittest.TestCase):

    def setUp(self):
        # load sample json files

        with open('tests/github_events.json', 'r') as f:
            self.events_json = json.load(f)

        with open('tests/gh_headers.json', 'r') as f:
            self.gh_headers = json.load(f)

    def tearDown(self):
        pass

    # TODO fix this or remove this class
    # def test_events_cli_writer(self):
    #     output = []
    #     writer = sb.EventsCLIWriter(printer=output.append)
    #     writer.write(self.events)
    #     # print(output) # for debugging
    #     self.assertEqual(16, len(output))

    # TODO: test aggregate events
    def test_events_csv_writer(self):
        csv_writer = MockCSVWriter
        # TODO: this should use mock_open to prevent empty file creation
        writer = sb.EventsCSVWriter(csv_writer=csv_writer)
        events = writer.aggregate_events(self.events_json)
        writer.write(events=events, out_path='/tmp')

        # minimal tests to make sure the format is right
        self.assertTrue('PullRequestEvent.csv' in MOCK_OUTPUT)
        self.assertEqual(len(MOCK_OUTPUT.keys()), 8)
        self.assertTrue(isinstance(MOCK_OUTPUT['PullRequestEvent.csv'],
                                   list))
        self.assertTrue(isinstance(MOCK_OUTPUT[
                                       'PullRequestEvent.csv'][0],
                                   list))
        # clear it out in case other tests use it
        #  again, this is not an ideal pattern but it works for now
        MOCK_OUTPUT.clear()

    def test_gh_headers_txt_writer(self):
        # just checks running the code path and documents the expected
        # format for recording the github headers from the last run
        mock_writer = MockTxtFileWriter()
        header_writer = sb.GhHeaderTxtFileWriter(writer=mock_writer,
                                                 filename='foo',
                                                 out_path='foo')
        header_writer.write(self.gh_headers)
        self.assertEqual(len(mock_writer.data), 924)
        self.assertTrue(re.match('{".*"}', mock_writer.data))

if __name__ == '__main__':
    unittest.main()
