# -*- coding:utf-8 -*-
from flask import Flask, request
from wechatpy import WeChatClient
import json, datetime, os, time
from user import User
from selector import Selector
from monitor import Monitor
from dbManager.sql import SQLManager
from publicFunc import *

from config import Configure

app = Flask(__name__)

wechat_client = WeChatClient(
    appid='wx3c1ed4db3c5b089b',
    secret='65860300a0c740cb5ca0757cc4b218e2'
)


@app.route("/v4", methods=['POST'])
def mainHandler():
    data = request.data.decode("utf-8")
    inputJsonTree = json.loads(data)
    user = User(inputJsonTree['studentNum'], inputJsonTree['passwd'])
    conf = Configure()
    if inputJsonTree['method'] == 'mainPage':
        returnMessage = dict()

        returnMessage['notSupport'] = False

        returnMessage['news'] = '''[01-07]为帮助大家早起学习，1月8日起，上午10点前不再提供修改时段服务。
        免责声明：近期图书馆开始打击外挂脚本，如果你继续使用小程序，代表你知悉可能封号风险，开发者不对封号的可能性做出任何承诺。
        [12-11]近期图书馆开始清查外挂，请及时加入座位助手用户群，关注最新动态，群号码：451417382'''

        returnMessage['serverVersion'] = '4.7.0-01.09'

        returnMessage['recommend'] = user.recommend

        if user.studentNum == '2014301220099':
            configure = conf.getStatus()
        else:
            configure = False
        returnMessage['conf'] = configure

        returnMessage['bannerColor'] = conf.bannerColor
        returnMessage['title'] = conf.title

        return json.dumps(returnMessage)

    if inputJsonTree['method'] == 'tomorrowMessage':
        returnMessage = dict()

        returnMessage['news'] = '''本页功能导引：
                预约：可预约次日的图书馆座位，系统将于22:10锁定此页信息，22:15执行选座指令，22:17前推送选座结果。
                常用座位：执行选座指令时，将按顺序依次提交常用座位的预约请求。为保证成功率，请设置三个且不相同的座位。
                服务时间：0:00~22:10
                '''
        returnMessage['bookedPeriod'] = user.bookedPeriod
        returnMessage['preferredSeat'] = user.preferedSeat

        if conf.tomorrow:
            lock_time = datetime.datetime.combine(datetime.date.today(), datetime.time(22, 10, 00))
            now = datetime.datetime.now()
            if lock_time > now:
                returnMessage['service_status'] = True

            else:
                returnMessage['service_status'] = False
                returnMessage['title'] = '预约信息已锁定'
        else:
            returnMessage['service_status'] = False
            returnMessage['title'] = conf.message

        return json.dumps(returnMessage)

    if inputJsonTree['method'] == 'meMessage':
        start = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 10, 0))
        end = datetime.datetime.combine(datetime.date.today(), datetime.time(23, 50, 0))
        now = datetime.datetime.now()
        returnMessage = dict()

        returnMessage['news'] = '''本页功能导引：
        修改时段：当天有一个可用预约时，可以点击"座位"卡片右上角的"修改时段"对预约时段进行修改。
        取消：当天有一个可用预约时，可以点击"座位"卡片右上角的"取消"按钮取消当前预约。
        服务时间：10:00~21:30
        '''
        returnMessage['recommend'] = user.recommend

        if conf.me:
            if start < now < end:
                adapt_night = datetime.datetime.combine(datetime.date.today(), datetime.time(21, 30, 0))
                adapt_morn = datetime.datetime.combine(datetime.date.today(), datetime.time(1, 0, 0))
                if now > adapt_night or now < adapt_morn:
                    returnMessage['notAdaptable'] = True
                else:
                    returnMessage['notAdaptable'] = False
                try:
                    returnMessage['inStatus'] = user.inStatus
                    returnMessage['bookedSeat'] = user.bookedSeat
                    returnMessage['service_status'] = True
                except ZeroDivisionError:
                    returnMessage['service_status'] = False
                    returnMessage['message'] = '图书馆服务器维护中'
            else:
                returnMessage['service_status'] = False
                returnMessage['message'] = '23:50~00:10期间暂停此项服务'
        else:
            returnMessage['service_status'] = False
            returnMessage['message'] = conf.message

        return json.dumps(returnMessage)

    if inputJsonTree['method'] == 'login':
        user.getOpenid(inputJsonTree['jscode'])
        user.setPasswd()
        try:
            return json.dumps({
                'isCorrect': user.isCorrect,
                'isAccessible': user.isAccessable,
                'inStatus': user.inStatus
            })
        except ValueError:
            return json.dumps({
                'isCorrect': False,
                'isAccessible': user.isAccessable,
                'message': '用户名密码错误'
            })

    if inputJsonTree['method'] == 'access':
        user.submitAccess(inputJsonTree['name'], inputJsonTree['reason'])
        return json.dumps({
            'status': True
        })

    if inputJsonTree['method'] == 'addSeats':
        if inputJsonTree['step'] == 'getBuildings':
            selector = Selector(user)

            return json.dumps({
                'status': True,
                'buildings': selector.buildings
            })

        if inputJsonTree['step'] == 'getRooms':
            buildingId = inputJsonTree['building']
            selector = Selector(user)

            return json.dumps({
                'status': True,
                'rooms': selector.getRooms(buildingId)
            })

        if inputJsonTree['step'] == 'submit':
            try:
                user.preferedSeat = inputJsonTree
            except ValueError:
                return json.dumps({
                    'status': False,
                    'message': '未匹配座位，请确认输入的座位号合法，且为三位。如039'
                })
            else:
                return json.dumps({
                    'status': True,
                    'message': '添加成功'
                })

    if inputJsonTree['method'] == 'book':
        if inputJsonTree['step'] == 'create':
            message = '提交成功，考试周期间预期预约成功率约70%，请尽量避开热门座位，请务必确认您已经在下方添加了3个常用座位。晚上22:12~22:16期间请勿使用手机客户端选座，以免产生冲突。'
            if len(inputJsonTree['starttime']) < 1 or len(inputJsonTree['endtime']) < 1:
                return json.dumps({
                    'status': False,
                    'message': '未指定起止时间，请确定选好起止时间后再提交。'
                })
            user.bookedPeriod = inputJsonTree
            today = datetime.datetime.now()
            if today.weekday() == 2:
                return json.dumps({
                    'status': True,
                    'message': '明天是周四，部分区域闭馆，请确认您的常用座位为不闭馆区域。' + message
                })
            else:
                return json.dumps({
                    'status': True,
                    'message': message
                })

        if inputJsonTree['step'] == 'delete':
            del user.bookedPeriod
            return json.dumps({
                'status': True,
                'message': '取消成功'
            })

    if inputJsonTree['method'] == 'keep':
        incrRedis('mod_num')
        if inputJsonTree['step'] == 'delete':
            try:
                del user.bookedSeat
            except IOError:
                return json.dumps({
                    'status': False,
                    'message': "通信异常"
                })
            else:
                return json.dumps({
                    'status': True,
                    'message': "取消成功"
                })

        if inputJsonTree['step'] == 'change':
            inputJsonTree['seatid'] = user.bookedSeat['seatId']
            inputJsonTree['date'] = str(datetime.date.today())
            try:
                del user.bookedSeat
                user.bookedSeat = inputJsonTree
            except IOError:
                return json.dumps({
                    'status': False,
                    'message': "通信异常"
                })
            else:
                time.sleep(0.5)
                booked = user.bookedSeat
                try:
                    mess = booked['message'].split('，')
                    room = mess[0]
                    seatNum = mess[1][3:]
                except Exception:
                    room = booked
                    seatNum = '-'

                code = pushMessage(
                    access_token=wechat_client.access_token,
                    openid=user.openid,
                    form_id=inputJsonTree['formid'],
                    data={
                        "keyword1": {
                            "value": room,
                        },
                        "keyword2": {
                            "value": seatNum,
                            "color": "#FF6666"
                        },
                        "keyword3": {
                            "value": user.timetrans(inputJsonTree['starttime'])
                                     + '~' + user.timetrans(inputJsonTree['endtime'])
                        }
                    },
                    method='keep'
                )
                return json.dumps({
                    'status': True,
                    'message': "修改成功, code:" + str(code)
                })

    if inputJsonTree['method'] == 'detect':
        returnMessage = dict()
        returnMessage['news'] = '''本页功能导引：
        余座监控：可选定时间、房间，由服务器监控相应时间、房间的余座情况。提交后小程序不必保持在线。监控成功将收到微信服务通知。
        服务时间：0:15~23:50。其中监控运行时间为6:30~21:30，非运行时间内仅接受请求提交，不执行监控。
        '''

        if not conf.detect:
            returnMessage['service_status'] = False
            returnMessage['message'] = conf.message
            return json.dumps(returnMessage)

        start = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 15, 0))
        forbid = datetime.datetime.combine(datetime.date.today(), datetime.time(23, 50, 0))
        end = datetime.datetime.combine(datetime.date.today(), datetime.time(21, 00, 0))
        now = datetime.datetime.now()
        if now < start or now > forbid:
            returnMessage['service_status'] = False
            returnMessage['message'] = '暂停服务'
            return json.dumps(returnMessage)

        else:
            today_s = (datetime.date.today() + datetime.timedelta(days=0)).strftime("%m月%d日")
            tomorrow_s = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%m月%d日")
            if now > end:
                dates = [
                    {'name': tomorrow_s, 'value': 1}
                ]
            else:
                dates = [
                    {'name': today_s, 'value': 0},
                    {'name': tomorrow_s, 'value': 1}
                ]

            if inputJsonTree['step'] == 'default':
                selector = Selector(user)
                monitor = Monitor()
                try:
                    userInfo = monitor.singleUser(user.studentNum)
                except KeyError:
                    try:
                        buildings = selector.buildings
                        buildingName = buildings[0]['name']
                        roomList = selector.roomInfoByTime(buildingName)
                    except Exception:
                        return json.dumps({
                            'service_status': False,
                            'message': '图书馆服务器通讯异常，请稍后再试。'
                        })
                    time_int = int(time.strftime('%H', time.localtime(time.time())))
                    if time_int < 8:
                        t = 7
                    else:
                        t = time_int

                        returnMessage['status'] = True
                        returnMessage['service_status'] = True
                        returnMessage['onDetecting'] = False
                        returnMessage['buildingList'] = buildings
                        returnMessage['roomList'] = roomList
                        returnMessage['time'] = t
                        returnMessage['dates'] = dates
                        returnMessage['today_start'] = time.strftime('%H:%M', time.localtime(time.time()))
                        returnMessage['tomorrow_start'] = '06:30'
                        return json.dumps(returnMessage)

                else:
                    if keyExists('d-'+user.studentNum):
                        count = int(getRedis('d-'+user.studentNum))
                    else:
                        count = '监控尚未开始'

                    returnMessage['service_status'] = True
                    returnMessage['count'] = count
                    returnMessage['onDetecting'] = True
                    returnMessage['begin'] = userInfo['enableTime'].strftime("%m月%d日 %H:%M")
                    returnMessage['stop'] = userInfo['expireTime'].strftime("%m月%d日 %H:%M")
                    returnMessage['resTime'] = user.timetrans(userInfo['start']) + '~' + user.timetrans(userInfo['end'])

                    return json.dumps(returnMessage)
            if inputJsonTree['step'] == 'submit':
                monitor = Monitor()
                exp = inputJsonTree['stopTime'].split(':')

                try:
                    beg = inputJsonTree['beginTime'].split(':')
                    dateDelta = inputJsonTree['date']
                except KeyError:
                    start = datetime.datetime.now()
                    expire = datetime.datetime.combine(datetime.date.today(),
                                                       datetime.time(int(exp[0]), int(exp[1]), 0))
                else:
                    date = datetime.date.today() + datetime.timedelta(days=dateDelta)
                    start = datetime.datetime.combine(date, datetime.time(int(beg[0]), int(beg[1]), 0))
                    expire = datetime.datetime.combine(date, datetime.time(int(exp[0]), int(exp[1]), 0))
                try:
                    monitor.addUser(
                        studentNum=user.studentNum,
                        roomIds=inputJsonTree['roomIds'],
                        expireTime=expire,
                        start=inputJsonTree['starttime'],
                        end=inputJsonTree['endtime'],
                        buildingId=inputJsonTree['buildingId'],
                        formId=inputJsonTree['formId'],
                        stop=inputJsonTree['stopTime'],
                        enableTime=start
                    )
                except ValueError:
                    return json.dumps({
                        'status': False,
                        'message': '已提交过监控请求，请下拉刷新查看。'
                    })
                else:
                    return json.dumps({
                        'status': True,
                        'message': '提交成功。'
                    })
            if inputJsonTree['step'] == 'stop':
                monitor = Monitor()
                try:
                    monitor.deleteUser(user.studentNum, success=False)
                except ZeroDivisionError:
                    return json.dumps({
                        'status': False,
                        'message': '通讯异常'
                    })
                return json.dumps({
                    'status': True,
                    'message': '取消成功'
                })

    if inputJsonTree['method'] == 'monitor':
        returnMessage = dict()

        returnMessage['news'] = '''本页功能导引：
        余座监控：根据选定条件，实时查询当前余座，下拉刷新列表，点击即可预约。
        服务时间：01:00~21:00
        '''
        if not conf.mon:
            returnMessage['service_status'] = False
            returnMessage['message'] = conf.message

            return json.dumps(returnMessage)
        if inputJsonTree['step'] == 'change':
            selector = Selector(user)
            buildingName = inputJsonTree['building']

            returnMessage['service_status'] = True
            returnMessage['roomList'] = selector.roomInfoByTime(buildingName)
            return json.dumps(returnMessage)

        start = datetime.datetime.combine(datetime.date.today(), datetime.time(1, 0, 0))
        end = datetime.datetime.combine(datetime.date.today(), datetime.time(21, 00, 0))
        now = datetime.datetime.now()
        if now < start or now > end:
            returnMessage['service_status'] = False
            returnMessage['message'] = '暂停服务'
            return json.dumps(returnMessage)
        else:
            if inputJsonTree['step'] == 'default':
                selector = Selector(user)
                try:
                    buildings = selector.buildings
                    buildingName = buildings[0]['name']
                    roomList = selector.roomInfoByTime(buildingName)
                except Exception:
                    returnMessage['service_status'] = False
                    returnMessage['message'] = '图书馆服务器通讯异常，请稍后再试。'
                    return json.dumps(returnMessage)
                time_int = int(time.strftime('%H',time.localtime(time.time())))
                if time_int < 8:
                    t = 7
                else:
                    t = time_int
                    returnMessage['service_status'] = True
                    returnMessage['buildingList'] = buildings
                    returnMessage['roomList'] = roomList
                    returnMessage['time'] = t
                    return json.dumps(returnMessage)


            if inputJsonTree['step'] == 'refresh':
                today = str(datetime.date.today())
                start = inputJsonTree['start']
                end = inputJsonTree['end']
                try:
                    jsonTree = user.safeJsonTree(
                        url='rest/v2/searchSeats/'+ today +'/'+ start + '/' + end,
                        para={
                            # 'token': user.token,
                            '"t': 1,
                            'roomId': int(inputJsonTree['room']),
                            'buildingId': int(inputJsonTree['build']),
                            'batch': 9999,
                            'page': 1,
                            't2': '2"'
                        },
                        isPost=True,
                        useToken=True
                    )
                except Exception:
                    return json.dumps({
                        'service_status': False,
                        'message': '图书馆服务器通讯异常，请稍后再试。'
                    })
                results = []
                for key in jsonTree['data']['seats'].keys():
                    results.append(jsonTree['data']['seats'][key])
                return json.dumps({
                    'service_status': True,
                    'seats': results
                })
        if inputJsonTree['step'] == 'submit':
            incrRedis('monitor_num')
            inputJsonTree['date'] = str(datetime.date.today())
            try:
                user.bookedSeat = inputJsonTree
            except IOError:
                return json.dumps({
                    'status': False,
                    'message': "通信异常"
                })
            except ValueError as e:
                return json.dumps({
                    'status': False,
                    'message': str(e)
                })
            else:
                time.sleep(0.5)
                booked = user.bookedSeat
                try:
                    mess = booked['message'].split('，')
                    room = mess[0]
                    seatNum = mess[1][3:]
                except Exception:
                    room = booked
                    seatNum = '-'

                code = pushMessage(
                    access_token=wechat_client.access_token,
                    openid=user.openid,
                    form_id=inputJsonTree['formId'],
                    data={
                        "keyword1": {
                            "value": room,
                        },
                        "keyword2": {
                            "value": seatNum,
                            "color": "#FF6666"
                        },
                        "keyword3": {
                            "value": user.timetrans(inputJsonTree['starttime'])
                                     + '~' + user.timetrans(inputJsonTree['endtime'])
                        }
                    },
                    method='keep'
                )
                return json.dumps({
                    'status': True,
                    'message': "预约成功, code:" + str(code)
                })

    if inputJsonTree['method'] == 'select':
        if not conf.today:
            return json.dumps({
                'service_status': False,
                'message': conf.message
            })
        start = datetime.datetime.combine(datetime.date.today(), datetime.time(8, 0, 0))
        end = datetime.datetime.combine(datetime.date.today(), datetime.time(21, 30, 0))
        now = datetime.datetime.now()
        if now < start or now > end:
            return json.dumps({
                'service_status': False,
                'message': '图书馆闭馆中，服务暂停'
            })
        else:
            selector = Selector(user)
            if inputJsonTree['step'] == 'default':
                endTime = selector.endTimesFromNow[0]['value']
                buildings = selector.buildings
                buildingName = buildings[0]['name']
                roomList = selector.roomInfoByTime(buildingName, endTime)
                roomId = roomList[0]['id']
                seatList = selector.layoutByTime(roomId, endTime)
                return json.dumps({
                    'status': True,
                    'service_status': True,
                    'endTimeList': selector.endTimesFromNow,
                    'buildingList': buildings,
                    'start': '现在',
                    'roomList': roomList,
                    'seatList': seatList
                })
            if inputJsonTree['step'] == 'changed':
                details = inputJsonTree['details']
                buildingName = details['building']
                endTime = details['endtime']
                roomId = details['roomId']
                return json.dumps({
                    'status': True,
                    'service_status': True,
                    'endTimeList': selector.endTimesFromNow,
                    'buildingList': selector.buildings,
                    'start': '现在',
                    'roomList': selector.roomInfoByTime(buildingName, endTime),
                    'seatList': selector.layoutByTime(roomId, endTime)
                })

            if inputJsonTree['step'] == 'submit':
                inputJsonTree['date'] = str(datetime.date.today())
                inputJsonTree['starttime'] = '-1'
                try:
                    user.bookedSeat = inputJsonTree
                except IOError:
                    return json.dumps({
                        'status': False,
                        'message': "通信异常"
                    })
                except ValueError as e:
                    return json.dumps({
                        'status': False,
                        'message': str(e)
                    })
                except KeyError:
                    return json.dumps({
                        'status': False,
                        'message': '此房间暂无座位'
                    })
                else:
                    time.sleep(0.5)
                    booked = user.bookedSeat
                    try:
                        mess = booked['message'].split('，')
                        room = mess[0]
                        seatNum = mess[1][3:]
                    except Exception:
                        room = booked
                        seatNum = '-'

                    code = pushMessage(
                        access_token=wechat_client.access_token,
                        openid=user.openid,
                        form_id=inputJsonTree['formId'],
                        data={
                            "keyword1": {
                                "value": room,
                            },
                            "keyword2": {
                                "value": seatNum,
                                "color": "#FF6666"
                            },
                            "keyword3": {
                                "value":  '现在 ~ ' + user.timetrans(inputJsonTree['endtime'])
                            }
                        },
                        method='keep'
                    )
                    return json.dumps({
                        'status': True,
                        'message': "预约成功, code:" + str(code)
                    })

    if inputJsonTree['method'] == 'recommend':
        if len(inputJsonTree['recommend_id']) != 13:
            return json.dumps({
                'status': False,
                'title': '推荐失败',
                'message': '学号格式不正确'
            })

        if user.recommend == 0 :
            return json.dumps({
                'status': False,
                'title': '推荐失败',
                'message': '剩余推荐次数不足'
            })
        else:
            if addUser(inputJsonTree['recommend_id']):
                user.recommend = user.recommend - 1
                return json.dumps({
                    'status': True,
                    'title': '推荐成功',
                    'message': '已为'+ inputJsonTree['recommend_id'] + '开通使用权限。'
                })
            else:
                return json.dumps({
                    'status': False,
                    'title': '推荐失败',
                    'message': '数据异常，该用户可能已开通权限。'
                })

    if inputJsonTree['method'] == 'admin':
        message = conf.setStatus(inputJsonTree['status'])
        return json.dumps({
            'message': message
        })

    if inputJsonTree['method'] == 'support':
        returnMessage = dict()

        returnMessage['data'] = '''
        cWwNf066F8
        '''

        returnMessage['message'] = '作者维护此项目需要花费大量精力，并且需要自行租赁服务器。支付宝红包口令已复制到您的剪贴版，打开支付宝客户端即可领取作者的红包，给作者带来一点点的福利。希望此项目在为您带来方便的同时，能够得到一点您的支持。'

        return json.dumps(returnMessage)

    if inputJsonTree['method'] == 'messAuthor':
        data = {
            'user': {
                'value': inputJsonTree['name']
            },
            'studentnum': {
                'value': user.studentNum
            },
            'message': {
                'value': inputJsonTree['message']
            }

        }
        try:
            res = pushRunningMessage('messAuthor', data)
        except Exception:
            return json.dumps({
                'title': '失败',
                'message': '网络异常，请稍后重新提交。'
            })

        if res['errcode'] == 0:
            return json.dumps({
                'title': '成功',
                'message': '消息已收到，请勿重复提交。作者将通过用户群回复消息。'
            })
        else:
            return json.dumps({
                'title': '失败',
                'message': '网络异常，请稍后重新提交。'
            })

    else:
        return json.dumps({
            'status': False,
            'message': 'Wrong request.'
        })


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=8888)
