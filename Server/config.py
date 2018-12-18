import publicFunc as public


class Configure(object):
    def getStatus(self):
        return [
            {'name': 'me', 'status': self.me},
            {'name': 'today', 'status': self.today},
            {'name': 'tomorrow', 'status': self.tomorrow},
            {'name': 'mon', 'status': self.mon},
            {'name': 'detect', 'status': self.detect},
            {'name': 'isRed', 'status': self.isRed}
        ]

    def setStatus(self, value):
        try:
            self.message = value['message']
            self.title = value['title']
            self.me = value['me']
            self.tomorrow = value['tomorrow']
            self.today = value['today']
            self.mon = value['mon']
            self.detect = value['detect']
            self.isRed = value['isRed']
        except Exception:
            return '异常'
        else:
            return '修改成功'

    @property
    def bannerColor(self):
        if public.keyExists('isRed'):
            if self.isRed:
                return {
                    'front': '#ffffff',
                    'back': '#F17C67'
                }
            else:
                return {
                    'front': '#ffffff',
                    'back': '#17abe3'
                }
        else:
            return {
                    'front': '#ffffff',
                    'back': '#17abe3'
                }

    @property
    def isRed(self):
        if public.keyExists('isRed'):
            return eval(public.getRedis('isRed'))
        else:
            return True

    @isRed.setter
    def isRed(self, status):
        public.setRedis('isRed', status, forever=True)

    @property
    def me(self):
        if public.keyExists('me'):
            return eval(public.getRedis('me'))
        else:
            return True

    @me.setter
    def me(self, status):
        public.setRedis('me', status, forever=True)

    @property
    def tomorrow(self):
        if public.keyExists('tomorrow'):
            return eval(public.getRedis('tomorrow'))
        else:
            return True

    @tomorrow.setter
    def tomorrow(self, status):
        public.setRedis('tomorrow', status, forever=True)

    @property
    def today(self):
        if public.keyExists('today'):
            return eval(public.getRedis('today'))
        else:
            return True

    @today.setter
    def today(self, status):
        public.setRedis('today', status, forever=True)

    @property
    def mon(self):
        if public.keyExists('mon'):
            return eval(public.getRedis('mon'))
        else:
            return True

    @mon.setter
    def mon(self, status):
        public.setRedis('mon', status, forever=True)

    @property
    def detect(self):
        if public.keyExists('detect'):
            return eval(public.getRedis('detect'))
        else:
            return True

    @detect.setter
    def detect(self, status):
        public.setRedis('detect', status, forever=True)

    @property
    def message(self):
        if public.keyExists('close_mess'):
            return str(public.getRedis('close_mess'), encoding = "utf-8")
        else:
            return '此功能暂时关闭'

    @message.setter
    def message(self, mess):
        public.setRedis('close_mess', mess, forever=True)

    @property
    def title(self):
        if public.keyExists('title'):
            return str(public.getRedis('title'), encoding="utf-8")
        else:
            return '座位助手'

    @title.setter
    def title(self, mess):
        public.setRedis('title', mess, forever=True)
