import publicFunc as public
from dbManager.sql import SQLManager
import datetime


class Report(object):
    def __init__(self):
        self.today = str(datetime.date.today())
        self.tomorrow = str(datetime.date.today() + datetime.timedelta(days=1))
        self.book_sum = self._book_sum
        try:
            self.book_rate = '%.2f%%' % ((1 - self.getProperty('book_failed') / self.book_sum) * 100)
        except ZeroDivisionError:
            self.book_rate = '-'

    @property
    def _book_sum(self):
        with SQLManager() as conn:
            results = conn.select(
                table='prog_book',
                info=['studentnum', 'starttime', 'endtime', 'formid'],
                args={
                    'timestamp': str(datetime.date.today() + datetime.timedelta(days=1))
                }
            )
        try:
            book_sum = len(results)
        except TypeError:
            book_sum = 0

        return book_sum

    def getProperty(self, name):
        if public.keyExists(name):
            return int(public.getRedis(name))
        else:
            return 0

    def writeRecord(self):
        with SQLManager() as conn:
            conn.add(
                table='report',
                args={
                    'date': self.today,
                    'book_sum': self.book_sum,
                    'book_failed': self.getProperty('book_failed'),
                    'monitor_num': self.getProperty('monitor_num'),
                    'detect_num': self.getProperty('detect_num'),
                    'mod_num': self.getProperty('mod_num')
                }
            )
        self.clearRecord()

    def clearRecord(self):
        public.setRedis('mod_num', 0, forever=True)
        public.setRedis('detect_num', 0, forever=True)
        public.setRedis('monitor_num', 0, forever=True)

    def run(self):
        data = {
            'date': {
                'value': self.today
            },
            'time': {
                'value': '全天'
            },
            'booked_sum': {
                'value': self.book_sum
            },
            'booked_success': {
                'value': self.book_sum - self.getProperty('book_failed')
            },
            'booked_rate': {
                'value':self.book_rate
            },
            'mod_num': {
                'value': self.getProperty('mod_num')
            },
            'detect_num': {
                'value': self.getProperty('detect_num')
            },
            'mon_num': {
                'value': self.getProperty('monitor_num')
            }

        }

        # print(data)
        public.pushRunningMessage('report', data)


if __name__ == '__main__':
    r = Report()
    r.run()
    # r.writeRecord()