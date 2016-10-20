#!/usr/bin/env python3
# coding: utf-8
import bottle
from bottle import get, post, static_file, request, route, template, install
from bottle import SimpleTemplate
from configparser import ConfigParser
from ldap3 import Connection, LDAPBindError, LDAPInvalidCredentialsResult, Server
from ldap3 import AUTH_SIMPLE, SUBTREE
from ldap3.core.exceptions import LDAPConstraintViolationResult, LDAPUserNameIsMandatoryError
import os
from os import path
import sys
import uuid
from bottle.ext import sqlite
from hashlib import sha1
import time
import datetime

from captcha.image import ImageCaptcha

from lib.mail import Email

# from lib.captcha import Captcha


# Устанавливаем кодировку
reload(sys)
sys.setdefaultencoding('utf-8')

# подключаем базу
plugin = sqlite.Plugin(dbfile='user_code.db')
install(plugin)


@get('/')
def get_index():
    return index_tpl()


@get('/email')
def get_email():
    global captcha, relative_path_captcha, full_path_captcha
    captcha = str(uuid.uuid1())[:5]
    relative_path_captcha = '%s%s.png' % (CONF['captcha']['path_image'], captcha[:4])
    full_path_captcha = '%s/%s' % (os.getcwdu(), relative_path_captcha)
    image = ImageCaptcha(fonts=[CONF['captcha']['font'], CONF['captcha']['font']])
    data = image.generate(captcha)
    image.write(captcha, full_path_captcha)
    return email_tpl(path_captcha=relative_path_captcha, ok='0')


@post('/email')
def post_email(db):
    form = request.forms.getunicode
    email = form('email')
    if (captcha != form('captcha')):
        return email_tpl(alerts=[('error', "Неверный код")], path_captcha=relative_path_captcha, ok='0')

        # каптча

    if find_email(email) != None:
        hash_user = sha1(email)
        id_user = str(hash_user.hexdigest())
        hash_session = sha1(id_user)
        id_session = str(hash_session.hexdigest())
        ip = str(request.environ.get('REMOTE_ADDR'))
        print check_db_email(db, email)
        if check_db_email(db, email):
            return email_tpl(alerts=[('error', "Письмо уже было отправлено вам на почту.(Проверьте спам)")],
                             path_captcha=relative_path_captcha, ok='0')

        db.execute(
            "INSERT INTO user_code (id_user, id_session, email, date_start, ip) VALUES ('{0:s}','{1:s}','{2:s}','{3:d}','{4:s}')"
                .format(id_user, id_session, email, unixtime(), ip))

        sm = Email(CONF['mail']['smtp'],
                   int(CONF['mail']['port']),
                   CONF['mail']['login'],
                   CONF['mail']['passwd'])

        html_message = """\
        <html>
        <head></head>
        <body>
    	    <p>Восстановление пароля!<br>
    	       На это письмо не нужно отвечать.<br>
    	       Перейдите по <a href="http://ldap.sotasystem.ru/restore/{0:s}/{1:s}">ссылке</a> для восстановление пароля<br>
    	       Или скопируйте ее в буфер обмена и вставьте в браузер.<br>
               http://ldap.sotasystem.ru/restore/{0:s}/{1:s}
               Ссылка действительна в течении 24 часов.
            </p>
        </body>
        </html>
        """.format(id_user, id_session)
        # Высылаем линк на почту для подтверждения

        sm.send_mail(CONF['mail']['login'], email, 'Восстановление пароля', html_message)
        return email_tpl(alerts=[('success', "Пароль был отправлен на почту")],
                         path_captcha=relative_path_captcha, ok='1')
    else:
        return email_tpl(alerts=[('error', "Пользователь с таким ящиком не найден")],
                         path_captcha=relative_path_captcha, ok='0')


@post('/')
def post_index():
    form = request.forms.getunicode

    def error(msg):
        return index_tpl(username=form('username'), alerts=[('error', msg)])

    if form('new-password') != form('confirm-password'):
        return error("Password doesn't match the confirmation!")

    if len(form('new-password')) < 8:
        return error("Password must be at least 8 characters long!")

    try:
        change_password(form('username'), form('old-password'), form('new-password'))
    except Error as e:
        print("Unsuccessful attemp to change password for %s: %s" % (form('username'), e))
        return error(str(e))

    print("Password successfully changed for: %s" % form('username'))

    return index_tpl(alerts=[('success', "Пароль был успешно изменен")])


@route('/static/<filename>', name='static')
def serve_static(filename):
    return static_file(filename, root=path.join(BASE_DIR, 'static'))


@route('/restore/<id_user>/<id_session>')
def serve_static(db, id_user, id_session):
    if redirect_to_change_passwd(db, id_user, id_session):
        return 'перенаправляем на страницу восстановления пароля'
    else:
        return 'Возспользуйтейсь формой восстановления пароля'


def index_tpl(**kwargs):
    return template('index', **kwargs)


def email_tpl(**kwargs):
    return template('email', **kwargs)


def connect_ldap(**kwargs):
    server = Server(CONF['ldap']['host'], int(CONF['ldap']['port']), connect_timeout=5)
    return Connection(server, raise_exceptions=True, **kwargs)


def change_password(*args):
    try:
        if CONF['ldap'].get('type') == 'ad':
            change_password_ad(*args)
        else:
            change_password_ldap(*args)

    except (LDAPBindError, LDAPInvalidCredentialsResult, LDAPUserNameIsMandatoryError):
        error = 'Ошибка'
        raise Error(error)

    except LDAPConstraintViolationResult as e:
        # Extract useful part of the error message (for Samba 4 / AD).
        msg = e.message.split('check_password_restrictions: ')[-1].capitalize()
        raise Error(msg)


def change_password_ldap(username, old_pass, new_pass):
    """
    Меняем пользователю пароль
    :param username:
    :param old_pass:
    :param new_pass:
    :return:
    """
    with connect_ldap() as c:
        user_dn = find_user_dn(c, username)

    # Note: raises LDAPUserNameIsMandatoryError when user_dn is None.
    with connect_ldap(authentication=AUTH_SIMPLE, user=user_dn, password=old_pass) as c:
        c.bind()
        c.extend.standard.modify_password(user_dn, old_pass, new_pass)


def change_password_ad(username, old_pass, new_pass):
    user = username + '@' + CONF['ldap']['ad_domain']

    with connect_ldap(authentication=AUTH_SIMPLE, user=user, password=old_pass) as c:
        c.bind()
        user_dn = find_user_dn(c, username)
        c.extend.microsoft.modify_password(user_dn, new_pass, old_pass)


def find_user_dn(conn, uid):
    """
    Ищем пользователя по его uid
    :param conn:
    :param uid:
    :return:
    """
    search_filter = CONF['ldap']['search_filter'].replace('{uid}', uid)
    conn.search(CONF['ldap']['base'], u"({0:s})".format(search_filter), SUBTREE, attributes=['dn', 'mail'])
    return conn.response[0]['dn'] if conn.response else None


def find_email(email):
    """
    Поиск почтового ящика в ldap
    :param email:
    :return:
    """
    search_filter = 'mail=%s' % email
    with connect_ldap() as conn:
        conn.search(CONF['ldap']['base'], "(%s)" % search_filter, SUBTREE, attributes=['dn', 'mail'])
        return conn.response[0]['attributes']['mail'] if conn.response else None


def unixtime():
    """
    Возвращает время в формате unixtime
    :return:
    """
    now = datetime.datetime.now()
    return int(time.mktime(now.timetuple()))


def check_db_email(db, email):
    """
    Проверяем высылалось ли письмо на почту
     если да, то True
    :return:
    """
    row = db.execute('SELECT email FROM user_code WHERE email="{0:s}" LIMIT 1'.format(email)).fetchone()
    return True if row else False


def redirect_to_change_passwd(db, id_user, id_session):
    row = db.execute('SELECT email FROM user_code WHERE id_user="{0}"  AND id_session="{1}" LIMIT 1'
                     .format(id_user, id_session)).fetchone()
    return True if row else False


def read_config():
    """
    Читаем конфиг
    :return:
    """
    config = ConfigParser()
    config.read([path.join(BASE_DIR, 'settings.ini'), os.getenv('CONF_FILE', '')])
    return config


class Error(Exception):
    pass


BASE_DIR = path.dirname(__file__)
CONF = read_config()

bottle.TEMPLATE_PATH = [BASE_DIR]

# Set default attributes to pass into templates.
SimpleTemplate.defaults = dict(CONF['html'])
SimpleTemplate.defaults['url'] = bottle.url

# Run bottle internal server when invoked directly (mainly for development).
if __name__ == '__main__':
    bottle.run(**CONF['server'])
# Run bottle in application mode (in production under uWSGI server).
else:
    application = bottle.default_app()
