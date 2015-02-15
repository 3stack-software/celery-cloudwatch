__author__ = 'nathan.muir'

from collections import defaultdict
import threading
from stats import Stats
import sys, traceback


class State(object):

    def __init__(self):
        self._mutex = threading.Lock()

        # track the number of events in the current window
        self.totals = defaultdict(lambda: defaultdict(int))

        self.time_to_start = defaultdict(Stats)

        self.time_to_process = defaultdict(Stats)

        # keep track of sent tasks and their timestamps
        self.waiting_tasks = {}
        self.running_tasks = {}
        self.task_types = {}

    def freeze_while(self, fun, *args, **kwargs):
        clear_after = kwargs.pop('clear_after', True)
        with self._mutex:
            try:
                return fun(*args, **kwargs)
            except:
                print "Exception in user code:"
                print '-'*60
                traceback.print_exc(file=sys.stdout)
                print '-'*60
            finally:
                if clear_after:
                    self._clear()

    def _clear(self):
        # reset all the counters
        self.totals = defaultdict(lambda: defaultdict(int))

        self.time_to_start = defaultdict(Stats)

        self.time_to_process = defaultdict(Stats)

    def num_waiting_tasks(self, queue='celery'):
        count = 0
        for task in self.waiting_tasks.values():
            if task['q'] == queue:
                count += 1
        return count

    def num_running_tasks(self, queue='celery'):
        count = 0
        for task in self.running_tasks.values():
            if task['q'] == queue:
                count += 1
        return count

    def task_sent(self, event):
        with self._mutex:
            self.waiting_tasks[event['uuid']] = {
                'ts': event['timestamp'],
                'q': event['queue']
            }
            # increment totals for this task type
            self.totals[event['name']]['waiting'] += 1
            self.task_types[event['uuid']] = event['name']

    def task_started(self, event):
        with self._mutex:
            if event['uuid'] in self.task_types:
                task_type = self.task_types[event['uuid']]
                queue = 'celery'
                # only track averages for tasks that have a waiting-started timestamp
                #  can only determine the queue from the 'task-sent' event
                if event['uuid'] in self.waiting_tasks:
                    waiting_task = self.waiting_tasks[event['uuid']]
                    queue = waiting_task['q']
                    self.time_to_start[task_type] += event['timestamp'] - waiting_task['ts']
                    del self.waiting_tasks[event['uuid']]

                self.running_tasks[event['uuid']] = {
                    'ts': event['timestamp'],
                    'q': queue
                }
                self.totals[task_type]['running'] += 1

    def task_succeeded(self, event):
        with self._mutex:
            if event['uuid'] in self.task_types:
                task_type = self.task_types[event['uuid']]
                del self.task_types[event['uuid']]
                if event['uuid'] in self.waiting_tasks:
                    del self.waiting_tasks[event['uuid']]
                # only track averages for tasks that have a waiting-started timestamp
                if event['uuid'] in self.running_tasks:
                    self.time_to_process[task_type] += event['timestamp'] - self.running_tasks[event['uuid']]['ts']
                    del self.running_tasks[event['uuid']]

                self.totals[task_type]['completed'] += 1


    def task_failed(self, event):
        with self._mutex:
            if event['uuid'] in self.task_types:
                task_type = self.task_types[event['uuid']]
                del self.task_types[event['uuid']]
                if event['uuid'] in self.waiting_tasks:
                    del self.waiting_tasks[event['uuid']]
                if event['uuid'] in self.running_tasks:
                    del self.running_tasks[event['uuid']]

                self.totals[task_type]['failed'] += 1
