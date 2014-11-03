__author__ = 'nathan.muir'

import argparse
import os
import io
import ConfigParser
from . import TaskMonitor

default_config = """
[ccwatch]
broker
camera = celery_cloudwatch.CloudWatchCamera
; if verbose - will print each task-sent, task-started, task-succeeded, and task-failed event
verbose = False

[camera]
frequency = 60.0
; if verbose - will print out data
verbose = False

[cloudwatch-camera]
; uncomment the following line, to "dry" test without connecting to aws
; noaws
namespace = celery
; provide a list of tasks
tasks =
queues = celery


[cloudwatch-camera-dimensions]
; additional dimensions to send through with each metric
; eg.
; app = myapp
"""

def main():
    parser = argparse.ArgumentParser(description="Monitors Celery Task Events and provides statistics", usage='celery_cloudwatch [options]')
    parser.add_argument('-b', '--broker', default=None, help='''url to broker. default is 'amqp://guest@localhost//' ''')
    parser.add_argument('-F', '--frequency', '--freq', type=float, default=None)
    parser.add_argument('--camera', default=None)
    parser.add_argument('--print', action='store_const', const='celery_cloudwatch.PrintCamera', dest='camera', default=None)

    parser.add_argument('-c', '--config', default='/etc/ccwatch.cfg')

    args = parser.parse_args()

    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.readfp(io.BytesIO(default_config))
    if os.path.isfile(args.config):
        with open(args.config, 'r') as fp:
            config.readfp(fp)

    for optname in ['broker', 'camera']:
        value = getattr(args, optname)
        if value is not None:
            config.set('ccwatch', optname, value)
    for optname in ['frequency']:
        value = getattr(args, optname)
        if value is not None:
            config.set('camera', optname, value)

    options = {
        'broker': config.get('ccwatch', 'broker'),
        'camera': config.get('ccwatch', 'camera'),
        'verbose': config.getboolean('ccwatch', 'verbose'),
        'config': config
    }

    monitor = TaskMonitor(**options)
    monitor.run()

if __name__ == '__main__':
    main()
