var website = getApp().globalData.website
var username = wx.getStorageSync('studentnum')
var card
var seat
var usingtime
var keepflag = false
var bookretflag = false
var timelist = [
  { name: "-:-", va: "480" },
  { name: "8:00", va: "480" },
  { name: "8:30", va: "510" },
  { name: "9:00", va: "540" },
  { name: "9:30", va: "570" },
  { name: "10:00", va: "600" },
  { name: "10:30", va: "630" },
  { name: "11:00", va: "660" },
  { name: "11:30", va: "690" },
  { name: "12:00", va: "720" },
  { name: "12:30", va: "750" },
  { name: "13:00", va: "780" },
  { name: "13:30", va: "810" },
  { name: "14:00", va: "840" },
  { name: "14:30", va: "870" },
  { name: "15:00", va: "900" },
  { name: "15:30", va: "930" },
  { name: "16:00", va: "960" },
  { name: "16:30", va: "990" },
  { name: "17:00", va: "1020" },
  { name: "17:30", va: "1050" },
  { name: "18:00", va: "1080" },
  { name: "18:30", va: "1110" },
  { name: "19:00", va: "1140" },
  { name: "19:30", va: "1170" },
  { name: "20:00", va: "1200" },
  { name: "20:30", va: "1230" },
  { name: "21:00", va: "1260" },
  { name: "21:30", va: "1290" },
  { name: "22:00", va: "1320" },
  { name: "22:30", va: "1350" },
  { name: "23:00", va: "1380" },
  { name: "23:30", va: "1410" },
]
Page({
  data: {
    username: wx.getStorageSync('studentnum'),
    timelist: timelist,
    startindex: 0,
    endindex: 0,
    name: wx.getStorageSync('name')
  },
  book: function () {
    bookretflag = ~bookretflag
    this.setData({
      bookretflag: bookretflag
    })
  },
  logout: function () {
    wx.setStorageSync('loginFlag', '0')
    wx.redirectTo({
      url: '../index/index',
    })
  },
  keep: function () {
    keepflag = ~keepflag
    this.setData({
      keepflag: keepflag
    })

  },
  cancel: function () {
    wx.showToast({
      title: '正在提交',
      icon: 'loading'
    })
    wx.request({
      url: website,
      data: {
        'studentNum': wx.getStorageSync('studentnum'),
        'passwd': wx.getStorageSync('passwd'),
        'step': 'delete',
        'method': 'keep'
      },
      method: 'POST', // OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT
      // header: {}, // 设置请求的 header
      success: function (res) {
        wx.hideToast()
        wx.showToast({
          title: '预约已取消',
          icon: 'success'
        })
      }
    })
    this.onLoad()
  },
  starttimePickerChange: function (e) {
    // console.log('timepicker发送选择改变，携带值为', timelist[e.detail.value].va)
    this.setData({
      startindex: e.detail.value
    })
    wx.setStorageSync('starttime', timelist[e.detail.value].va)
  },
  endtimePickerChange: function (e) {
    // console.log('timepicker发送选择改变，携带值为', e.detail.value)
    this.setData({
      endindex: e.detail.value
    })
    wx.setStorageSync('endtime', timelist[e.detail.value].va)
  },
  addseat: function () {
    wx.navigateTo({
      url: '../addseat/addseat',
    })
  },
  deletenextday: function () {
    wx.showToast({
      title: '正在提交',
      icon: 'loading'
    })
    var that = this
    wx.request({
      url: website,
      data: {
        'studentNum': wx.getStorageSync('studentnum'),
        'passwd': wx.getStorageSync('passwd'),
        'step': 'delete',
        'method': 'book'
      },
      method: 'POST', // OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT
      // header: {}, // 设置请求的 header
      success: function (res) {
        wx.hideToast()
        wx.showToast({
          title: '预约已取消',
          icon: 'success'
        })
        that.setData({
          bookretflag: false
        })

      }
    })
    this.onLoad()
  },
  keepsubmit: function (res) {
    var that = this
    wx.showToast({
      title: '信息提交中',
      icon: "loading",
      duration: 10000
    })
    wx.request({
      url: website,
      data: {
        'studentNum': wx.getStorageSync('studentnum'),
        'passwd': wx.getStorageSync('passwd'),
        'step': 'change',
        'method': 'keep',
        'formid': res.detail.formId,
        'starttime': wx.getStorageSync('starttime'),
        'endtime': wx.getStorageSync('endtime')
      },
      method: 'POST', // OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT
      // header: {}, // 设置请求的 header
      success: function (res) {
        wx.hideToast()
        wx.showModal({
          title: "提示",
          content: res.data.message
        })
        that.onLoad()
        that.setData({
          keepflag: false
        })
      },
      fail: function () {
        // fail
      },
      complete: function () {
        // complete
      }
    })

  },
  booksubmit: function (e) {
    var that = this
    wx.showToast({
      title: '正在提交预约',
      icon: 'loading',
      duration: 10000
    })
    wx.reportAnalytics('book_submit', {
      starttime: wx.getStorageSync('starttime'),
      endtime: wx.getStorageSync('endtime'),
      student_num: wx.getStorageSync('studentnum'),
      username: wx.getStorageSync('name')
    });
    wx.request({
      url: website,
      data: {
        'studentNum': wx.getStorageSync('studentnum'),
        'passwd': wx.getStorageSync('passwd'),
        'formid': e.detail.formId,
        'starttime': wx.getStorageSync('starttime'),
        'endtime': wx.getStorageSync('endtime'),
        'step': 'create',
        'method': 'book'
      },
      method: 'POST', // OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT
      // header: {}, // 设置请求的 header
      success: function (res) {
        wx.hideToast()
        wx.showModal({
          title: '提示',
          content: res.data.message,
        })
        that.onLoad()
        that.setData({
          bookretflag: false
        })
      }
    })

  },
  news_ctr: function () {
    wx.setStorageSync('enableNews', true)
    this.onLoad()
  },

  onLoad: function (options) {
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
        card: wx.getStorageSync('height') - 120,
        seat: '正在获取预约信息',
        using: '正在获取当前使用信息',
        commonseat: '正在获取常用座位',
        usingtime: '正在获取时间',
        usingflag: false,
        bookflag: false,
        navbookflag: true,
        enable_news: true,
        checkedIn: '正在获取签到状态',
        ck_in: true,
        name: wx.getStorageSync('name'),
        seat1: '空',
        seat2: '空',
        seat3: '空',
        nickname: wx.getStorageSync('name'),
        logo: wx.getStorageSync('logo'),
        open: true,
        close: true
      })
      var that = this

      wx.request({
        url: website,
        data: {
          'method': 'tomorrowMessage',
          'studentNum': wx.getStorageSync('studentnum'),
          'passwd': wx.getStorageSync('passwd')
        },
        method: 'POST', // OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT
        // header: {}, // 设置请求的 header
        success: function (res) {
          if(res.data.service_status){
            var navbookflag = !res.data.bookedPeriod.status

            that.setData({
              bookflag: res.data.bookedPeriod.status,
              seat: res.data.bookedPeriod.message,
              navbookflag: navbookflag,
              seat1: res.data.preferredSeat.seat1,
              seat2: res.data.preferredSeat.seat2,
              seat3: res.data.preferredSeat.seat3,
              open: true,
              close: false
            })
          }
          else{
            that.setData({
              title: res.data.title,
              content: res.data.content,
              open: false,
              close: true,
              bookflag: res.data.bookedPeriod.status,
              seat: res.data.bookedPeriod.message,
              navbookflag: navbookflag,
              seat1: res.data.preferredSeat.seat1,
              seat2: res.data.preferredSeat.seat2,
              seat3: res.data.preferredSeat.seat3,
            })
          }
          that.setData({
            news: res.data.news
          })
          wx.hideNavigationBarLoading()
          wx.stopPullDownRefresh()
        }
      })
    }

  },
  onPullDownRefresh: function () {
    this.onLoad()
  },
}

)
