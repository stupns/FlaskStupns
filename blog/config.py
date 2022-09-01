import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


# print(os.urandom(24))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '\q\xbfq\x97\xbf\t}\xec\x8c/\xcd\xb5V\x0e\x93\x81\xa0\xa9\xd0I=s\x17'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(BASEDIR, 'flask.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 2525)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USE_SSL = False
    ADMINS = ['your-email@example.com']
    POSTS_PER_PAGE = 25
    LANGUAGES = ['en', 'uk']
