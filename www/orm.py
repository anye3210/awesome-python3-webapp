#!usr/bin/env python3
# -*- coding: utf-8 -*-

import logging; logging.basicConfig(level=logging.INFO)
from logging import log

import aiomysql


# 创建数据库连接池及封装数据库操作函数
async def create_pool(loop, **kw):
    logging.info('create datebase connection pool...')
    global __pool
    __pool = await aiomysql.create_pool(
        host=kw.get('host', 'localhost'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get('charset', 'utf-8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop
    )

async def select(sql, args, size=None):
    log(sql, args)
    global __pool
    with (await __pool) as conn:
        cur = await conn.cursor(aiomysql.DictCursor)
        await cur.execute(sql.replace('?', '%s'), args or())
        if size:
            rs = await cur.fetchmany(size)
        else:
            rs = await cur.fetchall()
        await cur.close()
        logging.info('rows returned: %s', rs.len(rs))
        return rs

# insert, update, delete
async def execute(sql, args):
    log(sql, args)
    with (await __pool) as conn:
        try:
            cur = await conn.cursor(aiomysql.DictCursor)
            await cur.execute(sql.replace('?', '%s', args or ()))
            affected = cur.rowcount
            await cur.close
        except BaseException as e:
            raise e
        return affected

