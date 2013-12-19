__author__ = 'nathan.muir'

from camera import Camera, CameraFactory
import boto.ec2.cloudwatch
import sys, traceback, os
import json

class CloudWatchCameraFactory(CameraFactory):

    def camera(self, state):
        kwargs = {
            'freq': self.frequency,
            'task_names': None,
            'cloud_watch_namespace': 'celery',
            'aws_connection': boto.ec2.cloudwatch.CloudWatchConnection()
        }
        if 'TASK_MONITOR_CW_TASK_NAMES' in os.environ:
            kwargs['task_names'] = [x.strip() for x in os.environ['TASK_MONITOR_CW_TASK_NAMES'].split(',')]

        if 'TASK_MONITOR_CW_NAMESPACE' in os.environ:
            kwargs['cloud_watch_namespace'] = os.environ['TASK_MONITOR_CW_NAMESPACE'].strip()

        if 'TASK_MONITOR_CW_DIMS' in os.environ:
            pass
        return self.c(state, **kwargs)


class CloudWatchCamera(Camera):

    clear_after = True
    _event_names = ('waiting', 'running', 'completed', 'failed')

    def __init__(self, state, aws_connection, freq=1.0, task_names=None, cloud_watch_namespace='celery', base_dimensions=None):
        super(CloudWatchCamera, self).__init__(state, freq=freq)
        self.aws_connection = aws_connection
        self.cloud_watch_namespace = cloud_watch_namespace
        self.base_dimensions = base_dimensions
        if task_names is not None:
            self.task_names = task_names
        else:
            self.task_names = []
        self.metrics = None

    def on_shutter(self, state):
        try:
            self.metrics = self._build_metrics(state)
        except RuntimeError as r:
            print r


    def after_shutter(self):
        try:
            self.metrics.send()
        except:
            print "Exception in user code:"
            print '-'*60
            traceback.print_exc(file=sys.stdout)
        finally:
            self.metrics = None

    def _metric_list(self):
        return MetricList(self.cloud_watch_namespace, self.aws_connection, self.base_dimensions)

    def _build_metrics(self, state):
        metrics = self._metric_list()
        self._add_queue_times(metrics, state.time_to_start)
        self._add_run_times(metrics, state.time_to_process)
        self._add_task_events(metrics, state.totals)
        self._add_waiting_tasks(metrics, len(state.waiting_tasks))
        self._add_running_tasks(metrics, len(state.running_tasks))
        return metrics

    def _add_task_events(self, metrics, event_totals):
        task_events = self._fill_task_events(event_totals)
        for task_name, total_by_event in task_events.items():
            for event_name, total in total_by_event.items():
                metrics.add('CeleryTaskEvent%s' % event_name.capitalize(), unit='Count', value=total, dimensions={'task': task_name})

    def _fill_task_events(self, event_totals):
        task_events = {}
        for task_name in self.task_names:
            task_events[task_name] = dict((en, 0) for en in self._event_names)

        for task_name, totals in event_totals.items():
            if task_name not in task_events:
                task_events[task_name] = dict((en, 0) for en in self._event_names)
            for event_name, total in totals.items():
                task_events[task_name][event_name] = total
        return task_events

    @staticmethod
    def _add_queue_times(metrics, time_to_start):
        for task_name, stats in time_to_start.items():
            metrics.add('CeleryQueuedTime', unit='Seconds', dimensions={'task': task_name}, stats=stats.__dict__.copy())

    @staticmethod
    def _add_run_times(metrics, time_to_process):
        for task_name, stats in time_to_process.items():
            metrics.add('CeleryProcessingTime', unit='Seconds', dimensions={'task': task_name}, stats=stats.__dict__.copy())
    @staticmethod
    def _add_waiting_tasks(metrics, waiting_tasks):
        metrics.add('CeleryQueueSize', unit='Count', value=waiting_tasks, dimensions={'queue': 'celery'})

    @staticmethod
    def _add_running_tasks(metrics, running_tasks):
        metrics.add('CeleryRunningTasks', unit='Count', value=running_tasks, dimensions={'queue': 'celery'})




def xchunk(arr, size):
    for x in xrange(0, len(arr), size):
        yield arr[x:x+size]

class MetricList(object):

    _metric_chunk_size = 20

    def __init__(self, namespace, aws_connection, base_dimensions=None):
        self.metrics = []
        self.namespace = namespace
        self.aws_connection = aws_connection
        self.base_dimensions = base_dimensions

    def add(self, *args, **kwargs):
        self.append(Metric(*args, **kwargs))

    def append(self, metric):
        if self.base_dimensions is not None:
            for key, val in self.base_dimensions.items():
                metric.add_dimension(key, val)
        self.metrics.append(metric)

    def _serialize(self, metric_chunk):
        params = {
            'Namespace': self.namespace
        }
        index = 0
        for metric in metric_chunk:
            for key, val in metric.serialize().iteritems():
                params['MetricData.member.%d.%s' % (index + 1, key)] = val
            index += 1
        return params

    def send(self):
        for metric_chunk in xchunk(self.metrics, self._metric_chunk_size):
            metrics = self._serialize(metric_chunk)
            self.aws_connection.get_status('PutMetricData', metrics, verb="POST")


class Metric(object):

    def __init__(self, name, unit=None, timestamp=None, value=None, stats=None, dimensions=None):
        self.name = name
        self.unit = unit
        self.timestamp = timestamp
        self.value = value
        self.stats = stats
        self.dimensions = dimensions

    def add_dimension(self, key, val):
        if self.dimensions is None:
            self.dimensions = {}
        if key not in self.dimensions:
            self.dimensions[key] = val


    def serialize(self):
        metric_data = {
            'MetricName': self.name,
        }

        if self.timestamp:
            metric_data['Timestamp'] = self.timestamp.isoformat()

        if self.unit:
            metric_data['Unit'] = self.unit

        if self.dimensions:
            self._build_dimension_param(self.dimensions, metric_data)

        if self.stats:
            metric_data['StatisticValues.Maximum'] = self.stats['maximum']
            metric_data['StatisticValues.Minimum'] = self.stats['minimum']
            metric_data['StatisticValues.SampleCount'] = self.stats['samplecount']
            metric_data['StatisticValues.Sum'] = self.stats['sum']
        elif self.value is not None:
            metric_data['Value'] = self.value
        else:
            raise Exception('Must specify a value or statistics to put.')

        return metric_data


    @staticmethod
    def _build_dimension_param(dimensions, params):
        prefix = 'Dimensions.member'
        i = 0
        for dim_name in dimensions:
            dim_value = dimensions[dim_name]
            if dim_value:
                if isinstance(dim_value, basestring):
                    dim_value = [dim_value]
                for value in dim_value:
                    params['%s.%d.Name' % (prefix, i+1)] = dim_name
                    params['%s.%d.Value' % (prefix, i+1)] = value
                    i += 1
            else:
                params['%s.%d.Name' % (prefix, i+1)] = dim_name
                i += 1

    def __repr__(self):
        return '<Metric %s>' % self.name
