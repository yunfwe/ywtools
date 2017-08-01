#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-07-07

from functools import wraps

def coroutinue_activate(func)
    """
    预先激活协程
    """
    @wraps(func)
    def _coroutinue(*args, **kwargs):
        gen = func(*args, **kwargs)
        next(gen)
        return gen
    return _coroutinue
