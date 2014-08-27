__author__ = 'nathan.muir'


class Stats(object):
    def __init__(self, samplecount=0, total=0.0, minimum=None, maximum=None):
        self.samplecount = samplecount
        self.sum = total
        self.minimum = minimum
        self.maximum = maximum

    def __iadd__(self, value):
        if isinstance(value, Stats):
            self.samplecount += value.samplecount
            self.sum += value.sum
            self._minmax(value.maximum)
            self._minmax(value.minimum)
        else:
            self.samplecount += 1
            self.sum += value
            self._minmax(value)
        return self

    def _minmax(self, value):
        if self.maximum is None or value > self.maximum:
            self.maximum = value
        if self.minimum is None or value < self.minimum:
            self.minimum = value

    def __add__(self, value):
        if isinstance(value, Stats):
            stats = Stats(self.samplecount + value.samplecount,
                          self.sum + value.sum, self.minimum, self.maximum)
            stats._minmax(value.maximum)
            stats._minmax(value.minimum)
        else:
            stats = Stats(self.samplecount, self.sum, self.minimum,
                          self.maximum)
            stats += value
        return stats

    def average(self):
        if self.samplecount == 0:
            return None
        return self.sum / self.samplecount

