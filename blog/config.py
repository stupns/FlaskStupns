import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


# print(os.urandom(24))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '\q\xbfq\x97\xbf\t}\xec\x8c/\xcd\xb5V\x0e\x93\x81\xa0\xa9\xd0I=s\x17'
