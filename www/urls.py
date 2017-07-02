#!/usr/bin/env python
#coding:utf-8

from ToyToolkit.myweb import route,intercept,view,ctx,StaticRoute,SeeOther,NotFound;
from models import User,Blog;
import datetime, time, hashlib;

from page import datetime_filter;

from config.config import configs;

_COOKIE_KEY = configs['session']['secret'];

@view('index.html')
@route('/','get')
def index():
	blogs = Blog.get_all();
	user = ctx.request.user;
	return dict( blogs = blogs, user=user);

@view('blog_list.html')
@route('/manage/blog','get')
def blog_list():
	user = ctx.request.user;
	index = ctx.request.get('page_index');
	return dict(author=user, user = user, index=index);

@view('blog_edit.html')
@route('/manage/blog/create','get')
def blog_create():
	user = ctx.request.user;
	return dict(author=user,user=user);

@view('blog_edit.html')
@route('/manage/blog/edit/{id}', 'get')
def blog_edit( id ):
	user = ctx.request.user;
	blog = Blog.get_one(id=id);
	return dict(author=user, user=user, blog=blog);

@view('blog_show.html')
@route('/blog/{id}', 'get')
def blog( id ):
	blog = Blog.get_one(id=id);
	author = User.get_one(id=blog.user_id);
	user = ctx.request.user;
	blog.created_at = datetime_filter( blog.created_at );
	return dict(blog = blog, author=author, user=user);

@view('user.html')
@route('/user/{username}', 'get')
def user( name ):
	authors = User.select('where name=%s',name);
	if len(authors) != 1:
		NotFound();
	author = authors[0];
	blogs = Blog.select('where user_id=%s', author.id);
	user = ctx.request.user;
	index = ctx.request.get('page_index');
	print index;
	return dict( blogs=blogs, author=author, user=user, index=index);

@view('home.html')
@route('/home','get')
def home():
	blogs = Blog.get_all();
	users = User.get_all();
	blog_detial = ( (blog,user) for blog in blogs for user in users if blog.user_id == user.id);

	user = ctx.request.user;
	return dict( blogs = blog_detial, user = user );

@route('/static/*','get')
def static_file_route():
	return StaticRoute();

@view('register.html')
@route('/register', 'get')
def register():
	return dict();

@view('signin.html')
@route('/signin', 'get')
def signin():
	return dict();

@intercept('/*')
def check_user():
	user = None;
	cookie = ctx.request.cookie('username');
	if cookie:
		user = parse_signed_cookie( cookie );
	ctx.request.user = user;

# 从 cookie 中获得确认用户信息
def parse_signed_cookie( cookie_str ):
	try:
		L = cookie_str.split('-');
		if len(L) != 3: return None;
		name, expires, md5 = L;
		if int(expires) < time.time(): return None;
		users = User.select('where name=%s ', name);
		if len(users) != 1: return None;
		if md5 != hashlib.md5('%s-%s-%s-%s' %(name, users[0].passwd,expires, _COOKIE_KEY)).hexdigest(): return None;
		return users[0];
	except:
		return None;
