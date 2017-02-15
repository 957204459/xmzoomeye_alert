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


# 说明: 插件异常模版
alarm_template = '''
pluginname: {0}
expression: during({1}) matchs({2}) errors({3})
moredatail: ctime({4}) total({5}) succs({6}) error({7})
statistics:
{8}
'''
