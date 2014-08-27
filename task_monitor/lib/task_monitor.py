__author__ = 'nathan.muir'
from celery import Celery

from state import State
from import_class import import_class
from camera import CameraFactory


class TaskMonitor(object):
    def __init__(self, options):
        self.options = options

    def run(self):
        app = Celery(broker=self.options.broker)
        state = State()

        if self.options.factory is None:
            factory = CameraFactory(self.options.camera)
        else:
            CustomCameraFactory = import_class(self.options.factory)
            factory = CustomCameraFactory(self.options.camera)
        factory.frequency = self.options.frequency
        camera = factory.camera(state)

        with app.connection() as connection:
            camera.install()
            recv = app.events.Receiver(connection, handlers={
                'task-sent': state.task_sent,
                'task-started': state.task_started,
                'task-succeeded': state.task_succeeded,
                'task-failed': state.task_failed

            })
            try:
                recv.capture(limit=None, timeout=None, wakeup=False)
            except KeyboardInterrupt:
                raise SystemExit
            finally:
                camera.cancel()

