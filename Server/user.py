# -*- coding:utf-8 -*-

from dbManager.sql import SQLManager
from publicFunc import *
import time, datetime


class User(object):
    def __init__(self, studentNum, passwd=None):
        self.studentNum = studentNum
        self.passwd = passwd or self.savedPasswd
        self.libWebSite = "http://seat.lib.whu.edu.cn/"
        self.publicRate = 1.0

    @property
    def savedPasswd(self):
        with SQLManager() as conn:
            passwd = conn.select(
                table='prog_user',
                info=['passwd'],
                args={
                    'studentnum': self.studentNum
                }
            )[0][0]

        return passwd
    def login(self):
        # 需要处理ValueError（用户名密码错误）
        jsonTree = getJsonTree(self.libWebSite + "rest/auth", {
            'username': self.studentNum,
            'password': self.passwd
        })
        token = jsonTree['data']['token']
        setRedis(self.studentNum, token)
        return str(token)

    def safeJsonTree(self, url, para={}, isPost=False, urlPara=None, useToken=False):
        # 除了Login方法以外，其他方法须调用此方法获取json解析树，否则可能出现异常
        if useToken:
            token = self.token
        else:
            token = None
        try:
            if isPost:
                jsonTree = getJsonTree(self.libWebSite + url, para, isPost=True, urlData=urlPara, token=token)
            else:
                jsonTree = getJsonTree(self.libWebSite + url, para, urlData=urlPara, token=token)
        except ValueError:
            deleteRedis(self.studentNum)
            token = self.token
            if isPost:
                jsonTree = getJsonTree(self.libWebSite + url, para, isPost=True, urlData=urlPara, token=token)
            else:
                jsonTree = getJsonTree(self.libWebSite + url, para, urlData=urlPara, token=token)
        return jsonTree

    @property
    def token(self):
        if keyExists(self.studentNum):
            return str(getRedis(self.studentNum), encoding = "utf-8")
        else:
            return self.login()

    @property
    def preferedSeat(self):
        info = ['level', 'loc']
        args = {
            'studentnum': self.studentNum
        }
        with SQLManager() as conn:
            result = conn.select(
                table='prog_seat',
                info=info,
                args=args
            )

        prefered = {}
        message = ''
        try:
            for record in result:
                prefered['seat' + str(record[0])] = record[1]
                message = message + str(record[0]) + u'、' + record[1] + '\n'
            prefered['message'] = message
        except TypeError:
            prefered['message'] = '无'
            return prefered
        return prefered

    @preferedSeat.setter
    def preferedSeat(self, value):
        if not isinstance(value, dict):
            raise TypeError('preferedSeat should be dict.')
        roomId = value['roomid']
        seatNum = value['seatnum']
        jsonTree = self.safeJsonTree(
            url="rest/v2/room/layoutByDate/" + str(roomId) + "/" + str(datetime.date.today()),
            useToken=True
        )

        find = False
        for key, seat in jsonTree['data']['layout'].items():
            try:
                name = seat['name']
                seatId = str(seat['id'])
            except KeyError:
                pass
            else:
                if seatNum == name:
                    find = True
                    break

        if not find:
            raise ValueError("Can't match given seat.")

        with SQLManager() as conn:
            conn.add(
                table='prog_seat',
                args={
                    'studentnum': self.studentNum,
                    'loc': value['room'] + ',' + value['seatnum'],
                    'level': value['level'],
                    'build': value['building'],
                    'seatid': seatId
                }
            )

    @property
    def bookedSeat(self):
        # if time.localtime().tm_hour >= 23 or time.localtime().tm_hour < 1:
        #     raise ValueError("Server closed.")

        jsonTree = self.safeJsonTree(
            url="rest/v2/user/reservations",
            useToken=True
        )

        records = jsonTree['data']
        if records is None:
            return {
                'message': "当前无预约信息",
                'booked': False
            }
        else:
            record = records[0]
            return {
                'time': record['begin'] + '~' + record['end'],
                'beginTime': record['begin'],
                'endTime': record['end'],
                'seatId': str(record['seatId']),
                'message': record['location'],
                'period': record['begin'] + '~' + record['end'],
                'booked': True
            }

    @bookedSeat.setter
    def bookedSeat(self, value):
        if not isinstance(value, dict):
            raise TypeError()

        jsonTree = self.safeJsonTree(
            url="rest/v2/freeBook",
            para={
                "startTime": value['starttime'],
                "endTime": value['endtime'],
                "seat": value['seatid'],
                "date": value['date']
            },
            isPost=True,
            useToken=True
        )

        print(jsonTree)

        if jsonTree['status'] != 'success':
            raise IOError(jsonTree)

    @bookedSeat.deleter
    def bookedSeat(self):
        jsonTree = self.safeJsonTree(
            url="rest/v2/history/1/10",
            useToken=True
        )
        for record in jsonTree['data']['reservations']:
            if record['stat'] == "RESERVE" :
                secondJsonTree = self.safeJsonTree(
                    url="rest/v2/cancel/" + str(record['id']),
                    useToken=True
                )
                if secondJsonTree['status'] != 'success':
                    raise IOError("failed to cancel.")

            if record['stat'] == "CHECK_IN" or record['stat'] == "AWAY":
                secondJsonTree = self.safeJsonTree(
                    url="rest/v2/stop",
                    useToken=True
                )
                if secondJsonTree['status'] != 'success':
                    raise IOError("failed to stop.")

    @property
    def inStatus(self):
        # if time.localtime().tm_hour >= 23 or time.localtime().tm_hour < 1:
        #     raise ValueError('Server closed.')

        jsonTree = self.safeJsonTree(
            url="rest/v2/user",
            useToken=True
        )

        return jsonTree['data']

    def timetrans(self, st):
        num = int(st)
        hour = int(num / 60)
        minute = num % 60
        if minute == 0:
            return str(hour) + ':00'
        else:
            return str(hour) + ':' + str(minute)

    @property
    def bookedPeriod(self):
        info = ['starttime', 'endtime']
        args = {
            'studentnum': self.studentNum,
            'timestamp': str(datetime.date.today() + datetime.timedelta(days=1))
        }
        with SQLManager() as conn:
            result = conn.select(
                table='prog_book',
                info=info,
                args=args,
                size=1
            )

        if result is not False:
            return {
                'status': True,
                'message': '已预约明日时段：'
                           + self.timetrans(result[0][0])
                           + '~' + self.timetrans(result[0][1]),
                'starttime': result[0][0],
                'endtime': result[0][1]
            }
        else:
            return {
                'status': False,
                'message': '未预约明日时段。'
            }

    @bookedPeriod.setter
    def bookedPeriod(self, value):
        if not isinstance(value, dict):
            raise TypeError()
        today = datetime.date.today()
        tomorrow = str(today + datetime.timedelta(days=1))
        with SQLManager() as conn:
            conn.add(
                table='prog_book',
                args={
                    'studentnum': self.studentNum,
                    'starttime': value['starttime'],
                    'endtime': value['endtime'],
                    'timestamp': tomorrow,
                    'formid': value['formid']
                }
            )

    @bookedPeriod.deleter
    def bookedPeriod(self):
        today = datetime.date.today()
        tomorrow = str(today + datetime.timedelta(days=1))
        with SQLManager() as conn:
            conn.delete(
                table='prog_book',
                args={
                    'studentnum': self.studentNum,
                    'timestamp': tomorrow
                }
            )

    @property
    def isAccessable(self):
        with SQLManager() as conn:
            result = conn.select(
                table='prog_user',
                info=['studentnum'],
                args={
                    'studentnum': self.studentNum
                }
            )

        if result == False:
            return False
        else:
            return True

    @property
    def isCorrect(self):
        try:
            self.login()
        except ValueError:
            return False
        else:
            return True

    def getOpenid(self, jsCode):
        wechatUrl = 'https://api.weixin.qq.com/sns/jscode2session'
        para = {
            'appid': 'wx3c1ed4db3c5b089b',
            'secret': '65860300a0c740cb5ca0757cc4b218e2',
            'js_code': jsCode,
            'grant_type': 'authorization_code'
        }

        jsonTree = getJsonTree(wechatUrl, para, isLib=False)

        with SQLManager() as conn:
            conn.update(
                table='prog_user',
                modArgs={
                    'openid': jsonTree['openid']
                },
                selectArgs={
                    'studentnum': self.studentNum
                }
            )

    def setPasswd(self):
        with SQLManager() as conn:
            conn.update(
                table='prog_user',
                modArgs={
                    'passwd': self.passwd
                },
                selectArgs={
                    'studentnum': self.studentNum
                }
            )

    @property
    def openid(self):
        with SQLManager() as conn:
            result = conn.select(
                table='prog_user',
                info=['openid'],
                args={
                    'studentnum': self.studentNum
                }
            )
        return result[0][0]

    def submitAccess(self, name, reason):
        with SQLManager() as conn:
            conn.add(
                table='prog_apply',
                args={
                    'studentnum': self.studentNum,
                    'name': name,
                    'reason': reason
                }
            )

    @property
    def recommend(self):
        with SQLManager() as conn:
            result = conn.select(
                table='prog_user',
                info=['recommend'],
                args={
                    'studentnum': self.studentNum
                }
            )
        return result[0][0]

    @recommend.setter
    def recommend(self, value):
        with SQLManager() as conn:
            conn.update(
                table='prog_user',
                modArgs={
                    'recommend': value
                },
                selectArgs={
                    'studentnum': self.studentNum
                }
            )




