var website = getApp().globalData.website
var username = wx.getStorageSync('studentnum')
var logo = wx.getStorageSync('logo')
var card 
var seat
var usingtime
var keepflag = false
var bookretflag = false
const Zan = require('../../dist/index');
var timelist = [
      {name: "-:-", va: "480"},
      {name:"8:00", va : "480"},
      {name:"8:30", va : "510"},
      {name:"9:00", va : "540"},
      {name:"9:30", va : "570"},
      {name:"10:00", va : "600"},
      {name:"10:30", va : "630"},
      {name:"11:00", va : "660"},
      {name:"11:30", va : "690"},
      {name:"12:00", va : "720"},
      {name:"12:30", va : "750"},
      {name:"13:00", va : "780"},
      {name:"13:30", va : "810"},
      {name:"14:00", va : "840"},
      {name:"14:30", va : "870"},
      {name:"15:00", va : "900"},
      {name:"15:30", va : "930"},
      {name:"16:00", va : "960"},
      {name:"16:30", va : "990"},
      {name:"17:00", va : "1020"},
      {name:"17:30", va : "1050"},
      {name:"18:00", va : "1080"},
      {name:"18:30", va : "1110"},
      {name:"19:00", va : "1140"},
      {name:"19:30", va : "1170"},
      {name:"20:00", va : "1200"},
      {name:"20:30", va : "1230"},
      {name:"21:00", va : "1260"},
      {name:"21:30", va : "1290"},
      {name:"22:00", va : "1320"},
    ]
Page(Object.assign({}, Zan.Field, 
  {
  data: {
    username: wx.getStorageSync('studentnum'),
    timelist: timelist,
    startindex: 0,
    endindex:0,
    name: wx.getStorageSync('name'),
    bookedseat: {
      loc:{
        title: '位置',
        placeholder: '正在读取'
      },
      time:{
        title: '时间',
        placeholder: '正在读取'
      }
    }
  },

  logout: function(){
    wx.clearStorageSync()
    wx.redirectTo({
      url: '../index/index',
    })
  },
  recommend_change: function (e) {
    wx.setStorageSync('recommend', e.detail.value)
  },
  mess_change: function (e) {
    wx.setStorageSync('messAuthor', e.detail.value)
  },
  mess_submit: function () {
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
        'method': 'messAuthor',
        'message': wx.getStorageSync('messAuthor'),
        'name': wx.getStorageSync('name')
      },
      method: 'POST', // OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT
      // header: {}, // 设置请求的 header
      success: function (res) {
        wx.hideToast()
        wx.showModal({
          title: res.data.title,
          content: res.data.message
        })
        that.onLoad()
      }
    })
  },
  support: function(){
    wx.showToast({
      title: '正在读取',
      icon: 'loading'
    })
    wx.request({
      url: website,
      data: {
        'studentNum': wx.getStorageSync('studentnum'),
        'passwd': wx.getStorageSync('passwd'),
        'method': 'support',
      },
      method: 'POST', // OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT
      // header: {}, // 设置请求的 header
      success: function (res) {
        wx.hideToast()
        wx.showModal({
          title: "提示",
          content: res.data.message
        })
        wx.setClipboardData({
          data: res.data.data,
        })
      }
    })
  },
  setColor: function(front, background){
    wx.setNavigationBarColor({
      frontColor: front,
      backgroundColor: background,
    })
    this.setData({
      back_color: background
    })
  },
  changeStatus: function (e) {
    console.log(e)
    var that = this
    wx.request({
      url: website,
      data: {
        'studentNum': wx.getStorageSync('studentnum'),
        'passwd': wx.getStorageSync('passwd'),
        'method': 'admin',
        'status': e.detail.value
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
      }
    })
  },
  onLoad: function(){
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
        username: wx.getStorageSync('studentnum'),
        logo: 'http://prog-1251794097.costj.myqcloud.com/unknown.png', 
        news: '正在获取公告',
        name: '-',
        recommend_disable: true,
        notAdmin: true,
        notSupport: true
      })
      var that = this
      wx.getUserInfo({
        success: function (res) {
          var user = res.userInfo
          wx.setStorageSync('logo', user.avatarUrl)
          that.setData({
            logo: user.avatarUrl,
            nickname: user.nickName
          })
        }
      })

      wx.request({
        url: website,
        data: {
          'method': 'mainPage',
          'studentNum': wx.getStorageSync('studentnum'),
          'passwd': wx.getStorageSync('passwd')
        },
        method: 'POST', // OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT
        // header: {}, // 设置请求的 header
        success: function (res) {
          if (res.data.conf != false){
            that.setData({
              notAdmin: false,
              configure: res.data.conf
            })
          }
          else{
            that.setData({
              notAdmin: true
            })
          }
            that.setColor(res.data.bannerColor.front, res.data.bannerColor.back)
            wx.setNavigationBarTitle({
              title: res.data.title,
            })
            

          if (res.data.recommend > 0){
            that.setData({
              recommend_disable: false
            })
          }
            
          that.setData({
            news: res.data.news,
            serverVersion: res.data.serverVersion,
            progVersion: res.data.progVersion,
            recommend: res.data.recommend,
            notSupport: res.data.notSupport
          })
          wx.hideNavigationBarLoading()
          wx.stopPullDownRefresh()
        }
      })
      
    }
  },
  recommend_submit: function(){
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
        'method': 'recommend',
        'recommend_id': wx.getStorageSync('recommend')
      },
      method: 'POST', // OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT
      // header: {}, // 设置请求的 header
      success: function (res) {
        wx.hideToast()
        wx.showModal({
          title: res.data.title,
          content: res.data.message
        })
        that.onLoad()
      }
    })
  },
  onPullDownRefresh: function () {
    this.onLoad()
    
  },
  }
  
  
))
