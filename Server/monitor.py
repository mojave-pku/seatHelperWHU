# -*- coding:utf-8 -*-
import publicFunc as public
import datetime
from user import User
from wechatpy import WeChatClient


class Monitor(object):
    def __init__(self):
        self.wechat_client = WeChatClient(
            appid='wx3c1ed4db3c5b089b',
            secret='65860300a0c740cb5ca0757cc4b218e2'
        )

    @property
    def date(self):
        return str(datetime.date.today())

    @property
    def _usersOnRunning(self):
        if public.keyExists('_usersOnRunning'):
            return eval(public.getRedis('_usersOnRunning'))
        else:
            return {}

    @_usersOnRunning.setter
    def _usersOnRunning(self, value):
        if type(value) is not dict:
            raise TypeError
        else:
            public.setRedis('_usersOnRunning', value, forever=True)

    def flush(self):
        users = self._users
        for user in users.values():
            now = datetime.datetime.now()
            if user['enableTime'] < now:
                self.activeUser(user['studentNum'])
            if user['expireTime'] < now:
                self.deleteUser(user['studentNum'], success=False)

    def singleUser(self, studentNum):
        if self._users.__contains__(studentNum):
            return self._users[studentNum]
        raise KeyError('No such a user.')

    def _singleUserOnRunning(self, studentNum):
        if self._usersOnRunning.__contains__(studentNum):
            return self._usersOnRunning[studentNum]

    @property
    def roomStatus(self):
        if not public.keyExists('flush'):
            print('flush')
            public.setRedis('flush', True, expire=8, forever=False)
            self.flush()
        if public.keyExists('roomStatus'):
            return eval(public.getRedis('roomStatus'))
        else:
            return {}

    @roomStatus.setter
    def roomStatus(self, value):
        if type(value) is not dict:
            raise TypeError
        public.setRedis('roomStatus', value, forever=True)

    # 获取指定roomId的列表
    def __getitem__(self, roomId):
        return self.roomStatus[str(roomId)]

    @property
    def _users(self):
        if public.keyExists('users'):
            return eval(public.getRedis('users'))
        else:
            return {}

    @_users.setter
    def _users(self, u):
        if type(u) is not dict:
            raise TypeError
        public.setRedis('users', u, forever=True)

    @property
    def sumOfUsersOnRunning(self):
        return len(self._usersOnRunning)

    def addUser(self, studentNum, roomIds, expireTime, start, end, buildingId, formId, stop, enableTime=None):
        if type(studentNum) is not str or type(roomIds) is not list:
            raise TypeError

        enable = enableTime or datetime.datetime.now()
        # 添加_users
        users = self._users
        if users.__contains__(studentNum):
            raise ValueError('User has submitted the request.')
        users[studentNum] = {
            'studentNum': studentNum,
            'roomIds': roomIds,
            'enableTime': enable,
            'expireTime': expireTime,
            'start': start,
            'end': end,
            'buildingId': buildingId,
            'formId': formId,
            'stop': stop
        }

        self._users = users

    def activeUser(self, studentNum):
        # 添加_roomStatus
        if self._usersOnRunning.__contains__(studentNum):
            return

        print('active ' + studentNum)
        usersOnRunning = self._usersOnRunning
        users = self._users

        usersOnRunning[studentNum] = users[studentNum]
        self._usersOnRunning = usersOnRunning

        u = users[studentNum]
        roomIds = u['roomIds']

        roomStatus = self.roomStatus
        for roomId in roomIds:
            try:
                roomStatus[str(roomId)].append(studentNum)
            except KeyError:
                roomStatus[str(roomId)] = []
                roomStatus[str(roomId)].append(studentNum)

        self.roomStatus = roomStatus

    def deleteUser(self, studentNum, success=False, booked=False):
        if type(studentNum) is not str:
            raise TypeError
        users = self._users
        usersOnRunning = self._usersOnRunning
        roomStatus = self.roomStatus
        user = users[studentNum]

        try:
            usersOnRunning.pop(studentNum)
        except KeyError:
            running = False
        else:
            running = True
            self._usersOnRunning = usersOnRunning

        count = 0
        if running:
            if public.keyExists('d-'+studentNum):
                count = public.getRedis('d-'+studentNum)
            else:
                count = 0
            public.deleteRedis('d-'+studentNum)
            for roomId in user['roomIds']:
                try:
                    roomStatus[str(roomId)].remove(studentNum)
                except KeyError:
                    return False
                except ValueError:
                    pass
                else:
                    self.roomStatus = roomStatus

        try:
            users.pop(studentNum)
        except KeyError:
            return False
        else:
            self._users = users

        if success:
            public.incrRedis('detect_num')
            u = User(studentNum)
            booked = u.bookedSeat
            try:
                mess = booked['message'].split('，')
                room = mess[0]
                seatNum = mess[1][3:]
            except Exception:
                room = booked
                seatNum = '-'

            data = {
                "keyword1": {
                    "value": room
                },
                "keyword2": {
                    "value": booked['time']
                },
                "keyword3": {
                    "value": seatNum,
                    "color": "#FF6666"
                },
                "keyword4": {
                    "value": int(count)
                },

            }
            code = public.pushMessage(
                access_token=self.wechat_client.access_token,
                openid=u.openid,
                form_id=user['formId'],
                data=data,
                method='detect'
            )
            return code
        if booked:
            u = User(studentNum)
            data = {
                "keyword1": {
                    "value": '已有预约',
                    "color": "#FF6666"
                },
                "keyword2": {
                    "value": '您可能已具有一个预约，请登录小程序查看。若无预约，请到用户群报告异常。'
                }
            }
            code = public.pushMessage(
                access_token=self.wechat_client.access_token,
                openid=u.openid,
                form_id=user['formId'],
                data=data,
                method='delete_mon'
            )
            print(code)
            return code
        return True

    def deleteMon(self):
        data = {
            'service_name': {
                'value': '余座监控'
            },
            'reason': {
                'value': '脚本异常'
            },
            'mess': {
                'value': '【严重】全流水线清空'
            }
        }
        public.pushRunningMessage('warn', data)
        for studentNum in self._users.keys():
            user = User(studentNum)
            data = {
                "keyword1": {
                    "value": '脚本异常',
                    "color": "#FF6666"
                },
                "keyword2": {
                    "value": '请及时重新提交监控请求，并麻烦您在用户群报告异常。'
                }
            }
            code = public.pushMessage(
                access_token=self.wechat_client.access_token,
                openid=user.openid,
                form_id=self._users[studentNum]['formId'],
                data=data,
                method='delete_mon'
            )
            print(code)

        self._users = {}
        self.roomStatus = {}
        self._usersOnRunning = {}





if __name__ == "__main__":
    m = Monitor()
    expire = datetime.datetime.combine(datetime.date.today(), datetime.time(23, 50, 0))
    start = datetime.datetime.combine(datetime.date.today(), datetime.time(11, 50, 0))
    # m.flush()
    # m.addUser("2014301220099", [8,9,10,11], expireTime=expire, start='840', end='1320', buildingId='1',formId='0',stop='13:00', enableTime=start)
    # m.activeUser('2014301220099')
    # m.deleteUser('2014301220099',False)
    # m.addUser("2014301220011", [11, 17], expireTime=expire)
    # public.setRedis('flush', True, expire=10, forever=False)
    print(public.keyExists('flush'))
    print(m._users)
    print(m.roomStatus)
    print(m._usersOnRunning)
    # m.roomStatus = {}
    # m._usersOnRunning = {}
    # print(m.deleteUser('2014301220099'))
    # for room in m.roomStatus.keys():
    #     print(room)
    #     users = m.roomStatus[room]
    #     print(users)



