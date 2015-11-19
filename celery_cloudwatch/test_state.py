from __future__ import unicode_literals

import unittest2 as unittest
from state import State

class TestPickleErrors(unittest.TestCase):

    def assert_success(self, s, task_name):
        self.assertEquals(s.task_event_sent[task_name], 1)
        self.assertEquals(s.task_event_started[task_name], 1)
        self.assertEquals(s.task_event_succeeded[task_name], 1)
        self.assertEquals(s.task_event_failed[task_name], 0)

    def assert_failure(self, s, task_name):
        self.assertEquals(s.task_event_sent[task_name], 1)
        self.assertEquals(s.task_event_started[task_name], 1)
        self.assertEquals(s.task_event_succeeded[task_name], 0)
        self.assertEquals(s.task_event_failed[task_name], 1)

    def test_success_0_1_2(self):
        s = State()
        s.task_sent({'uuid': 'a', 'name': 't', 'timestamp': 0})
        s.task_started({'uuid': 'a', 'timestamp': 1})
        s.task_succeeded({'uuid': 'a', 'timestamp': 2})
        self.assert_success(s, 't')

    def test_success_0_2_1(self):
        s = State()
        s.task_sent({'uuid': 'a', 'name': 't', 'timestamp': 0})
        s.task_succeeded({'uuid': 'a', 'timestamp': 2})
        s.task_started({'uuid': 'a', 'timestamp': 1})
        self.assert_success(s, 't')

    def test_success_1_0_2(self):
        s = State()
        s.task_started({'uuid': 'a', 'timestamp': 1})
        s.task_sent({'uuid': 'a', 'name': 't', 'timestamp': 0})
        s.task_succeeded({'uuid': 'a', 'timestamp': 2})
        self.assert_success(s, 't')

    def test_success_1_2_0(self):
        s = State()
        s.task_started({'uuid': 'a', 'timestamp': 1})
        s.task_succeeded({'uuid': 'a', 'timestamp': 2})
        s.task_sent({'uuid': 'a', 'name': 't', 'timestamp': 0})
        self.assert_success(s, 't')

    def test_success_2_0_1(self):
        s = State()
        s.task_succeeded({'uuid': 'a', 'timestamp': 2})
        s.task_sent({'uuid': 'a', 'name': 't', 'timestamp': 0})
        s.task_started({'uuid': 'a', 'timestamp': 1})
        self.assert_success(s, 't')

    def test_success_2_1_0(self):
        s = State()
        s.task_succeeded({'uuid': 'a', 'timestamp': 2})
        s.task_started({'uuid': 'a', 'timestamp': 1})
        s.task_sent({'uuid': 'a', 'name': 't', 'timestamp': 0})
        self.assert_success(s, 't')

    def test_failure_0_1_2(self):
        s = State()
        s.task_sent({'uuid': 'a', 'name': 't', 'timestamp': 0})
        s.task_started({'uuid': 'a', 'timestamp': 1})
        s.task_failed({'uuid': 'a', 'timestamp': 2})
        self.assert_failure(s, 't')

    def test_failure_0_2_1(self):
        s = State()
        s.task_sent({'uuid': 'a', 'name': 't', 'timestamp': 0})
        s.task_failed({'uuid': 'a', 'timestamp': 2})
        s.task_started({'uuid': 'a', 'timestamp': 1})
        self.assert_failure(s, 't')

    def test_failure_1_0_2(self):
        s = State()
        s.task_started({'uuid': 'a', 'timestamp': 1})
        s.task_sent({'uuid': 'a', 'name': 't', 'timestamp': 0})
        s.task_failed({'uuid': 'a', 'timestamp': 2})
        self.assert_failure(s, 't')

    def test_failure_1_2_0(self):
        s = State()
        s.task_started({'uuid': 'a', 'timestamp': 1})
        s.task_failed({'uuid': 'a', 'timestamp': 2})
        s.task_sent({'uuid': 'a', 'name': 't', 'timestamp': 0})
        self.assert_failure(s, 't')

    def test_failure_2_0_1(self):
        s = State()
        s.task_failed({'uuid': 'a', 'timestamp': 2})
        s.task_sent({'uuid': 'a', 'name': 't', 'timestamp': 0})
        s.task_started({'uuid': 'a', 'timestamp': 1})
        self.assert_failure(s, 't')

    def test_failure_2_1_0(self):
        s = State()
        s.task_failed({'uuid': 'a', 'timestamp': 2})
        s.task_started({'uuid': 'a', 'timestamp': 1})
        s.task_sent({'uuid': 'a', 'name': 't', 'timestamp': 0})
        self.assert_failure(s, 't')

