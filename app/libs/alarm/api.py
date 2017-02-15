# -*- coding: utf-8 -*-
"""
#
# Authors: limanman
# 51CTOBG: http://xmdevops.blog.51cto.com/
# Purpose:
#
"""
# 说明: 兼容绝对导入
from __future__ import absolute_import
# 说明: 导入公共模块
# 说明: 导入其它模块
from . import sms
from . import mail
from . import weixin


# 说明: 短信报警接口
def sms_notify(*args, **kwargs):
    return sms.alarm_notify(*args, **kwargs)


# 说明: 邮件报警接口
def mail_notify(*args, **kwargs):
    return mail.alarm_notify(*args, **kwargs)


# 说明: 微信报警接口
def weixin_notify(*args, **kwargs):
    return weixin.alarm_notify(*args, **kwargs)
