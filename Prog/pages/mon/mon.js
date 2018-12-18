var website = getApp().globalData.website
var username = wx.getStorageSync('studentnum')
var card
var seat
var usingtime
var keepflag = false
var bookretflag = false
var timelist = [
  { name: "8:00", va: "480" },
  { name: "9:00", va: "540" },
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
  startPickerChange: function (e) {
    this.setData({
      start: e.detail.value,
      end: Number(e.detail.value) + 1,
    })
    var newtime = wx.getStorageSync('newtime')
    // var bookInfo = wx.getStorageSync('bookInfo')
    // var timelist = wx.getStorageSync('timelist')
    // bookInfo.endtime = timelist[e.detail.value].value
    wx.setStorageSync('start_m', newtime[e.detail.value].va)
    // this.refresh()
    this.onContentChange()
  },
  endPickerChange: function (e) {
    this.setData({
      end: e.detail.value
    })
    var newtime = wx.getStorageSync('newtime')
    // var bookInfo = wx.getStorageSync('bookInfo')
    // var timelist = wx.getStorageSync('timelist')
    // bookInfo.endtime = timelist[e.detail.value].value
    wx.setStorageSync('end_m', newtime[e.detail.value].va)
    // this.refresh()
    this.onContentChange()
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
    wx.setStorageSync('build_m', buildlist[e.detail.value].id)
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
          wx.setStorageSync('roomlist_m', roomlist)
          wx.setStorageSync('room_m', roomlist[0].id)
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
    this.onContentChange()
  },
  onContentChange: function () {
    var start = wx.getStorageSync('start_m')
    var end = wx.getStorageSync('end_m')
    var that = this
    wx.showLoading({
      title: '正在获取座位信息',
    })
    that.setData({
      'seats': [],
      'message': ''
    })
    wx.request({
      url: website,
      data: {
        'method': 'monitor',
        'step': 'refresh',
        'studentNum': wx.getStorageSync('studentnum'),
        'passwd': wx.getStorageSync('passwd'),
        'start': start,
        'end': end,
        'room': wx.getStorageSync('room_m'),
        'build': wx.getStorageSync('build_m')
      },
      method: 'POST', // OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT
      // header: {}, // 设置请求的 header
      success: function (res) {
        wx.hideLoading()
        wx.stopPullDownRefresh()
        if (res.data.service_status){
          if (res.data.seats.length == 0) {
            that.setData({
              message: '该区域在所选时段内无可用座位，请更换区域/时段/刷新重试',
              seats: res.data.seats
            })
          }
          else {
            that.setData({
              message: '',
              seats: res.data.seats
            })
          }
        }
        else{
          wx.setStorageSync('mon_stat', false)
          that.setData({
            open_m: false,
            close_m: true,
            title: res.data.message
          })
        }
        
      }
    })
  },
  submitSeat: function(e){
    console.log(e)
    console.log(e.currentTarget.dataset.seatid)
    wx.showLoading({
      title: '正在预约',
    })
    wx.request({
      url: website,
      
      data: {
        'method': 'monitor',
        'step': 'submit',
        'studentNum': wx.getStorageSync('studentnum'),
        'passwd': wx.getStorageSync('passwd'),
        'starttime': wx.getStorageSync('start_m'),
        'endtime': wx.getStorageSync('end_m'),
        'seatid': e.currentTarget.dataset.seatid,
        'formId': e.detail.formId
      },
      method: 'POST', // OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT
      // header: {}, // 设置请求的 header
      success: function (res) {
        wx.hideLoading()
        wx.showModal({
          title: '提示',
          content: res.data.message,
        })
      }
    })

  },
  roomPickerChange: function (e) {
    this.setData({
      room: e.detail.value
    })
    // var bookInfo = wx.getStorageSync('bookInfo')
    // var roomlist = wx.getStorageSync('roomlist')
    // bookInfo.roomId = roomlist[e.detail.value].id
    var roomlist = wx.getStorageSync('roomlist_m')
    wx.setStorageSync('room_m', roomlist[e.detail.value].id)
    // this.refresh()
    
    this.onContentChange()
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
        nickname: '加载中',
        timelist: [{ "name": "-" }, { "name": "-" }],
        start: 0,
        end: 1,
        room: 0,
        build: 0,
        name: wx.getStorageSync('name'),
        logo: wx.getStorageSync('logo'),
        buildlist: [{'name': '正在读取分馆数据'}],
        roomlist: [{ 'name': '正在读取楼层数据' }],
        seats: [],
        message: '',
        open_m: true,
        close_m: false
        
      })
      var that = this   
      wx.request({
        url: website,
        data: {
          'method': 'monitor',
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
            wx.setStorageSync('mon_stat', true)
            var roomlist = res.data.roomList
            var newtime = timelist.slice(); 
            newtime.splice(0, res.data.time-7)
            wx.setStorageSync('newtime', newtime)
            that.setData({
              timelist: newtime
            })
            // roomlist.unshift({'name':'全部房间','id': null})
            that.setData({
              buildlist: res.data.buildingList,
              roomlist: roomlist,

            })
            wx.setStorageSync('start_m', newtime[0].va)
            wx.setStorageSync('end_m', newtime[1].va)
            wx.setStorageSync('buildlist', res.data.buildingList)
            wx.setStorageSync('roomlist_m', roomlist)
            wx.setStorageSync('room_m', roomlist[0].id)
            wx.setStorageSync('build_m', res.data.buildingList[0].id)

            that.onContentChange()
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
    var mon_stat = wx.getStorageSync('mon_stat')
    if(mon_stat){
      this.onContentChange()
    }
    else{
      this.onShow()
    }
    

  },
}

)
