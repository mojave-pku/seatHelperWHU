import datetime, time, json ,ssl
from dbManager.sql import SQLManager
from user import User
import random

class PrePareSystem(object):
    def __init__(self, debug_date=None):
        self.submit_url = "https://service-bjaz4azq-1251794097.ap-guangzhou.apigateway.myqcloud.com"
        ssl._create_default_https_context = ssl._create_unverified_context
        self.date = debug_date or \
                    str(datetime.date.today() + datetime.timedelta(days=1))

        self.delay = 0.4
        with SQLManager() as conn:
            results = conn.select(
                table='prog_book',
                info=['studentnum', 'starttime', 'endtime', 'formid'],
                args={
                    'timestamp': self.date
                }
            )

        self.book_records = []
        for result in results:
            with SQLManager() as conn:
                passwd = conn.select(
                    table='prog_user',
                    info=['passwd'],
                    args={
                        'studentnum':result[0]
                    }
                )[0][0]

            with SQLManager() as conn:
                seats = conn.select(
                    table='prog_seat',
                    info=['loc', 'build', 'seatid'],
                    args={
                        'studentnum': result[0]
                    },
                    orderBy= 'level'
                )

            seats_formed = []
            for seat in seats:
                seat_formed = {
                    'location': seat[0],
                    'building': seat[1],
                    'seat_id': seat[2]
                }
                seats_formed.append(seat_formed)

            record = {
                'student_num': result[0],
                'passwd': passwd,
                'start_time': result[1],
                'end_time': result[2],
                'form_id': result[3],
                'seats': seats_formed
            }

            self.book_records.append(record)

    def flush_token(self):
        # 刷新token缓存
        token = None
        for record in self.book_records:
            time.sleep(random.randint(2,6))
            token = User(record['student_num'], record['passwd']).login()
        return token or False

    def prepare_data(self, ignore_wait=False):
        if len(self.book_records) == 0:
            return
        else:
            self.flush_token()
            records = []
            count = 0
            for i in range(0, 3):
                for record in self.book_records:
                    user = User(
                        studentNum=record['student_num'],
                        passwd=record['passwd']
                    )
                    try:
                        params = {
                            "startTime": record['start_time'],
                            "endTime": record['end_time'],
                            "seat": record['seats'][i]['seat_id'],
                            "date": self.date,
                            't': 1,
                            'ip_restrict': 'true',
                            't2': 2
                        }
                        push = {
                            'token': user.token,
                            'student_num': user.studentNum,
                            'passwd': user.passwd,
                            'location': record['seats'][i]['location'],
                            'building': record['seats'][i]['building'],
                            'form_id': record['form_id'],
                            "startTime": record['start_time'],
                            "endTime": record['end_time'],
                            "delay": count * self.delay
                        }
                        print(params, push)
                        count = count + 1
                    except IndexError:
                        pass
                    else:
                        records.append({
                            'params': params,
                            'push': push
                        })
            print('Data has prepered.')

            with open(self.date + '.txt', 'w') as f:
                f.write(json.dumps(records))

p = PrePareSystem()
print(p.date)
p.prepare_data()

