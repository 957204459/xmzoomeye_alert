#!/usr/bin/env python
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
import os
import copy
import time
import hashlib
from gevent.server import StreamServer
# 说明: 导入其他模块
from ..libs.alarm import alarm_template


# 说明: 报警服务类
class AlertServer(object):
    def __init__(self, conf, info, error):
        self.info = info
        self.error = error
        # 报警统计记录
        self.alertdatas = {}
        # 消息加密分类
        self.hash = hashlib.md5

        self.conf = conf
        self.alert_host = self.conf['alert'].get('host', '')
        self.alert_port = int(self.conf['alert'].get('port', 1314))

    def start(self):
        server = StreamServer(
            (self.alert_host, self.alert_port), self.tcp_handler
        )
        server.serve_forever()

    # 尝试触发报警器
    def sta_alarmes(self, plugin_name, plugin_event):
        expression = self.conf[plugin_name]
        statistics = []
        for md5 in plugin_event['datas']:
            md5_data = plugin_event['datas'][md5]
            statistics.append(
                '=> {0} . {1}'.format(md5_data['count'], md5_data['mesgs'])
            )
        weixin_msg = alarm_template.format(
            plugin_name,
            str(expression['during']),
            str(expression['matchs']),
            str(expression['errors']),
            str(plugin_event['ctime']),
            str(plugin_event['total']),
            str(plugin_event['succs']),
            str(plugin_event['error']),
            os.linesep.join(statistics)
        )
        print weixin_msg

    # 检测匹配触发器
    def chk_handler(self):
        if not self.alertdatas:
            return
        alertdatas = copy.deepcopy(self.alertdatas)
        for plugin_name in alertdatas:
            plugin_name = plugin_name.strip()
            if plugin_name not in self.conf:
                # 如果插件未定义触发器则提醒并弹出
                self.error.error(
                    'not defined expresion for plugin#{0}'.format(plugin_name)
                )
                self.alertdatas.pop(plugin_name)
                continue
            during = self.conf[plugin_name].get('during').strip()
            if during:
                during = int(during)
            matchs = self.conf[plugin_name].get('matchs').strip()
            if matchs:
                matchs = int(matchs)
            errors = self.conf[plugin_name].get('errors').strip()
            if errors:
                errors = int(errors)

            # 如果没有取样时间,就尝试判断匹配次数和失败次数
            if not during:
                if self.alertdatas[plugin_name]['total'] == matchs:
                    # 如果大于等于自定义失败次数就报警
                    if self.alertdatas[plugin_name]['error'] >= errors:
                        self.sta_alarmes(plugin_name, self.alertdatas[plugin_name])
                    # 最终都弹出已计算过项
                    self.alertdatas.pop(plugin_name)
            # 如果存在取样时间,就尝试判断失败次数
            else:
                # 当前时间-插件第一次数据上报时间时>=during时间时
                if time.time() - self.alertdatas[plugin_name]['ctime'] >= during:
                    if self.alertdatas[plugin_name]['error'] >= errors:
                        self.sta_alarmes(plugin_name, self.alertdatas[plugin_name])
                        # 最终都弹出已计算过项
                        self.alertdatas.pop(plugin_name)
                else:
                    # 当前时间-插件第一次数据上报时间时<during时间时,但错误数已超出
                    if self.alertdatas[plugin_name]['error'] >= errors:
                        self.sta_alarmes(plugin_name, self.alertdatas[plugin_name])
                        # 最终都弹出已计算过项
                        self.alertdatas.pop(plugin_name)
                    else:
                        continue

    # 实时接收处理流
    def tcp_handler(self, socket, address):
        """
        plugin_name -> {
            ctime: time.time(),
            total: 10,
            succs: 8,
            error: 2,
            datas: {
                md5: {
                    'count': 1
                    'mesgs': 'error messages'
                },
                md5: {
                    'count': 1,
                    'mesgs': 'error messages'
                }
                .......
            }
        }
        """
        while True:
            data = socket.recv(4096)
            if not data.strip():
                break
            plugin_name, res, message = data.split(' ', 2)
            self.alertdatas.setdefault(plugin_name, {
                'ctime': time.time(),
                'total': 0, 'succs': 0, 'error': 0, 'datas': {}
            })
            self.info.info(
                'recv from {0} with plugin_name#{1} res#{2} message#{3}'.format(
                    address, plugin_name, res, message
                )
            )
            # 异常信息
            if int(res):
                self.alertdatas[plugin_name]['error'] += 1
                md5_obj = self.hash(message)
                md5 = md5_obj.hexdigest()
                if md5 in self.alertdatas[plugin_name]['datas']:
                    self.alertdatas[plugin_name]['datas'][md5]['count'] += 1
                else:
                    self.alertdatas[plugin_name]['datas'].setdefault(md5, {
                        'count': 1, 'mesgs': message,
                    })
            # 正常信息
            else:
                self.alertdatas[plugin_name]['succs'] += 1

            self.alertdatas[plugin_name]['total'] += 1

            # 开始检测
            self.chk_handler()
