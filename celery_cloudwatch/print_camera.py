

from stats import Stats
from camera import Camera


class PrintCamera(Camera):
    clear_after = True

    def on_shutter(self, state):
        print '-----'

        print 'Time to Start'
        total = Stats()
        for method_name, stats in state.time_to_start.items():
            print "%s avg:%.2fs, max:%.2fs, min: %.2fs" % (method_name, stats.average() or -1.0 , stats.maximum or -1.0, stats.minimum or -1.0)
            total += stats

        print ''
        print 'Time to Process'
        total = Stats()
        for method_name, stats in state.time_to_process.items():
            print "%s avg:%.2fs, max:%.2fs, min: %.2fs" % (method_name, stats.average() or -1.0, stats.maximum or -1.0, stats.minimum or -1.0)
            total += stats
        print "Total: avg:%.2fs, max:%.2fs, min: %.2fs" % (total.average() or -1.0, total.maximum or -1.0, total.minimum or -1.0)

        print ''
        print 'Event Totals'
        methods = set(state.task_event_waiting.keys() + state.task_event_running.keys() +
                      state.task_event_completed.keys() + state.task_event_failed.keys())
        for method_name in methods:
            if method_name in state.task_event_waiting:
                print "%s[%s]: %d" % (method_name, 'waiting', state.task_event_waiting[method_name])
            if method_name in state.task_event_running:
                print "%s[%s]: %d" % (method_name, 'running', state.task_event_running[method_name])
            if method_name in state.task_event_completed:
                print "%s[%s]: %d" % (method_name, 'completed', state.task_event_completed[method_name])
            if method_name in state.task_event_failed:
                print "%s[%s]: %d" % (method_name, 'failed', state.task_event_failed[method_name])

        print ''
        print 'Queue Sizes'
        print 'Waiting Tasks: %d' % len(state.waiting_tasks)
        print 'Running Tasks: %d' % len(state.running_tasks)

        print ''
        print ''

