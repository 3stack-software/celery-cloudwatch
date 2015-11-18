from celery import Celery
from state import State
from camera import CameraFactory

from pprint import PrettyPrinter
pp = PrettyPrinter()


def noop(x):
    pass


class TaskMonitor(object):

    def __init__(self, broker=None, camera='celery_cloudwatch.PrintCamera',
                 verbose=False, config=None):
        self.broker = broker
        self.camera = camera
        self.verbose = verbose
        self.config = config

    def run(self):
        app = Celery(broker=self.broker)
        state = State()

        factory = CameraFactory(self.camera)
        camera = factory.camera(state, self.config)

        with app.connection() as connection:
            camera.install()
            recv = app.events.Receiver(connection, handlers={
                'task-sent': self.proxy_event('task-sent',state.task_sent),
                'task-started': self.proxy_event('task-started', state.task_started),
                'task-succeeded': self.proxy_event('task-succeeded', state.task_succeeded),
                'task-failed': self.proxy_event('task-failed', state.task_failed)
            })
            try:
                recv.capture(limit=None, timeout=None, wakeup=False)
            except KeyboardInterrupt:
                raise SystemExit
            finally:
                camera.cancel()

    def proxy_event(self, event_name, fn):
        if not self.verbose:
           return fn
        else:
            def proxy_event_fn(event):
                print '[{}] - {}'.format(event_name, pp.pformat(event))
                return fn(event)
            return proxy_event_fn
