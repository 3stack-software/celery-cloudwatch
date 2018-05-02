import argparse
import os
import voluptuous as v
import yaml
import six
import logging
import logging.config

from . import TaskMonitor

v_str = v.Any(*six.string_types)

config_schema = v.Schema({
    v.Optional('ccwatch', default={}): v.Schema({
        v.Optional('broker', default=None): v.Any(None, v_str),
        v.Optional('camera', default="celery_cloudwatch.CloudWatchCamera"): v_str,
        v.Optional('verbose', default=False): bool
    }, extra=False),
    v.Optional('camera', default={}): v.Schema({
        v.Optional('frequency', default=60.0): v.Any(int, float),
        v.Optional('verbose', default=False): bool
    }, extra=False),
    v.Optional('cloudwatch-camera', default={}): v.Schema({
        v.Optional('dryrun', default=False): bool,
        v.Optional('namespace', default='celery'): v_str,
        v.Optional('tasks', default=[]): v.Schema([
            v_str, v.Schema({
                'name': v_str,
                'dimensions': v.Schema({
                    v.Extra: v_str
                }, extra=True)
            }, extra=False)
        ]),
        v.Optional('task-groups', default=[]): [
            v.Any(
                v.Schema({
                    'tasks': [v_str],
                    'dimensions': v.Schema({
                        v.Extra: v_str,
                    }),
                }),
                v.Schema({
                    'patterns': [v_str],
                    'dimensions': v.Schema({
                        v.Extra: v_str,
                    }),
                })
            )
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
    parser.add_argument('--logging-config', default='/etc/ccwatch.logging.conf')

    args = parser.parse_args()

    config = {}
    if os.path.isfile(args.config):
        with open(args.config, 'r') as fp:
            config = yaml.load(fp)

    if args.logging_config and os.path.isfile(args.logging_config):
        logging.config.fileConfig(args.logging_config)


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
