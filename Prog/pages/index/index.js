//index.js
//获取应用实例
var website = getApp().globalData.website
const Zan = require('../../dist/index');
var app = getApp()
var returnInfo = ''
var loginFlag = wx.getStorageSync('loginFlag')
Page(Object.assign({}, Zan.Field, 
  {
  data: {
    inputContent: {},
    stu : wx.getStorageSync('studentnum'),
    passwd : wx.getStorageSync('passwd'),
    form: {
      name:{
        title: '学号',
        type: 'number',
        componentId: 'studentnum'
      },
      passwd:{
        title: '密码',
        inputType: 'password',
        componentId: 'passwd'
      }
    }
  },
  //事件处理函数
  bindViewTap: function() {
    wx.navigateTo({
      url: '../logs/logs'
    })
  },
  pwd: function(e){
    this.setData({
      pwdfocus : true
    })
  },
  checkUser: function(e){
    this.setData({
      btn_style: 'zan-btn--loading'
    })
    var that = this
    wx.login({
      success: function(res){
        
        if (res.code){
          
          wx.request({
            url: website,
            data: {
              'method': 'login',
              'studentNum': e.detail.value.studentnum,
              'passwd': e.detail.value.passwd,
              'jscode': res.code
            },
            method: 'POST', // OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT
            // header: {}, // 设置请求的 header
            success: function(res){
              that.setData({
                btn_style: ''
              })
              if (res.data.isCorrect){
                if (res.data.isAccessible){
                  wx.setStorageSync('studentnum', e.detail.value.studentnum)
                  wx.setStorageSync('passwd', e.detail.value.passwd)
                  wx.setStorageSync('loginFlag', '1')
                  wx.setStorageSync('name', res.data.inStatus.name)
                  wx.switchTab({
                    url: '/pages/news/news'
                  })
                }
                else{
                  wx.setStorageSync('studentnum', e.detail.value.studentnum)
                  wx.setStorageSync('passwd', e.detail.value.passwd)
                  wx.setStorageSync('name', res.data.inStatus.name)
                  wx.showToast({
                    title: '用户未认证'
                  })
                  wx.navigateTo({
                    url: "/pages/access/access",
                  })
                }
              }
              else{
                wx.hideToast()
                wx.showModal ({
                  content: '账号/密码错误!',

                })
              }

            }
          })
        }
        else{
          wx.showModal({
            title:"授权失败",
            content:"您将无法使用公众号的部分功能"
          })
        }
      }
      
    })
  },
  handleZanFieldChange(e) {
    const { componentId, detail } = e;

    console.log('[zan:field:change]', componentId, detail);
  },

  handleZanFieldFocus(e) {
    const { componentId, detail } = e;

    console.log('[zan:field:focus]', componentId, detail);
  },

  handleZanFieldBlur(e) {
    const { componentId, detail } = e;

    console.log('[zan:field:blur]', componentId, detail);
  },

  clearInput() {
    this.setData({
      value: ''
    });
  },

  clearTextarea() {
    this.setData({
      textareaValue: ''
    });
  },

  formSubmit(event) {
    console.log('[zan:field:submit]', event.detail.value);
  },

  formReset(event) {
    console.log('[zan:field:reset]', event);
  },
  onLoad: function () {
    console.log('onLoad')
    var that = this
    //调用应用实例的方法获取全局数据
    app.getUserInfo(function(userInfo){
      //更新数据
      that.setData({
        userInfo:userInfo
      })
    })
    
  }
}))
