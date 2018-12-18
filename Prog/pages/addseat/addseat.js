// pages/addseat/addseat.js

var website = getApp().globalData.website
var roomlist = []
var bulidinglist = []
var level = '1'
Page({
  data:{
    roomlist : [],
    index: 0,
    roomindex: 0,
    bulidingindex: 0,
    on_button: true
  },
  onLoad:function(options){
    // 页面初始化 options为页面跳转所带来的参数
    this.setData({
      level : '1'
    })
    wx.showToast({
      title:'正在读取数据',
      icon:'loading',
      duration:10000
    })
    var that = this
    wx.request({
      url: website,
      data: {
        'studentNum': wx.getStorageSync('studentnum'),
        'passwd': wx.getStorageSync('passwd'),
        'method': 'addSeats',
        'step': 'getBuildings',
      },
      method: 'POST', // OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT
      // header: {}, // 设置请求的 header
      success: function(res){
        wx.hideToast()
        bulidinglist = res.data.buildings
        bulidinglist.unshift({'name':'请选择分馆','id':'-1'})
        that.setData({
          bulidinglist: bulidinglist
        })
        
      }
    })
  },
  onReady:function(){
    // 页面渲染完成
  },
  onShow:function(){
    // 页面显示
  },
  onHide:function(){
    // 页面隐藏
  },
  onUnload:function(){
    // 页面关闭
  },
  bulidingChange: function(e) {
    this.setData({
      bulidingindex: e.detail.value
    })
    var that = this
    wx.showToast({
      title:'正在读取数据',
      icon:'loading',
      duration:10000
    })
    wx.request({
      url: website,
      data: {
        'studentNum': wx.getStorageSync('studentnum'),
        'passwd': wx.getStorageSync('passwd'),
        'method': 'addSeats',
        'step': 'getRooms',
        'building': bulidinglist[e.detail.value].id
      },
      method: 'POST', // OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT
      // header: {}, // 设置请求的 header
      success: function(res){
        wx.hideToast()
        roomlist = res.data.rooms
        roomlist.unshift({'room':'请选择房间','id':'-1'})
        that.setData({
          roomlist: roomlist
        })
      }
    })
  },
  roomChange: function(e){
    this.setData({
      roomindex: e.detail.value
    })
  },
  levelChange: function(e){
    this.setData({
      level: e.detail.value
    })
  },
  submit: function(e){
    wx.showToast({
      title: '正在提交信息',
      icon: 'loading',
      duration: 10000
    })
    wx.request({
      url: website,
      data: {
        'studentNum': wx.getStorageSync('studentnum'),
        'passwd': wx.getStorageSync('passwd'),
        'method': 'addSeats',
        'step': 'submit',
        'roomid': roomlist[e.detail.value.room].roomId,
        'seatnum': e.detail.value.seat,
        'building': bulidinglist[e.detail.value.building].name,
        'room': roomlist[e.detail.value.room].room,
        'level': e.detail.value.level
      },
      method: 'POST', // OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT
      // header: {}, // 设置请求的 header
      success: function(res){
        wx.hideToast()
        wx.showModal({
          title: '提示',
          content: res.data.message,
        })
      },
      fail: function() {
        // fail
      },
      complete: function() {
        // complete
      }
    })
  }
})