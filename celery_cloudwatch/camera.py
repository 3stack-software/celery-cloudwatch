from celery.utils.timer2 import Timer
from celery.utils.dispatch import Signal

from import_class import import_class


class CameraFactory(object):

    def __init__(self, class_name):
        self.c = import_class(class_name)

    def camera(self, state, config):
        return self.c(state, config)


class Camera(object):
    clear_after = False
    _tref = None
    shutter_signal = Signal(providing_args=('state', ))

    def __init__(self, state, config):
        self.state = state
        self.timer = Timer()
        self.freq = config['camera']['frequency']

    def install(self):
        self._tref = self.timer.call_repeatedly(self.freq, self.capture)

    def on_shutter(self, monitor):
        pass

    def after_shutter(self):
        pass

    def capture(self):
        self.state.freeze_while(self.shutter, clear_after=self.clear_after)
        self.after_shutter()

    def shutter(self):
        self.shutter_signal.send(self.state)
        self.on_shutter(self.state)

    def cancel(self):
        if self._tref:
            self._tref()  # flush all received events.
            self._tref.cancel()

    def __enter__(self):
        self.install()
        return self

    def __exit__(self, *exc_info):
        self.cancel()
        return True
