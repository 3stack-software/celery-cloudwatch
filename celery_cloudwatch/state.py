import sys
import traceback
import threading
import logging
from collections import defaultdict, namedtuple

from stats import Stats

logger = logging.getLogger('ccwatch')

Task = namedtuple('Task', ['timestamp', 'name'])


class State(object):

    # http://docs.celeryproject.org/en/latest/userguide/monitoring.html

    def __init__(self):
        self._mutex = threading.Lock()

        # track the number of events in the current window
        self.task_event_sent = defaultdict(int)
        self.task_event_started = defaultdict(int)
        self.task_event_succeeded = defaultdict(int)
        self.task_event_failed = defaultdict(int)

        self.time_to_start = defaultdict(Stats)

        self.time_to_process = defaultdict(Stats)

        # keep track of sent tasks and their timestamps
        self.waiting_tasks = {}
        self.running_tasks = {}

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
        self.task_event_sent = defaultdict(int)
        self.task_event_started = defaultdict(int)
        self.task_event_succeeded = defaultdict(int)
        self.task_event_failed = defaultdict(int)

        self.time_to_start = defaultdict(Stats)

        self.time_to_process = defaultdict(Stats)

    def num_waiting_by_task(self):
        totals = {}
        for task in self.waiting_tasks.values():
            totals.setdefault(task.name, 0)
            totals[task.name] += 1
        return totals

    def num_running_by_task(self):
        totals = {}
        for task in self.waiting_tasks.values():
            totals.setdefault(task.name, 0)
            totals[task.name] += 1
        return totals

    def task_sent(self, event):
        with self._mutex:
            uuid = event['uuid']
            if uuid not in self.running_tasks:
                task = Task(event['timestamp'], event['name'])
                self.waiting_tasks[uuid] = task
                self.task_event_sent[task.name] += 1
            else:
                # If the task is already in self.tasks, it means
                #  that it was `task_started` before the `task_sent` event was received.
                logger.info('Got late task-sent for %r', event)

    def task_started(self, event):
        with self._mutex:
            uuid = event['uuid']
            task = self.waiting_tasks.pop(uuid, None)
            if task is None:
                logger.warn('Got early task-started for %r', event)
                self.running_tasks[uuid] = Task(event['timestamp'], 'unknown')
            else:
                self.task_event_started[task.name] += 1
                self.running_tasks[uuid] = Task(event['timestamp'], task.name)
                self.time_to_start[task.name] += event['timestamp'] - task.timestamp

    def task_succeeded(self, event):
        with self._mutex:
            uuid = event['uuid']
            task = self.running_tasks.pop(uuid, None)
            if task is None:
                logger.warn('Got task-succeeded for unknown %r', event)
                return
            self.task_event_succeeded[task.name] += 1
            self.time_to_process[task.name] += event['timestamp'] - task.timestamp

    def task_failed(self, event):
        with self._mutex:
            uuid = event['uuid']
            task = self.running_tasks.pop(uuid, None)
            if task is None:
                logger.warn('Got task-failed for unknown %r', event)
                return
            self.task_event_failed[task.name] += 1
