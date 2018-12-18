import aiohttp, asyncio, ssl
import datetime, time, json,random
from wechatpy import WeChatClient
from dbManager.sql import SQLManager
from user import User
from publicFunc import pushMessage, getJsonTree, incrRedis
import threading

date = str(datetime.date.today() + datetime.timedelta(days=1))

wechat_client = WeChatClient(
    appid='wx3c1ed4db3c5b089b',
    secret='65860300a0c740cb5ca0757cc4b218e2'
)
with open(date + '.txt', 'r') as f:
    records = json.loads(f.read())


for record in records:
    user = User(record['push']['student_num'], record['push']['passwd'])
    data = {
        "keyword1": {
            "value": date,
            "color": "#173177"
        },
        "keyword2": {
            "value": user.timetrans(record['push']['startTime'])
                     + '~' + user.timetrans(record['push']['endTime']),
            "color": "#173177"
        },
        "keyword3": {
            "value": '预约失败，请及时预约其他座位',
            "color": "#173177"
        },
        "keyword4": {
            "value": '请点击下方链接进入"余座监控"功能监控座位！',
            "color": "#173177"
        }
    }
    code = pushMessage(
        access_token=wechat_client.access_token,
        openid=user.openid,
        form_id=record['push']['form_id'],
        data=data,
        method='book_failed'
    )

    if code == 0:
        incrRedis('book_failed')
        print(record['push']['student_num'] + ', failed.')