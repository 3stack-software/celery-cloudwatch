from __future__ import print_function
from stats import Stats
from camera import Camera


class PrintCamera(Camera):
    clear_after = True

    def on_shutter(self, state):
        print('-----')

        print('Time to Start')
        total = Stats()
        for method_name, stats in state.time_to_start.items():
            print(
                "%s avg:%.2fs, max:%.2fs, min: %.2fs" %
                method_name,
                stats.average() or -1.0,
                stats.maximum or -1.0,
                stats.minimum or -1.0
            )
            total += stats

        print('\nTime to Process')
        total = Stats()
        for method_name, stats in state.time_to_process.items():
            print("%s avg:%.2fs, max:%.2fs, min: %.2fs" %
                  (method_name,
                   stats.average() or -1.0,
                   stats.maximum or -1.0,
                   stats.minimum or -1.0)
            )
            total += stats
        print("Total: avg:%.2fs, max:%.2fs, min: %.2fs" %
              (total.average() or -1.0,
               total.maximum or -1.0,
               total.minimum or -1.0)
        )

        print('\nEvent Totals')
        for method_name, totals in state.totals.items():
            for total_name, total in totals.items():
                print("%s[%s]: %d" % (method_name, total_name, total))

        print('\nQueue Sizes')
        print('Waiting Tasks: %d' % len(state.waiting_tasks))
        print('Running Tasks: %d' % len(state.running_tasks))

        print('')
        print('')

