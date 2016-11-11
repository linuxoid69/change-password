#!/usr/bin/env python
# coding: utf-8
from os import path, unlink
from time import sleep, mktime
# from bottle.ext import sqlite
import sys
from  glob import glob
from configparser import ConfigParser
import datetime
import sqlite3
import traceback


def delete_old_fields(dbname, expire):
    '''
    Запрос к базе данных
    :param dbname:
    :return:
    '''
    try:
        conn = sqlite3.connect(dbname)
        c = conn.cursor()
        c.execute("DELETE FROM user_code WHERE strftime('%s',datetime('now','localtime'))"
                  " - date_start >=  {0:d}".format(expire))
        conn.commit()
        conn.close()
        return True

    except:
        print traceback.print_exception()
        print 'don\'t connect to database'
        print dbname
        return False


def remove_captcha(img, extension='png', expire=300):
    '''
        Удаляем остаточные файлы каптчи старше 5 минут
    :param img:
    :param extension:
    :param expire:
    :return:
    '''
    try:
        for i in glob('{0:s}/*.{1:s}'.format(img, extension)):
            if (unixtime() - int(path.getctime(i))) >= int(expire):
                print 'delete file {0:s}'.format(i)
                unlink(i)

        return True
    except:
        return False

def unixtime():
    """
    Возвращает время в формате unixtime
    :return:
    """
    now = datetime.datetime.now()
    return int(mktime(now.timetuple()))


def read_config(conf):
    """
    Читаем конфиг
    :return:
    """
    config = ConfigParser()
    config.read(conf)
    return config


CONF = read_config('../settings.ini')

while True:
    remove_captcha('../{0:s}'.format(CONF['captcha']['path_image']), expire=CONF['captcha']['expire'])
    delete_old_fields('../{0:s}'.format(CONF['db']['dbname']), int(int(CONF['db']['date_expire']) * 60 * 60))
    sleep(60)

