#!/usr/bin/env python
# coding: utf-8
from os import path, unlink
from time import sleep, mktime
from bottle.ext import sqlite
import sys
from  glob import glob
from configparser import ConfigParser
import datetime


def remove_captcha(img, extension='png', expire=300):
    '''
    Удаляем остаточные файлы каптчи старше 5 минут
    :return:
    '''
    try:
        for i in glob('{0:s}/*.{1:s}'.format(img, extension)):
            if (unixtime() - int(path.getctime(i))) >= expire:
                print 'delete file {0:s}'.format(i)
                unlink(i)

        return True
    except:
        return False


def clean_db():
    '''
    Удаляем старые записи из базы данных которые старше 6 часов
    :return:
    '''


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

remove_captcha('../{0:s}'.format(CONF['captcha']['path_image']),expire=CONF['captcha']['expire'])

#
# while True:
#     sleep(60)
