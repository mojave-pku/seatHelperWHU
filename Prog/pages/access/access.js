var website = getApp().globalData.website

Page({
  data:{
    dis_btn: true,
    dis_reason: true
  },
  onLoad:function(options){
    // 页面初始化 options为页面跳转所带来的参数
    var that = this
    that.setData({
      studentnum: wx.getStorageSync('studentnum'),
      name: wx.getStorageSync('name')
    })
  },
  submit:function(e){
    wx.showToast({
      title: '正在处理',
      icon: 'loading',
      duration: 10000
    })
    var that = this
    wx.request({
      url: website,
      method: "POST",
      data: { 
        'method': 'access',
        'studentNum': e.detail.value.studentnum,
        'passwd': '',
        'name': e.detail.value.name, 
        'reason': e.detail.value.reason
        },
      success: function(){
        wx.hideToast()
        wx.showModal({
          title: '提交成功',
          content: '您的提交已成功，我们将根据情况决定是否为您开通使用权限。为限制软件发展速度，保证正常运营，我们必须这么做，请您谅解。如您已经提交过申请，之前的申请将被覆盖。',
          showCancel: false
        })
        that.onLoad()
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
  }
})