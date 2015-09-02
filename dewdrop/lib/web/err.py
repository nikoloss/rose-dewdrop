#coding: utf-8

class BizError(Exception):
    __slots__ = ('code', 'reason')
    code = '0'
    reason = '业务发生异常'

class RemoteError(BizError):
    code = '19'
    reason = '远程服务器不可达'

class SessionError(BizError):
    code = '102'
    reason = 'ck失效'