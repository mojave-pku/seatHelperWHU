# -*- coding:utf-8 -*-
from monitor import Monitor
from user import User
import datetime
import time,random
import publicFunc as public


class FetchSeatHandler(object):
    def __init__(self):
        self.monitor = Monitor()
        if public.keyExists('error'):
            self.monitor.deleteMon()
        public.setRedis('error', True, expire=100, forever=False)
        self.sleeping = 2

    def _hasEmptySeat(self, roomId, studentNum):
        currentUser = User(studentNum)
        today = str(datetime.date.today())
        userInfo = self.monitor.singleUser(studentNum)
        jsonTree = currentUser.safeJsonTree(
            url='rest/v2/searchSeats/' + today + '/' + userInfo['start'] + '/' + userInfo['end'],
            para={
                '"t': 1,
                'roomId': roomId,
                'buildingId': userInfo['buildingId'],
                'batch': 9999,
                'page': 1,
                't2': '2"'
            },
            isPost=True,
            useToken=True
        )

        results = []
        for key in jsonTree['data']['seats'].keys():
            results.append(jsonTree['data']['seats'][key])

        if len(results) == 0:
            return None
        else:
            return results[0]['id']

    def _submit(self, seatId, studentNum):
        user = User(studentNum)
        userInfo = self.monitor.singleUser(studentNum)
        try:
            user.bookedSeat = {
            'starttime': userInfo['start'],
            'endtime': userInfo['end'],
            'date': self.monitor.date,
            'seatid':seatId
        }
        except IOError:
            return False
        except ValueError:
            print(self.monitor.deleteUser(studentNum, booked=True))
            return False
        else:
            return True

    def run(self):
        while True:
            if self.monitor.sumOfUsersOnRunning < 2:
                self.sleeping_max = 5
                self.sleeping_min = 3
            elif self.monitor.sumOfUsersOnRunning >= 2:
                self.sleeping_max = 5
                self.sleeping_min = 2
            elif self.monitor.sumOfUsersOnRunning >= 4:
                self.sleeping_max = 5
                self.sleeping_min = 1

            for roomId in self.monitor.roomStatus.keys():
                for studentNum in self.monitor.roomStatus[roomId]:
                    seatId = self._hasEmptySeat(roomId, studentNum)
                    if seatId is not None:
                        if self._submit(seatId, studentNum):
                            print(self.monitor.deleteUser(studentNum, success=True))
                    public.incrRedis('d-'+studentNum)
                    print('roomId:'+ roomId + ',StudentNum:'+ studentNum)
                    time.sleep(random.randint(self.sleeping_min, self.sleeping_max))

                if len(self.monitor.roomStatus[roomId]) > 0:
                    time.sleep(random.randint(self.sleeping_min, self.sleeping_max))
            if self.monitor.sumOfUsersOnRunning == 0:
                print('No User.')
                time.sleep(10)


if __name__ == "__main__":
    app = FetchSeatHandler()
    app.run()