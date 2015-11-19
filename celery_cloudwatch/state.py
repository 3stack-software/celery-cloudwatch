import sys
import traceback
import threading
from operator import itemgetter
from collections import defaultdict, OrderedDict

from stats import Stats


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

        self.registry = {}

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

    def num_waiting_running_by_task(self):
        total_waiting = {}
        total_running = {}
        for task_record in self.registry.values():
            if task_record.name is not None:
                if task_record.started:
                    total_running.setdefault(task_record.name, 0)
                    total_running[task_record.name] += 1
                else:
                    total_waiting.setdefault(task_record.name, 0)
                    total_waiting[task_record.name] += 1
        return total_waiting, total_running

    def task_sent(self, event):
        with self._mutex:
            uuid = event['uuid']
            if uuid not in self.registry:
                task_name = event['name']
                self.registry[uuid] = TaskRecord(task_name, event['timestamp'], None, None, None)
                self.task_event_sent[task_name] += 1
                return

            task_record = self.registry[uuid]._replace(
                name=event['name'],
                sent_at=event['timestamp']
            )
            self.registry[uuid] = task_record
            self.task_event_sent[task_record.name] += 1

            if task_record.started_at is None:
                return

            self.task_event_started[task_record.name] += 1
            self.time_to_start[task_record.name] += task_record.wait_duration
            if not task_record.finished:
                return
            del self.registry[uuid]
            if task_record.successful:
                self.task_event_succeeded[task_record.name] += 1
                self.time_to_process[task_record.name] += task_record.processing_duration
            else:
                self.task_event_failed[task_record.name] += 1

    def task_started(self, event):
        with self._mutex:
            uuid = event['uuid']
            task_record = self.registry.get(uuid, None)
            if task_record is None:
                self.registry[uuid] = TaskRecord(None, None, event['timestamp'], None, None)
                return

            task_record = task_record._replace(started_at=event['timestamp'])
            self.registry[uuid] = task_record

            if task_record.sent_at is None:
                return

            self.task_event_started[task_record.name] += 1
            self.time_to_start[task_record.name] += task_record.wait_duration
            if not task_record.finished:
                return
            del self.registry[uuid]
            if task_record.successful:
                self.task_event_succeeded[task_record.name] += 1
                self.time_to_process[task_record.name] += task_record.processing_duration
            else:
                self.task_event_failed[task_record.name] += 1

    def task_succeeded(self, event):
        with self._mutex:
            uuid = event['uuid']
            task_record = self.registry.get(uuid, None)
            if task_record is None:
                self.registry[uuid] = TaskRecord(None, None, None, event['timestamp'], None)
                return

            task_record = task_record._replace(succeeded_at=event['timestamp'])

            if task_record.sent_at is None or task_record.started_at is None:
                self.registry[uuid] = task_record
                return
            del self.registry[uuid]
            self.task_event_succeeded[task_record.name] += 1
            self.time_to_process[task_record.name] += task_record.processing_duration

    def task_failed(self, event):
        with self._mutex:
            uuid = event['uuid']
            task_record = self.registry.get(uuid, None)
            if task_record is None:
                self.registry[uuid] = TaskRecord(None, None, None, None, event['timestamp'])
                return

            task_record = task_record._replace(failed_at=event['timestamp'])

            if task_record.sent_at is None or task_record.started_at is None:
                self.registry[uuid] = task_record
                return
            del self.registry[uuid]
            self.task_event_failed[task_record.name] += 1


class TaskRecord(tuple):
    'TaskRecord(name, sent_at, started_at, succeeded_at, failed_at)'

    __slots__ = ()

    _fields = ('name', 'sent_at', 'started_at', 'succeeded_at', 'failed_at')

    def __new__(_cls, name, sent_at, started_at, succeeded_at, failed_at):
        'Create new instance of TaskRecord(name, sent_at, started_at, succeeded_at, failed_at)'
        return tuple.__new__(_cls, (name, sent_at, started_at, succeeded_at, failed_at))

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new TaskRecord object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 5:
            raise TypeError('Expected 5 arguments, got %d' % len(result))
        return result

    def __repr__(self):
        'Return a nicely formatted representation string'
        return 'TaskRecord(name=%r, sent_at=%r, started_at=%r, succeeded_at=%r, failed_at=%r)' % self

    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values'
        return OrderedDict(zip(self._fields, self))

    def _replace(_self, **kwds):
        'Return a new TaskRecord object replacing specified fields with new values'
        result = _self._make(map(kwds.pop, ('name', 'sent_at', 'started_at', 'succeeded_at', 'failed_at'), _self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result

    def __getnewargs__(self):
        'Return self as a plain tuple.  Used by copy and pickle.'
        return tuple(self)

    __dict__ = property(_asdict)

    def __getstate__(self):
        'Exclude the OrderedDict from pickling'
        pass

    name = property(itemgetter(0), doc='Alias for field number 0')

    sent_at = property(itemgetter(1), doc='Alias for field number 1')

    started_at = property(itemgetter(2), doc='Alias for field number 2')

    succeeded_at = property(itemgetter(3), doc='Alias for field number 3')

    failed_at = property(itemgetter(4), doc='Alias for field number 4')

    @property
    def started(self):
        return self.sent_at is not None and self.started_at is not None

    @property
    def wait_duration(self):
        return self.started_at - self.sent_at

    @property
    def finished(self):
        return self.succeeded_at is not None or self.failed_at is not None

    @property
    def successful(self):
        return self.succeeded_at is not None

    @property
    def processing_duration(self):
        return self.succeeded_at - self.started_at
