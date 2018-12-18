# -*- coding:utf-8 -*-
import redis, urllib.request, urllib.parse, json, ssl, requests
from dbManager.sql import SQLManager
from wechatpy import WeChatClient
from config import Configure

def setRedis(key, values, expire=300, forever=False):
    ### 从管理控制台获取host, port, db_name, api_key, secret_key值

    ### 连接Redis服务
    r = redis.Redis(host="localhost", port=6379, db=0)
    r.set(key, values)
    if not forever:
        r.expire(key, expire)
    return


def getRedis(key):
    r = redis.Redis(host="localhost", port=6379, db=0)

    return r.get(key)


def incrRedis(key, amount=1, expire=False):
    r = redis.Redis(host="localhost", port=6379, db=0)
    r.incr(key, amount)

    if expire != False:
        r.expire(key, expire)
    return


def deleteRedis(key):
    r = redis.Redis(host="localhost", port=6379, db=0)

    return r.delete(key)


def keyExists(key):
    r = redis.Redis(host="localhost", port=6379, db=0)

    return r.exists(key)


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").content


def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


def addUser(studentNum):
    with SQLManager() as conn:
        result = conn.select(
            table='prog_user',
            args={
                'studentnum': studentNum
            }
        )
        if result is not False:
            return False

        conn.add(
            table='prog_user',
            args={
                'studentnum': studentNum,
                'passwd': '',
                'openid': '',
                'phonenum': ''
            }
        )

        return True

def freezeService(code):
    c = Configure()
    c.setStatus({
        'message': '发生异常，系统自动冻结服务。',
        'title': '服务已冻结',
        'me': False,
        'tomorrow': True,
        'today': True,
        'mon': False,
        'detect': False,
        'isRed': True
    })
    data = {
        'service_name': {
            'value': '全服务'
        },
        'reason': {
            'value': '网络异常：code:' + code
        },
        'mess': {
            'value': '服务已自动冻结'
        }
    }
    pushRunningMessage('warn',data)

def getJsonTree(requestUrl, requestPara, isLib=True, isPost=False, urlData=None, token=None):
    # requestPara中的key名需要与图书馆系统要求的一致
    headers = {
               # 'Accept-Language': 'en-US,en;q=0.8',
               # 'Cache-Control': 'max-age=0',
               #  'Host': 'https://seat.lib.whu.edu.cn:8443/',
               'User-Agent': 'Dalvik/2.0.0 (Linux; U; Android 7.1.1; MI 5 MIUI/8.12.7)',
               'Connection': 'Keep-Alive',
               'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8"
               }
    if token is not None:
        headers['token'] = token



    if not isPost:
        url = requestUrl + '?' + urllib.parse.urlencode(requestPara)
        ssl._create_default_https_context = ssl._create_unverified_context


        # req = urllib.request.Request(url, headers=headers)
        # try:
        if urlData is not None:

            data = json.dumps(urlData).encode(encoding='UTF8')
        else:
            data = None

            # res = urllib.request.urlopen(req, data)
        try_time = 3
        while try_time > 0:
            proxy = str(get_proxy(), encoding='utf-8')
            try:
                r = requests.get(url,
                                 headers=headers,
                                 proxies={"http": "http://{}".format(proxy)},
                                 params=data,
                                 timeout=5
                                 )
            except Exception:
                print(1)
                try_time -= 1

            # res = urllib.request.urlopen(req)
        # except urllib.request.URLError as e:
        #     if e.code == 403:
        #         incrRedis('403-error', expire=60)
        #         if int(getRedis('403-error')) >= 5:
        #             freezeService('403')
        #
        #     elif e.code == 503:
        #         incrRedis('503-error', expire=30)
        #         if not keyExists('send-503'):
        #             if int(getRedis('503-error')) >= 5:
        #                 data = {
        #                     'service_name': {
        #                         'value': '全服务'
        #                     },
        #                     'reason': {
        #                         'value': '网络异常：code:503'
        #                     },
        #                     'mess': {
        #                         'value': '错误次数：'+ str(getRedis('503-error'), encoding = "utf-8")
        #                     }
        #                 }
        #                 pushRunningMessage('warn', data)
        #                 setRedis('send-503', True, expire=300, forever=False)

        message = r.text
        print(message)

    else:
        ssl._create_default_https_context = ssl._create_unverified_context
        para = urllib.parse.urlencode(requestPara).encode(encoding='UTF8')
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
        req = urllib.request.Request(requestUrl, headers=headers)
        response = opener.open(req, para)

        message = response.read()
    # print(message)
    jsonTree = json.loads(message)
    if isLib:
        if jsonTree['status'] == 'fail':
            raise ValueError(jsonTree['message'])

    return jsonTree

def pushRunningMessage(method, data):
    client = WeChatClient('wxa7eb90b9c476562f', 'fcdc658762b4531da64bdead1004ba95')

    if method == 'warn':
        template_id = '5vx0qurLSCrOhXf2gS-NwOqcZ0xpemyxbtcRcboS578'
    if method == 'report':
        template_id = 'BFXWWD4rPNT41qQfNmBWo_d16aYdhrVA465fojniuYY'
    if method == 'messAuthor':
        template_id = 'LfKwTtgJjdUOKFqM924S8-u7B2IIO53OCIGNqoqNml0'

    res = client.message.send_template(
        user_id='o-heKw_yPwUZvJX23RcqbYX4VnG8',
        template_id=template_id,
        data=data
    )

    print(res)

    return res
def pushMessage(access_token, openid, form_id, data, method):
    pushData = {
        "touser": openid,
        "form_id": form_id,
        "data": data,
        "page": 'pages/me/me'
    }

    if method == "keep":
        templateId = 'PeCB_8avj33ESYJQt-_P2vipGuVmke0m1bRiZrFrqD0'
        pushData['emphasis_keyword'] = "keyword2.DATA"
    elif method == "book_success":
        templateId = 'f4XlGxg5jJ6gZbglcFFKAxg1syFmakmyM0Ku7QeWkmI'
    elif method == 'book_failed':
        templateId = 'UizUVVbwB67OSjD55noIWcWRyeinKs6d6AZ-5Gw7VlU'
        pushData['page'] = 'pages/detect/detect'
    elif method == 'detect':
        templateId = 'wUETS5GX1JzqeZvN6e5LLu-WcK_sZh2MZsRn87BqzDM'
        pushData['emphasis_keyword'] = "keyword3.DATA"
    elif method == 'delete_mon':
        templateId = 'UizUVVbwB67OSjD55noIWWDj0vYSKrA09BDbT4ouXNQ'
        pushData['emphasis_keyword'] = "keyword1.DATA"
        pushData['page'] = 'pages/detect/detect'
    else:
        return
    pushData['template_id'] = templateId

    jsonTree = getJsonTree(
        requestUrl="https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send",
        requestPara={
            'access_token': access_token
        },
        urlData=pushData,
        isLib=False
    )

    return jsonTree['errcode']

def intTime2strTime(intTime):
    intTime = int(intTime)
    hour = intTime // 60
    mini = intTime % 60

    if hour < 10:
        hour = '0' + str(hour)
    else:
        hour = str(hour)

    if mini < 10:
        mini = '0' + str(mini)
    else:
        mini = str(mini)

    return hour + ':' + mini

if __name__ == '__main__':
    data = {
        'date': {
            'value': '2018-01-11'
        },
        'time': {
            'value': '全天'
        },
        'booked_sum': {
            'value': '17'
        },
        'booked_success': {
            'value': '15'
        },
        'booked_rate': {
            'value': '88.23%'
        },
        'mod_num': {
            'value': '37'
        },
        'detect_num': {
            'value': '16'
        },
        'mon_num': {
            'value': '13'
        }

    }
    pushRunningMessage('report', data)