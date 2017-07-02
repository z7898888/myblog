#!/usr/bin/env python
#coding:utf-8

import logging; logging.basicConfig(level=logging.INFO);
import os,time;

from ToyToolkit.myweb import WSGIApplication, Jinja2TemplateEngine;
from ToyToolkit import db;

from config.config import configs;
import sys;
reload(sys);
sys.setdefaultencoding('utf-8');

db.createDBEngine( ** configs['db'] );

main_dir = os.path.dirname(os.path.abspath(__file__));

wsgi = WSGIApplication( main_dir );

engine_dir = os.path.join(main_dir, 'templates');
engine = Jinja2TemplateEngine( engine_dir );
wsgi.template_engine = engine;

import urls,apis;
wsgi.add_module( urls );
wsgi.add_module( apis );

if __name__ == '__main__':
	wsgi.run(host='192.168.3.222');
