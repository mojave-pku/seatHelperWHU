class Selector(object):
    def __init__(self, user):
        self.user = user

    @property
    def buildings(self):
        jsonTree = self.user.safeJsonTree(
            url="rest/v2/free/filters",
            para={
                'token': self.user.token
            }
        )
        buildings = []
        for item in jsonTree['data']['buildings']:
            building = {
                'name': item[1],
                'id': str(item[0])
            }
            buildings.append(building)
        return buildings

    def getRooms(self, buildingId):
        jsonTree = self.user.safeJsonTree(
            url="rest/v2/room/stats2/" + str(buildingId),
            para={
                "token": self.user.token
            }
        )
        return jsonTree['data']

    def getSeats(self, roomId):
        pass

    @property
    def endTimesFromNow(self):
        jsonTree = self.user.safeJsonTree(
            url="rest/v2/endTimesFromNow",
            para={
                "token": self.user.token
            }
        )
        results = []
        for time in jsonTree['data']['endTimes']:
            result = {
                'name': self.user.timetrans(time),
                'value': str(time)
            }
            results.append(result)

        return results

    def roomInfoByTime(self, building, end=-1, start=-1):
        jsonTree = self.user.safeJsonTree(
            url="rest/v2/roomsByTime/" + str(start) + '/' + str(end),
            para={
                "token": self.user.token
            }
        )
        results = []
        for record in jsonTree['data']:
            if building == record['building']:
                results.append(record)

        return results

    def layoutByTime(self, roomId, end):
        jsonTree = self.user.safeJsonTree(
            url="rest/v2/room/layoutByEndMinutes/" + str(roomId) + '/' + str(end),
            para={
                "token": self.user.token
            }
        )

        seats = jsonTree['data']['layout']
        results = []
        for item in seats.keys():
            if seats[item]['type'] == 'seat':
                if seats[item]['status'] == 'FREE':
                    results.append(seats[item])

        if len(results) == 0:
            results =[{
                        'name': '此房间暂无座位'
                    }]
        return results
