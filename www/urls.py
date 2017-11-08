#!/usr/bin/env python
#coding:utf-8

from ToyToolkit.myweb import route,intercept,view,ctx,StaticRoute,SeeOther,NotFound;
from models import User,Blog,Catelog;
import datetime, time, hashlib;

from group import date_filter,df1,df2,get_blogs_cata;

from config.config import configs;

_COOKIE_KEY = configs['session']['secret'];

from group import get_author_info;

@view('index.html')
@route('/','get')
def index():
	return dict();

@view('user.html')
@route('/user/{username}', 'get')
def user( name ):
	authors = User.select('where name=%s',name);
	if len(authors) != 1:
		NotFound();
	author = get_author_info( authors[0].id );
	user = ctx.request.user;
	api = '/api/blogs/'+author.id;
	return dict( api=api, author=author, user=user);

@view('blog_list.html')
@route('/list/{id}','get')
def blog_list( id ):
	user = ctx.request.user;
	author = get_author_info( id );
	api = '/api/blogs-date/'+author.id;
	return dict( api=api, author=author, user = user);

@view('blog_list.html')
@route('/list/{id}/{date}','get')
def blog_list_date( id, date ):
	user = ctx.request.user;
	author = get_author_info( id );
	api = '/api/blogs-date/'+id+'/'+date;
	return dict( api=api, author=author, user = user);

@view('blog_list.html')
@route('/cata/{cataid}','get')
def blog_list_cata( cataid ):
	user = ctx.request.user;
	id = Catelog.get_one(id=cataid).user_id;
	author = get_author_info( id );
	api = '/api/blogs-cata/'+cataid;
	return dict( api=api, author=author, user = user);

@view('blog_edit.html')
@route('/manage/blog','get')
def blog_create():
	user = ctx.request.user;
	author = get_author_info( user.id );
	return dict(author=author ,user=user);

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
	author = get_author_info( blog.user_id );#User.get_one(id=blog.user_id);
	user = ctx.request.user;
	blog.created_at = df1( blog.created_at );
	return dict(blog = blog, author=author, user=user);

@view('home.html')
@route('/home','get')
def home():
	blogs = Blog.get_all();
	users = User.get_all();
	blogs = date_filter( blogs, key=df2);
	blogs = get_blogs_cata( blogs );

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
