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
  book: function (){
    bookretflag = ~ bookretflag
    this.setData({
      bookretflag : bookretflag
    })
  },
  logout: function(){
    wx.clearStorageSync()
    wx.redirectTo({
      url: '../index/index',
    })
  },
  keep: function(){
    keepflag = ~keepflag
    this.setData({
      keepflag : keepflag
    })
    
  },
  changeStatus: function(e){
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
        that.onShow()
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
  cancel:function(){
    wx.showToast({
      title:'正在提交',
      icon:'loading'
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
      success: function(res){
        wx.hideToast()
        wx.showToast({
          title:'预约已取消',
          icon:'success'
        })
      }
    })
    this.onShow()
  },
  starttimePickerChange:function(e){
    // console.log('timepicker发送选择改变，携带值为', timelist[e.detail.value].va)
    this.setData({
      startindex: e.detail.value
    })
    wx.setStorageSync('starttime', timelist[e.detail.value].va)
  },
  endtimePickerChange:function(e){
    // console.log('timepicker发送选择改变，携带值为', e.detail.value)
    this.setData({
      endindex: e.detail.value
    })
    wx.setStorageSync('endtime', timelist[e.detail.value].va)
  },
  addseat: function(){
    wx.navigateTo({
      url: '../addseat/addseat',
    })
  },
  deletenextday: function(){
    deletenextdayinfo['studentnum'] = wx.getStorageSync('studentnum')
    wx.showToast({
      title:'正在提交',
      icon:'loading'
    })
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
      success: function(res){
        wx.hideToast()
        wx.showToast({
          title:'预约已取消',
          icon:'success'
        })
        this.setData({
          bookretflag: false
        })
        
      }
    })
    this.onShow()
  },
  keepsubmit:function (res){
    var that = this
    wx.showToast({
      title:'信息提交中',
      icon:"loading",
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
      success: function(res){
        wx.hideToast()
        wx.showModal({
            title:"提示",
            content: res.data.message
          })
        that.onShow()
        that.setData({
          keepflag: false
        })
      },
      fail: function() {
        // fail
      },
      complete: function() {
        // complete
      }
    })
    
  },
  booksubmit: function(e){
    var that = this
    wx.showToast({
      title:'正在提交预约',
      icon:'loading',
      duration: 10000
    })
    booktime['formid'] = e.detail.formId
    booktime['studentnum'] = wx.getStorageSync('studentnum')
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
      success: function(res){
        wx.hideToast()
        wx.showToast({
          title:"提交成功",
          icon:'success'
        })
        that.onShow()
        that.setData({
          bookretflag: false
        })
      }
    })
    
  },
  recommend_change: function(e){
    wx.setStorageSync('recommend', e.detail.value)
  },
  news_ctr: function(){
    wx.setStorageSync('enableNews', true)
    this.onShow()
  },
  onShow: function(){
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
        name: '-',
        close: true,
        open: true,
        recommend_disable: true,
        notAdmin: true
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
          'method': 'meMessage',
          'studentNum': wx.getStorageSync('studentnum'),
          'passwd': wx.getStorageSync('passwd')
        },
        method: 'POST', // OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT
        // header: {}, // 设置请求的 header
        success: function (res) {
          
          if(!res.data.service_status){
            that.setData({
              title: res.data.message,
              name: wx.getStorageSync('name'),
              news: res.data.news,
              close: true,
              open: false,
            })
          }
          else{
    
            that.setData({
            close: false,
            open: true,
            name: res.data.inStatus.name,
            usingflag: res.data.bookedSeat.booked,
            using: res.data.bookedSeat.message,
            usingtime: res.data.bookedSeat.period,
            notAdaptable: res.data.notAdaptable
            })
            if (res.data.inStatus.checkedIn == true) {

              that.setData({
                ck_out: true,
                ck_in: false,
                checkedIn: res.data.inStatus.lastIn + '于',
                inLoc: res.data.inStatus.lastInBuildingName + '签到',
                
              })

              if (res.data.inStatus.lastOut != null) {
                // 入馆但未出馆
                that.setData({
                  ck_out: false,
                  outTime: '，' + res.data.inStatus.lastOut + '暂离',
                })
              }


            }
            else {
              that.setData({
                checkedIn: '未在馆内'
              })
            }

            wx.setStorageSync('name', res.data.inStatus.name)
            
          }
          if (res.data.recommend > 0){
            that.setData({
              recommend_disable: false
            })
          }
            
          that.setData({
            news: res.data.news,
            serverVersion: res.data.serverVersion,
            progVersion: res.data.progVersion,
            recommend: res.data.recommend
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
        that.onShow()
      }
    })
  },
  onPullDownRefresh: function () {
    this.onShow()
    
  },

  }
  
  
))
