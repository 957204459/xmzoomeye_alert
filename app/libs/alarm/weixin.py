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
import json
import urllib2
# 说明: 导入其它模块


# 说明: 获取ACCTOKEN
def get_access_token(cropid, secret):
    access_token = ''
    sou_url = ('https://qyapi.weixin.qq.com/cgi-bin/gettoken?'
               'corpid={0}&corpsecret={1}').format(cropid, secret)
    try:
        uhandle = urllib2.urlopen(sou_url)
    except urllib2.URLError, e:
        return ''
    try:
        access_token = json.loads(uhandle.read())['access_token']
    except ValueError, e:
        return ''
    uhandle.close()
    return access_token


# 说明: 发送微信消息
def post_winxinmessage(url_destpost, post_content):
    try:
        uhandle = urllib2.urlopen(url_destpost, post_content)
    except urllib2.URLError, e:
        return 'wxsend key#%s val#%s with error %s' % (url_destpost, post_content, e)
    try:
        results = json.loads(uhandle.read())
    except ValueError, e:
        return 'wxread key#%s val#%s with error %s' % (url_destpost, post_content, e)
    return results['errcode']


# 说明: 组装微信消息
def alarm_notify(content, cropid, secret, agentid=4, toparty=1, touser='@all',
                ):
    post_content = {'touser': touser,
                    'toparty': toparty,
                    'msgtype': 'text',
                    'agentid': agentid,
                    'text': {'content': content},
                    'safe': '0'}
    access_token = get_access_token(cropid, secret)
    if not access_token:
        return ''
    post_content = json.dumps(post_content, ensure_ascii=False)
    url_destpost = ('https://qyapi.weixin.qq.com/cgi-bin/message/send?'
                    'access_token={0}').format(access_token)
    postresponse = post_winxinmessage(url_destpost, post_content)
    if 0 == postresponse:
        return ''
    else:
        postresponse = 'notify key#%s val#%s with error {}'.format(postresponse)
        return postresponse
