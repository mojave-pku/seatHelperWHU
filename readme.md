# 座位助手

该项目适用于武汉大学图书馆的座位预约系统，可以实现座位自动预约、余座监控等功能。由于长时间未维护，**现暂时无法与图书馆服务器正常通讯**。需要改造Server/publicFunc.py中的**getJsonTree()**方法，加上某些字段以伪装成正常的访问。

## 项目结构

该项目分为两个部分，微信小程序和服务端，可以通过对服务端的代码稍加改造实现单机版的插件。

- Prog：小程序源码
  - app.js/app.json/app.wxss/.../（这部分文件为微信小程序的配置文件，[说明见官方文档](https://developers.weixin.qq.com/miniprogram/dev/index.html)）
  - pages
    - access：使用申请页面
    - addseat：添加常用座位
    - detect：余座监控
    - index：登陆页面
    - me：我的（该页面为登陆后实际的主页）
    - mon：余座查询
    - news：关于
    - *resIndex：已弃用*
    - today：即时选座
    - tomorrow：预约明日座位
- Server：服务器源码
  - book_failed.py：预定失败时给用户推送失败信息的脚本
  - bookSys.py：刷座功能的核心脚本
  - config.py：服务端控制功能开闭的配置
  - dbManager：数据库管理公共代码
    - sql_config.py：配置文件
    - sql.py：实现了一个mysql的抽象接口
  - fetchSeatHandler.py：余座监控核心功能脚本（常驻后台）
  - monitor.py：余座监控信息管理脚本
  - prepareBook.py：预约前预登陆、信息获取脚本
  - publicFunc.py：公共方法库
  - report.py：每日报告（向开发者）脚本
  - requestHandler.py：服务端主脚本（常驻后台）
  - selector.py：座位信息查询类
  - user.py：用户类

## 修改建议

使用云服务器有被图书馆整体拉黑ip的可能，建议放弃小程序，直接将原服务端改造成单机版小程序。可以先从Server/publicFunc.py中的**getJsonTree()**入手，先建立正常的服务器通讯，然后参考bookSys.py实现刷座功能

## 需要帮助？

关于代码理解方面的问题欢迎一起探讨，但毕竟是很早以前写的代码，我会尽我所能提供帮助。如有需要，请在该项目内提issue或发邮件至hlz@pku.edu.cn。