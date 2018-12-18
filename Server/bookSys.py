import aiohttp, asyncio, ssl
import datetime, time, json,random
from wechatpy import WeChatClient
from dbManager.sql import SQLManager
from user import User
from publicFunc import pushMessage, getJsonTree
import threading


class MultiThreading(threading.Thread):
    def __init__(self, record):
        threading.Thread.__init__(self)
        self.record = record
        self.date = str(datetime.date.today() + datetime.timedelta(days=1))

    def run(self):
        time.sleep(self.record['push']['delay'])
        # print(self.record['push']['delay'])
        result = getJsonTree(
            requestPara=self.record['params'],
            requestUrl='https://seat.lib.whu.edu.cn:8443/rest/v2/freeBook',
            isLib=False,
            isPost=True,
            token=self.record['push']['token']
        )

        # print(result)

        user = User(self.record['push']['student_num'], self.record['push']['passwd'])

        if result['status'] == 'fail':
            pass
        else:
            data = {
                "keyword1": {
                    "value": self.record['push']['building'],
                    "color": "#173177"
                },
                "keyword2": {
                    "value": self.record['push']['location'],
                    "color": "#173177"
                },
                "keyword3": {
                    "value": self.date,
                    "color": "#173177"
                },
                "keyword4": {
                    "value": user.timetrans(self.record['push']['startTime'])
                             + '~' + user.timetrans(self.record['push']['endTime']),
                    "color": "#173177"
                }
            }
            code = int(pushMessage(
                access_token=wechat_client.access_token,
                openid=user.openid,
                form_id=self.record['push']['form_id'],
                data=data,
                method='book_success'
            ))
            if code == 0:
                print(self.record['push']['student_num'] + ', success.')



date = str(datetime.date.today() + datetime.timedelta(days=1))

wechat_client = WeChatClient(
    appid='',
    secret=''
)

with open(date + '.txt', 'r') as f:
    records = json.loads(f.read())

for record in records:
    m = MultiThreading(record)
    m.start()

# class BookSystem(object):
#     async def submit(self, record, results):
#         async with aiohttp.ClientSession() as session:
#             h = self.headers
#             h['token'] = record['push']['token']
#             asyncio.sleep(record['push']['delay'])
#             async with session.post(self.submit_url, params=record['params'], verify_ssl=False, headers=h) as response:
#                 data = await response.read()
#                 print(data)
#                 resp = json.loads(data.decode("utf-8"))
#                 print(resp)
#                 results.append({
#                     'message': resp['message'],
#                     'status': resp['status'],
#                     'push': record['push']
#                 })
#
#     def __init__(self, debug_date=None):
#         self.submit_url = "https://seat.lib.whu.edu.cn:8443/rest/v2/freeBook"
#         self.date = debug_date or \
#                     str(datetime.date.today() + datetime.timedelta(days=1))
#         self.headers = {
#                # 'Accept-Language': 'en-US,en;q=0.8',
#                # 'Cache-Control': 'max-age=0',
#                #  'Host': 'https://seat.lib.whu.edu.cn:8443/',
#                'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.1; MI 6 MIUI/7.12.7)',
#                'Connection': 'close',
#                'Expect': '100-continue',
#                'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8"
#                }
#         with open(self.date + '.txt', 'r') as f:
#             self.records = json.loads(f.read())
#
#     def start(self):
#         results = []
#         tasks = [self.submit(record, results) for record in self.records]
#         loop = asyncio.get_event_loop()
#         loop.run_until_complete(asyncio.wait(tasks))
#
#         for result in results:
#             user = User(result['push']['student_num'], result['push']['passwd'])
#             if result['status'] == 'fail':
#                 pass
#             else:
#                 data = {
#                     "keyword1": {
#                         "value": result['push']['building'],
#                         "color": "#173177"
#                     },
#                     "keyword2": {
#                         "value": result['push']['location'],
#                         "color": "#173177"
#                     },
#                     "keyword3": {
#                         "value": self.date,
#                         "color": "#173177"
#                     },
#                     "keyword4": {
#                         "value": user.timetrans(result['push']['startTime'])
#                                  + '~' + user.timetrans(result['push']['endTime']),
#                         "color": "#173177"
#                     }
#                 }
#                 code = int(pushMessage(
#                     access_token=wechat_client.access_token,
#                     openid=user.openid,
#                     form_id=result['push']['form_id'],
#                     data=data,
#                     method='book_success'
#                 ))
#                 if code == 0:
#                     print(result['push']['student_num'] + ', success.')
#
#         for result in results:
#             user = User(result['push']['student_num'], result['push']['passwd'])
#             if result['status'] == 'fail':
#                 data = {
#                     "keyword1": {
#                         "value": self.date,
#                         "color": "#173177"
#                     },
#                     "keyword2": {
#                         "value": user.timetrans(result['push']['startTime'])
#                                  + '~' + user.timetrans(result['push']['endTime']),
#                         "color": "#173177"
#                     },
#                     "keyword3": {
#                         "value": result['message'],
#                         "color": "#173177"
#                     },
#                     "keyword4": {
#                         "value": '请点击下方链接进入"余座监控"功能监控座位！',
#                         "color": "#173177"
#                     }
#                 }
#                 code = pushMessage(
#                     access_token=wechat_client.access_token,
#                     openid=user.openid,
#                     form_id=result['push']['form_id'],
#                     data=data,
#                     method='book_failed'
#                 )
#
#                 if code == 0:
#                     print(result['push']['student_num'] + ', failed.')




# b = BookSystem()
# print(b.date)


