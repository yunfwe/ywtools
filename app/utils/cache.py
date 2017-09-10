#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: weiyunfei  date: 2017-07-05

import time
import hashlib
try:
    import cPickle as pickle
except ImportError:
    import pickle
from functools import wraps

class CacheAdapter(object):
    """
    抽象类 缓存处理器需要继承这个类
    子类需要实现 get 和 set 方法
    """
    def __init__(self, timeout=0):
        assert isinstance(timeout, (int,float)),'timeout type must to be number'
        # 缓存超时时间
        self.timeout = timeout

    class ExpiredException(Exception):pass
    class KeyNotFoundError(Exception):pass

    def get(self, key):
        raise NotImplementedError("Subclass must to be implement 'get' function")

    def set(self, key, value):
        raise NotImplementedError("Subclass must to be implement 'set' function")


class MemoryCache(CacheAdapter):
    """
    使用字典保存结果，也可以换成reids等数据库进行数据缓存
    """
    pool = {}

    # 最大缓存数 当缓存超过此值 将清空所有缓存
    # 设置为0 则不进行缓存 设置为负数 则不限制缓存大小
    maxcaches = -1

    def __init__(self, timeout=0):
        # 在父类中初始化timeout参数
        CacheAdapter.__init__(self, timeout=timeout)
        if MemoryCache.pool is None:
            MemoryCache.pool = {}
        assert isinstance(self.maxcaches, int),\
            'maxcache type must to be integer'

    @staticmethod
    def flush():
        MemoryCache.pool.clear()

    def set(self, key, value):
        cache = {
            'value' : value,
            'expire': time.time() + self.timeout
        }
        if self.maxcaches == 0:
            return None
        elif self.maxcaches > 0:
            if len(MemoryCache.pool.keys()) >= self.maxcaches:
                MemoryCache.flush()
        else:
            MemoryCache.pool[key] = cache



    def get(self, key):
        cache = MemoryCache.pool.get(key, None)
        if cache is None:
            raise self.KeyNotFoundError("Key: '%s' not found!" % key)
        if time.time() - cache.get('expire', 0) > 0:
            MemoryCache.pool.pop(key, {})
            raise self.ExpiredException('Expired!')
        else:
            return cache.get('value', None)

    def __str__(self):
        return str(MemoryCache.pool)

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()


def wrapcache(timeout=0, handler=MemoryCache):
    """
    这个装饰器用来缓存函数返回值
    """
    db = handler(timeout=timeout)
    def _wrapcache(func):
        @wraps(func)
        def _function(*args, **kwargs):
            meta = (func.__name__, args, kwargs)
            md5key = hashlib.md5(pickle.dumps(meta)).hexdigest()
            try:
                return db.get(md5key)
            except:
                value = func(*args, **kwargs)
                db.set(md5key, value)
                return value
        return _function
    return _wrapcache

