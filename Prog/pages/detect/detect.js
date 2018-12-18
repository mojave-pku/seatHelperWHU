var website = getApp().globalData.website
var username = wx.getStorageSync('studentnum')
var card
var seat
var usingtime
var keepflag = false
var bookretflag = false
var timelist = [
  { name: "08:00", va: "480" },
  { name: "09:00", va: "540" },
  { name: "10:00", va: "600" },
  { name: "11:00", va: "660" },
  { name: "12:00", va: "720" },
  { name: "13:00", va: "780" },
  { name: "14:00", va: "840" },
  { name: "15:00", va: "900" },
  { name: "16:00", va: "960" },
  { name: "17:00", va: "1020" },
  { name: "18:00", va: "1080" },
  { name: "19:00", va: "1140" },
  { name: "20:00", va: "1200" },
  { name: "21:00", va: "1260" },
  { name: "22:00", va: "1320" },
]
Page({
  data: {
    username: wx.getStorageSync('studentnum'),
    timelist: timelist,
    startindex: 0,
    endindex: 0,
    name: wx.getStorageSync('name')
  },
  checkboxChange: function(e){
    wx.setStorageSync('room_d', e.detail.value)
  },
  bindDateChange: function(e){
    var that = this
    var datelist = wx.getStorageSync('datelist_d')
    var date = datelist[e.detail.value].value
    wx.setStorageSync('date_d', date)
    that.setData({
      date_value: e.detail.value
    })
    if(date == 1){
      wx.setStorageSync('start_d', timelist[0].va)
      wx.setStorageSync('end_d', timelist[1].va)
      wx.setStorageSync('begin_d', '6:30')
      wx.setStorageSync('stop_d', that.va2str(Number(timelist[0].va) - 5))
      this.setData({
        timelist: timelist,
        mon_end_start: '06:30',
        mon_end_end: that.va2str(Number(timelist[0].va) - 5),
        mon_end_value: that.va2str(Number(timelist[0].va) - 5),
        mon_start_start: '06:30',
        mon_start_end: that.va2str(Number(timelist[0].va) - 5),
        mon_start_value: '06:30',
        start: 0,
        end: 1
      })
    }
      if (date == 0) {
        var t = this.currentTime()
        var newtime = wx.getStorageSync('newtime')
        wx.setStorageSync('start_d', newtime[0].va)
        wx.setStorageSync('end_d', newtime[1].va)
        wx.setStorageSync('begin_d', t)
        wx.setStorageSync('stop_d', that.va2str(Number(newtime[0].va) - 5))
        this.setData({
          timelist: newtime,
          mon_end_start: t,
          mon_end_end: that.va2str(Number(newtime[0].va) - 5),
          mon_end_value: that.va2str(Number(newtime[0].va) - 5),
          mon_start_start: t,
          mon_start_end: that.va2str(Number(newtime[0].va) - 5),
          mon_start_value: t,
          start: 0,
          end: 1
        })
    }
    
  },
  currentTime: function(){
    var date = new Date();
    if (Number(date.getMinutes()) < 10)
      var min = '0' + date.getMinutes()
    else
      var min = date.getMinutes()

    if (Number(date.getHours()) < 10)
      var hour = '0' + date.getHours()
    else
      var hour = date.getHours()
    var currentTime = hour + ':' + min
    return currentTime
  },
  startPickerChange: function (e) {
    var date = wx.getStorageSync('date_d')
    if (date == 0){
      var newtime = wx.getStorageSync('newtime')
    }
    else{
      var newtime = timelist
    }

    var now_stop = this.va2str(Number(newtime[e.detail.value].va) - 5)
    this.setData({
      start: e.detail.value,
      end: Number(e.detail.value) + 1,
      mon_end_end: now_stop,
      mon_end_value: now_stop
    })
    // var bookInfo = wx.getStorageSync('bookInfo')
    // var timelist = wx.getStorageSync('timelist')
    // bookInfo.endtime = timelist[e.detail.value].value
    wx.setStorageSync('start_d', newtime[e.detail.value].va)
    wx.setStorageSync('end_d', newtime[Number(e.detail.value) + 1].va)
    wx.setStorageSync('stop_d', now_stop)
    // this.refresh()
    // this.onContentChange()
    
  },
  endPickerChange: function (e) {
    this.setData({
      end: e.detail.value
    })

    var date = wx.getStorageSync('date_d')
    if (date == 0) {
      var newtime = wx.getStorageSync('newtime')
    }
    else {
      var newtime = timelist
    }

    // var bookInfo = wx.getStorageSync('bookInfo')
    // var timelist = wx.getStorageSync('timelist')
    // bookInfo.endtime = timelist[e.detail.value].value
    wx.setStorageSync('end_d', newtime[e.detail.value].va)
    // this.refresh()
    // this.onContentChange()
  },
  bindStartTimeChange: function(e){
    wx.setStorageSync('begin_d', e.detail.value)
    this.setData({
      mon_start_value: e.detail.value
    })
  },
  bindEndTimeChange: function (e) {
    wx.setStorageSync('stop_d', e.detail.value)
    this.setData({
      mon_end_value: e.detail.value
    })
  },
  buildPickerChange: function (e) {
    var that = this
    this.setData({
      build: e.detail.value
    })
    wx.showLoading({
      title: '正在获取数据',
    })
    wx.showNavigationBarLoading()
    var buildlist = wx.getStorageSync('buildlist')
    wx.setStorageSync('build_d', buildlist[e.detail.value].id)
    wx.request({
      url: website,
      data: {
        'method': 'monitor',
        'step': 'change',
        'studentNum': wx.getStorageSync('studentnum'),
        'passwd': wx.getStorageSync('passwd'),
        'building': buildlist[e.detail.value].name
      },
      method: 'POST', // OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT
      // header: {}, // 设置请求的 header
      success: function (res) {
        wx.hideLoading()
        wx.hideNavigationBarLoading()
        if (res.data.service_status) {
          var roomlist = res.data.roomList
          // roomlist.unshift({ 'name': '全部房间', 'id': null })
          wx.setStorageSync('roomlist_d', roomlist)
          that.setData({
            roomlist: roomlist,
          })
        }
        else {

        }
        wx.hideNavigationBarLoading()
        wx.stopPullDownRefresh()
      }
    })
    // this.onContentChange()
  },
  submitDetect: function(e){
    var that = this
    this.setData({
      btn_style: 'zan-btn--loading'
    })
    wx.request({
      url: website,
      
      data: {
        'method': 'detect',
        'step': 'submit',
        'date': wx.getStorageSync('date_d'),
        'studentNum': wx.getStorageSync('studentnum'),
        'passwd': wx.getStorageSync('passwd'),
        'starttime': wx.getStorageSync('start_d'),
        'endtime': wx.getStorageSync('end_d'),
        'beginTime': wx.getStorageSync('begin_d'),
        'stopTime': wx.getStorageSync('stop_d'),
        'roomIds': wx.getStorageSync('room_d'),
        'formId': e.detail.formId,
        'buildingId': wx.getStorageSync('build_d')
      },
      method: 'POST', // OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT
      // header: {}, // 设置请求的 header
      complete: function (){
        that.setData({
          btn_style: ''
        })
      },
      success: function (res) {
        that.setData({
          btn_style: ''
        })
        wx.showModal({
          title: '提示',
          content: res.data.message,
        })
        that.onShow()
        that.setData({
          running: true,
          not_running: false,
          count: '读取中',
          stoptime: '读取中'
        })
      }
    })

  },
  stopDetect: function(e){
    var that = this
    this.setData({
      btn_style: 'zan-btn--loading'
    })
    wx.request({
      url: website,

      data: {
        'method': 'detect',
        'step': 'stop',
        'studentNum': wx.getStorageSync('studentnum'),
        'passwd': wx.getStorageSync('passwd'),
      },
      method: 'POST', // OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT
      // header: {}, // 设置请求的 header
      complete: function () {
        that.setData({
          btn_style: ''
        })
      },
      success: function (res) {
        wx.hideLoading()
        wx.showModal({
          title: '提示',
          content: res.data.message,
        })
        that.onShow()
        that.setData({
          running: false,
          not_running: true
        })
      }
    })
  },
  va2str: function (va){
    var realtime = Number(va)
    var hour = parseInt(realtime/60)
    if(hour < 10) 
      var hour_s = "0" + hour.toString() 
    else
      var hour_s = hour.toString()
    var min = realtime%60
    if (min < 10)
      var min_s = "0" + min.toString()
    else
      var min_s = min.toString()
    var str = hour_s + ':' + min_s
    return str

  },
  onShow: function () {
    wx.showNavigationBarLoading()

    var loginFlag = wx.getStorageSync('loginFlag')
    if (loginFlag == "") {
      var res = wx.getSystemInfoSync()
      wx.setStorageSync('height', res.windowHeight)
      wx.redirectTo({
        url: '/pages/index/index'
      })
    }
    else {
      this.setData({
        username: wx.getStorageSync('studentnum'),
        name: wx.getStorageSync('name'),
        logo: wx.getStorageSync('logo'),
        timelist: [{ "name": "-" }, { "name": "-" }],
        start: 0,
        end: 1,
        room: 0,
        build: 0,
        nickname: wx.getStorageSync('name'),
        logo: wx.getStorageSync('logo'),
        buildlist: [{'name': '正在读取分馆数据'}],
        roomlist: [{ 'name': '正在读取楼层数据' }],
        seats: [],
        message: '',
        open_m: true,
        close_m: false,
        not_running: true
      })
      var that = this   
      wx.request({
        url: website,
        data: {
          'method': 'detect',
          'step': 'default',
          'studentNum': wx.getStorageSync('studentnum'),
          'passwd': wx.getStorageSync('passwd')
        },
        method: 'POST', // OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT
        // header: {}, // 设置请求的 header
        success: function (res) {
          that.setData({
            news: res.data.news
          })
          if (res.data.service_status) {
            
            if (!res.data.onDetecting){
              that.setData({
                running: false,
                not_running: true
              })
              wx.setStorageSync('mon_stat', true)
              var roomlist = res.data.roomList
              var newtime = timelist.slice();
              newtime.splice(0, res.data.time - 7)
              wx.setStorageSync('newtime', newtime)
              
              var date = res.data.dates[0].value
              if (date == 0){
                that.setData({
                  timelist: newtime,
                  mon_end_start: res.data.today_start,
                  mon_end_end: that.va2str(Number(newtime[0].va) - 5),
                  mon_end_value: that.va2str(Number(newtime[0].va) - 5),
                  mon_start_start: res.data.today_start,
                  mon_start_end: that.va2str(Number(newtime[0].va) - 5),
                  mon_start_value: res.data.today_start,
                })
                wx.setStorageSync('begin_d', res.data.today_start)
                wx.setStorageSync('start_d', newtime[0].va)
                wx.setStorageSync('end_d', newtime[1].va)
                wx.setStorageSync('stop_d', that.va2str(Number(newtime[0].va) - 5))
              }
              else{
                that.setData({
                  timelist: timelist,
                  mon_end_start: '06:30',
                  mon_end_end: that.va2str(Number(timelist[0].va) - 5),
                  mon_end_value: that.va2str(Number(timelist[0].va) - 5),
                  mon_start_start: '06:30',
                  mon_start_end: that.va2str(Number(timelist[0].va) - 5),
                  mon_start_value: '06:30',
                  start: 0,
                  end: 1
                })
                wx.setStorageSync('start_d', timelist[0].va)
                wx.setStorageSync('end_d', timelist[1].va)
                wx.setStorageSync('begin_d', '6:30')
                wx.setStorageSync('stop_d', that.va2str(Number(timelist[0].va) - 5))
              }
              // roomlist.unshift({'name':'全部房间','id': null})
              that.setData({
                buildlist: res.data.buildingList,
                roomlist: roomlist,
                dates: res.data.dates,
                date_value: 0
              })
              wx.setStorageSync('buildlist', res.data.buildingList)
              wx.setStorageSync('roomlist_d', roomlist)
              wx.setStorageSync('room_d', [])
              wx.setStorageSync('build_d', res.data.buildingList[0].id)
              wx.setStorageSync('date_d', res.data.dates[0].value)
              wx.setStorageSync('datelist_d', res.data.dates)
            }
            else{
              that.setData({
                running: true,
                not_running: false,
                stopTime:res.data.stop,
                count: res.data.count,
                resTime: res.data.resTime,
                beginTime: res.data.begin
              })
              
            }
            // that.onContentChange()
          }
          else {
            wx.setStorageSync('mon_stat', false)
            that.setData({
              open_m: false,
              close_m: true,
              title: res.data.message
            })
          }
          wx.hideNavigationBarLoading()
          wx.stopPullDownRefresh()
        }
      })
    }
  },

  onPullDownRefresh: function () {
    this.onShow()
    

  },
}

)
