import argparse

class Options:
    parser = None
    def __init__(self):
        self.parser = self._init_parser()

    def _init_parser(self):
        parser = argparse.ArgumentParser(description="Monitors Celery Task Events and provides statistics", usage='bin/task_monitor [options]')

        parser.add_argument('-b', '--broker', default=None, help='''url to broker. default is 'amqp://guest@localhost//' ''')
        parser.add_argument('-F', '--frequency', '--freq', type=float, default=60.0)
        parser.add_argument('-c', '--camera', default='lib.PrintCamera')
        parser.add_argument('-q', nargs='+', type=str, dest='queues', default='celery', help='Queues to monitor')
        parser.add_argument('--factory')
        parser.set_defaults(blur=True)
        return parser

    def parse(self, args=None):
        return self.parser.parse_args(args)
