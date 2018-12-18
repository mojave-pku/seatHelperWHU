var website = getApp().globalData.website

Page({
  data: {
    username: wx.getStorageSync('studentnum'),
  },
  onShow: function () {
    wx.showNavigationBarLoading()

    var loginFlag = wx.getStorageSync('loginFlag')
    if (loginFlag == "") {
      var res = wx.getSystemInfoSync()
      wx.setStorageSync('height', res.windowHeight)
      wx.redirectTo({
        url: '../index/index'
      })
    }
    else {
      this.setData({
        name: wx.getStorageSync('name'),
        logo: wx.getStorageSync('logo'),
        end: 0,
        build: 0,
        room: 0,
        seat: 0,
        open: true,
        close: false
      })
      var that = this

      wx.request({
        url: website,
        data: {
          'method': 'select',
          'studentNum': wx.getStorageSync('studentnum'),
          'passwd': wx.getStorageSync('passwd'),
          'step': 'default'
        },
        method: 'POST',
        success: function (res) {
          if (res.data.service_status) {
            wx.hideNavigationBarLoading()
            wx.stopPullDownRefresh()
            that.setData({
              open: true,
              close: false,
              timelist: res.data.endTimeList,
              buildlist: res.data.buildingList,
              start: res.data.start,
              roomlist: res.data.roomList,
              seatlist: res.data.seatList
            })

            var bookInfo = {
              'endtime': res.data.endTimeList[0].value,
              'building': res.data.buildingList[0].name,
              'roomId': res.data.roomList[0].id,
              'seatid': res.data.seatList[0].id,
              'studentNum': wx.getStorageSync('studentnum'),
              'passwd': wx.getStorageSync('passwd'),
              'method': 'select',
              'step': 'submit'
            }

            wx.setStorageSync('bookInfo', bookInfo)
            wx.setStorageSync('buildlist', res.data.buildingList)
            wx.setStorageSync('roomlist', res.data.roomList)
            wx.setStorageSync('seatlist', res.data.seatList)
            wx.setStorageSync('timelist', res.data.endTimeList)
          }
          else {
            wx.hideNavigationBarLoading()
            wx.stopPullDownRefresh()
            that.setData({
              close: true,
              open: false,
              title: res.data.message
            })
          }
        }
      })

    }

  },
  refresh: function () {
    var that = this
    wx.showNavigationBarLoading()
    wx.showToast({
      title: '正在加载',
      icon: 'loading',
      duration:20000
    })
    wx.request({
      url: website,
      data: {
        'method': 'select',
        'studentNum': wx.getStorageSync('studentnum'),
        'passwd': wx.getStorageSync('passwd'),
        'step': 'changed',
        'details': wx.getStorageSync('bookInfo')
      },
      method: 'POST',
      success: function (res) {
        wx.setStorageSync('buildlist', res.data.buildingList)
        wx.setStorageSync('roomlist', res.data.roomList)
        wx.setStorageSync('seatlist', res.data.seatList)
        wx.setStorageSync('timelist', res.data.endTimeList)
        var bookInfo = wx.getStorageSync('bookInfo')
        bookInfo.seatid = res.data.seatList[0].id
        wx.setStorageSync('bookInfo', bookInfo)
        wx.hideNavigationBarLoading()
        wx.stopPullDownRefresh()
        that.setData({
          timelist: res.data.endTimeList,
          buildlist: res.data.buildingList,
          start: res.data.start,
          roomlist: res.data.roomList,
          seatlist: res.data.seatList
        })
        wx.hideNavigationBarLoading()
        wx.hideToast()
      }
    })
  },
  endPickerChange: function(e){
    this.setData({
      end: e.detail.value
    })
    var bookInfo = wx.getStorageSync('bookInfo')
    var timelist = wx.getStorageSync('timelist')
    bookInfo.endtime = timelist[e.detail.value].value
    wx.setStorageSync('bookInfo', bookInfo)
    this.refresh()
  },
  buildPickerChange: function (e) {
    this.setData({
      build: e.detail.value
    })
    var bookInfo = wx.getStorageSync('bookInfo')
    var buildlist = wx.getStorageSync('buildlist')
    bookInfo.building = buildlist[e.detail.value].name
    wx.setStorageSync('bookInfo', bookInfo)
    this.refresh()
  },
  roomPickerChange: function (e) {
    this.setData({
      room: e.detail.value
    })
    var bookInfo = wx.getStorageSync('bookInfo')
    var roomlist = wx.getStorageSync('roomlist')
    bookInfo.roomId = roomlist[e.detail.value].id
    wx.setStorageSync('bookInfo', bookInfo)
    this.refresh()
  },
  seatPickerChange: function (e) {
    this.setData({
      seat: e.detail.value
    })
    var bookInfo = wx.getStorageSync('bookInfo')
    var seatlist = wx.getStorageSync('seatlist')
    bookInfo.seatid = seatlist[e.detail.value].id
    wx.setStorageSync('bookInfo', bookInfo)
  },
  submit: function (e){
    console.log(e)
    wx.showToast({
      title: '正在预约',
      icon: 'loading',
      duration: 20000
    })
    wx.showNavigationBarLoading()
    var bookInfo = wx.getStorageSync('bookInfo')
    bookInfo['formId'] = e.detail.formId
    wx.request({
      url: website,
      data: bookInfo,
      method: 'POST',
      success: function(res){
        wx.hideNavigationBarLoading()
        wx.hideToast()
        wx.showModal({
          title: '预约结果',
          content: res.data.message,
        })
      }
    })
  },
  onLoad: function (options) {
    
  },
  
  onPullDownRefresh: function () {
    this.onShow()

  },
}

)
