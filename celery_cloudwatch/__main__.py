import argparse
import os
import voluptuous as v
import yaml
import six

from . import TaskMonitor


config_schema = v.Schema({
    v.Optional('ccwatch', default={}): v.Schema({
        v.Optional('broker', default=None): v.Any(None, six.binary_type),
        v.Optional('camera', default="celery_cloudwatch.CloudWatchCamera"): v.Any(str, six.binary_type),
        v.Optional('verbose', default=False): bool
    }, extra=False),
    v.Optional('camera', default={}): v.Schema({
        v.Optional('frequency', default=60.0): v.Any(int, float),
        v.Optional('verbose', default=False): bool
    }, extra=False),
    v.Optional('cloudwatch-camera', default={}): v.Schema({
        v.Optional('dryrun', default=False): bool,
        v.Optional('namespace', default='celery'): six.binary_type,
        v.Optional('tasks', default=[]): v.Schema([
            six.binary_type, v.Schema({
                'name': six.binary_type,
                'dimensions': v.Schema({
                    v.Extra: six.binary_type
                }, extra=True)
            }, extra=False)
        ]),
        v.Optional('task-groups', default=[]): [
            v.Schema({
                'tasks': [six.binary_type],
                'dimensions': v.Schema({
                    v.Extra: six.binary_type
                })
            })
        ],
    }, extra=False)
}, extra=True)


def main():
    parser = argparse.ArgumentParser(description="Monitors Celery Task Events and provides statistics", usage='celery_cloudwatch [options]')
    parser.add_argument('-b', '--broker', default=None, help='''url to broker. default is 'amqp://guest@localhost//' ''')
    parser.add_argument('-F', '--frequency', '--freq', type=float, default=None)
    parser.add_argument('--camera', default=None)
    parser.add_argument('--print', action='store_const', const='celery_cloudwatch.PrintCamera', dest='camera', default=None)

    parser.add_argument('-c', '--config', default='/etc/ccwatch.yaml')

    args = parser.parse_args()

    config = {}
    if os.path.isfile(args.config):
        with open(args.config, 'r') as fp:
            config = yaml.load(fp)

    # voluptuous doesn't validate that `default=` values match the schema
    #  lets just run it through twice, to make sure everything is set.
    config = config_schema(config_schema(config))
    config_ccwatch = config['ccwatch']
    options = {
        'broker': config_ccwatch.get('broker'),
        'camera': config_ccwatch.get('camera'),
        'verbose': config_ccwatch.get('verbose'),
        'config': config
    }

    monitor = TaskMonitor(**options)
    monitor.run()

if __name__ == '__main__':
    main()
