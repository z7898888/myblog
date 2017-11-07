#!/usr/bin/env python
#coding:utf-8

from ToyToolkit.myweb import route,api,ctx,APIError,intercept,SeeOther;
from models import User,Blog;
from uuid import uuid1;
import datetime,time, hashlib;

from config.config import configs;

_COOKIE_KEY = configs['session']['secret'];

from group import get_blogs_and_page, df1, df2;

@api
@route('/api/blogs/{id}', 'get')
def api_get_blogs( id ):
	blogs, page = get_blogs_and_page( id , key=df1);
	return dict(blogs = blogs, page = page.obj2dict());

@api
@route('/api/blogs-date/{id}','get')
def api_get_blogs_by_date( id ):
	key = lambda x:datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M');
	blogs, page = get_blogs_and_page(id , key=df2);
	return dict(blogs=blogs, page=page.obj2dict());

@api
@route('/api/blogs-date/{id}/{date}','get')
def api_get_blogsd_by_date( id, date ):
	blogs, page = get_blogs_and_page(id, date, key=df2);
	return dict(blogs=blogs, page=page.obj2dict());

@api
@route('/api/blogs-cata/{cataid}','get')
def api_get_blogs_by_cataid( cataid ):
	blogs, page = get_blogs_and_page(cata=cataid, key=df2);
	return dict(blogs=blogs, page=page.obj2dict());

@intercept('/manage/*')
def check_private():
	user = ctx.request.user;
	if user is None:
		SeeOther('/signin');

def get_userid():
	user = ctx.request.user;
	if user is None:
		raise APIError('invaild:user','','无效用户');
	return user.id;

def get_blog():
	title = ctx.request.get('title').encode('utf-8');
	summary = ctx.request.get('summary').encode('utf-8');
	content = ctx.request.get('content').encode('utf-8');
	if not title:
		raise APIError('title','','标题不能为空');
	if not summary:
		raise APIError('summary','','简介不能为空');
	if not content:
		raise APIError('content','','内容不能为空');
	return title,summary,content;

@api
@route('/api/blog/save', 'post')
def api_create_blog():
	title,summary,content = get_blog();
	userid = get_userid();
	blog = Blog(id=uuid1(), title=title.strip(), summary=summary.strip(), content=content.strip(), user_id= userid, created_at=time.time());
	blog.insert();
	return dict(result='ok');

@api
@route('/api/blog/save/{id}', 'post')
def api_save_blog_by_id( id ):
	title,summary,content = get_blog();
	userid = get_userid();
	blog = Blog.get_one( id = id );
	if blog.user_id != userid:
		raise APIError('user_id','','用户ID异常');
	blog.title = title;
	blog.summary = summary;
	blog.content = content;
	blog.update();
	return dict(result='ok');

@api
@route('/api/blog/delete/{id}','get')
def api_delete_blog_by_id( id ):
	userid = get_userid();
	blog = Blog.get_one( id = id );
	if blog.user_id != userid:
		raise APIError('user_id','','用户ID异常');
	blog.delete();
	return dict(result='delete');

@api
@route('/api/blog/{id}', 'get')
def api_get_blog( id ):
	blog = Blog.get_one(id = id);
	return blog;

@api
@route('/api/signout','get')
def signout():
	ctx.response.delete_cookie('username');
	return dict( result='signout' );

@api
@route('/api/signin', 'post')
def signin():
	name = ctx.request.get('username');
	password = ctx.request.get('password');

	users = User.select('where name=%s', name);

	if len(users) != 1:
		raise APIError('username error','','用户名异常');
	user = users[0];
	
	if user.passwd != password:
		raise APIError('password error','','密码错误');

	max_age = 3600;
	cookie = make_signed_cookie(name, password, max_age).encode('utf-8');
	ctx.response.set_cookie('username', cookie, max_age=max_age);
	
	url = '/list/'+user.id;
	
	return dict(role=user.role, url=url);

def make_signed_cookie(name, password, max_age):
	expires = str(int(time.time() + max_age));
	L = [name, expires, hashlib.md5('%s-%s-%s-%s'%(name, password, expires, _COOKIE_KEY)).hexdigest()];
	return '-'.join( L );
