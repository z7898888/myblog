#!/usr/bin/env python
#coding:utf-8

"""
一个玩具级的 Web 框架
"""

__author__ = 'ppc';

import json,mimetypes,cgi,datetime,types,os,re,threading,logging,functools;

ctx = threading.local();

_RESPONSE_STATUSES = {

	# Successful
	200: 'OK',

	# Redirection
	301: 'Moved Permanently',
	303: 'See Other',
	307: 'Temporary Redirect',

	# Client Error
	404: 'Not Found',

	# Server Error
	500: 'Internal Server Error',
};

_RESPONSE_HEADERS = (
	'Accept-Ranges',
	'Age',
	'Allow',
	'Cache-Control',
	'Connection',
	'Content-Encoding',
	'Content-Language',
	'Content-Length',
	'Content-Location',
	'Content-MD5',
	'Content-Range',
	'Content-Type',
	'Date',
	'ETag',
	'Expires',
	'Last-Modified',
	'Link',
	'Location',
	'P3P',
	'Pragma',
	'Proxy-Authenticate',
	'Refresh',
	'Retry-After',
	'Server',
	'Set-Cookie',
	'Strict-Transport-Security',
	'Trailer',
	'Transfer-Encoding',
	'Vary',
	'Via',
	'Warning',
	'WWW-Authenticate',
	'X-Frame-Options',
	'X-XSS-Protection',
	'X-Content-Type-Options',
	'X-Forwarded-Proto',
	'X-Powered-By',
	'X-UA-Compatible'
);

_RESPONSE_HEADER_DICT = dict(zip(map(lambda x: x.lower(), _RESPONSE_HEADERS), _RESPONSE_HEADERS));

def _getResponseHeader( header ):
	"""
	返回Response Header，若是在表中没有找到对应的，则返回本身
	>>> _getResponseHeader('CONTENT-TYPE')
	'Content-Type'
	"""
	return _RESPONSE_HEADER_DICT.get(header.lower(), header);

class HttpError( Exception ):
	"""
	HttpError that defines http error code.
	>>> e = HttpError(404);
	>>> e.status
	'404 Not Found'
	"""
	def __init__(self, code):
		"""
		Init an HttpError with response code.
		"""
		self.status = '%d %s'%(code, _RESPONSE_STATUSES[code]);
		self._headers = [];
	
	def set_header( self, name, value):
		key = _getResponseHeader( name );
		self._headers.append((key, value));

	@property
	def headers( self ):
		return self._headers;

	def __str__( self ):
		return self.status;

	__repr__ = __str__;

def SeeOther( url ):
	r = HttpError( 303 );
	for k,v in ctx.response.headers:
		r.set_header(k,v);
	r.set_header('Location', url);
	raise r;

def Redirect( url ):
	r = HttpError(307);
	r.set_header('Location', url);
	raise r;

def NotFound():
	"""
	Send a not found response.
	>>> NotFound();
	Traceback (most recent call last):
		...
	HttpError: 404 Not Found
	"""
	raise HttpError(404)

class Response:
	def __init__( self ):
		self._header = {'Content-Type' : 'text/html'};
		self._status = "200 OK";

	@property
	def status( self ):
		"""
		Return response status.
		>>> r = Response();
		>>> r.status
		'200 OK'
		"""
		return self._status;

	@property
	def headers( self ):
		"""
		Return response headers as [(key1, value), (key2, value)...] includecookies.
		>>> r = Response();
		>>> r.headers;
		[('Content-Type', 'text/html')]
		"""
		L = [tuple([k,v]) for k,v in self._header.items()];
		if hasattr(self, '_cookies'):
			for v in self._cookies.values():
				L.append(('Set-Cookie',v));
		return L;

	def header( self, name):
		"""
		Get header by name, case-insensitive.
		>>> r = Response();
		>>> r.header('content-type');
		'text/html'
		"""
		key = _getResponseHeader( name );
		return self._header.get(key);

	def set_header( self, name, value):
		"""
		set header by name and value.
		>>> r = Response();
		>>> r.set_header('content-type','image/png');
		>>> r.header('content-TYPE');
		'image/png'
		"""
		key = _getResponseHeader( name );
		self._header[key] = value;

	def unset_header( self, name):
		"""
		unset header by name and value.
		>>> r = Response()
		>>> r.header('cOntEnt-TyPe')
		'text/html'
		>>> r.unset_header('CONTent-type');
		>>> r.header('content-type');
		"""
		key = _getResponseHeader( name );
		if key in self._header:
			del self._header[key];

	def set_cookie( self, name, value, max_age=None, expires=None, path='/',domain=None, secure=False, http_only=True):
		"""
		Set a cookie.
		Args:
			name: the cookie name.
			value: the cookie value.
			max_age: optional, seconds of cookie's max age.
			expires: optional, unix timestamp, datetime of date object that indicate an absolute time of the expiration time of cookie. Note that if expires specified, the max_age will be ignored.
			path: the cookie path, default to '/'.
			domain: the cookie domain, default to False.
			secure: if the cookie secure, default to False.
			http_only: if the cookie if for http only, default to True for better safty (client-side script cannot access cookies with HttpOnly flag).
		>>> r = Response();
		>>> r.set_cookie('company','Abc, Inc.', max_age=3600);
		>>> r._cookies
		{'company': 'company=Abc, Inc.; Max-Age=3600; Path=/; HttpOnly'}
		>>> r.set_cookie('company','Abc, Inc.', expires=0, path='/sub/');
		"""
		if not hasattr( self, '_cookies'):
			self._cookies = {}
		L = ['%s=%s'%(name,value)];
		if expires is not None:
			if isinstance(expires, (float, int, long)):
				L.append('Expires=%s'%datetime.datetime.fromtimestamp(expires).strftime('%a, %d-%b-%Y %H:%M:%S GMT'));
		elif isinstance(max_age, (int, long)):
			L.append('Max-Age=%d'%max_age);
		L.append('Path=%s'%path);
		if domain:
			L.append('Domain=%s'%domain);
		if secure:
			L.append('Secure');
		if http_only:
			L.append('HttpOnly');
		self._cookies[name] = '; '.join(L);

	def delete_cookie( self, name):
		"""
		Delete a cookie immediately.
		Args:
			name: the cookie name.
		"""
		self.set_cookie(name, '__deleted__', expires=0);

def _2str( s ):
	"""
	Conver to str.
	>>> _2str('s123') == 's123'
	True
	>>> _2str(u'\u4e2d\u6587') == '\xe4\xb8\xad\xe6\x96\x87'
	True
	>>> _2str(-123) == '-123';
	True
	"""
	if isinstance(s, str): return s;
	if isinstance(s, unicode): return s.encode('utf-8');
	return str(s);

def _2unicode( s, encoding='utf-8'):
	"""
	Convert to unicode.
	>>> _2unicode('\xe4\xb8\xad\xe6\x96\x87') == u'\u4e2d\u6587'
	True
	"""
	return s.decode( encoding );

class MultipartFile:
	"""
	Multipart file storage get from request input.
	f = ctx.request['file']
	f.filename # 'test.png'
	f.file # file-like object
	"""
	def __init__( self, storage ):
		self.filename = _2unicode( storage.filename)
		self.file = storage.file

class Request:
	"""
	Request object for obtaining all http request infomation.
	"""
	def __init__( self, environ ):
		self._environ = environ;

	def _parse_input( self ):
		def _convert( item ):
			if isinstance( item, list):
				return [_2unicode(i.value) for i in item];
			if item.filename:
				return MultipartFile( item );
			return _2unicode(item.value);
		fs = cgi.FieldStorage(fp=self._environ['wsgi.input'],
				environ=self._environ,
				keep_blank_values=True)
		inputs = dict();
		for key in fs:
			inputs[key] = _convert(fs[key]);
		return inputs;

	def _get_raw_input( self ):
		"""
		Get raw input as dict containing values as unicode, list or MultipartFile.
		"""
		if not hasattr(self, '_raw_input'):
			self._raw_input = self._parse_input();
		return self._raw_input;

	def get( self, key, default=None ):
		"""
		The same as request[key], but return default value if key is not found.
		"""
		r = self._get_raw_input().get(key, default);
		if isinstance(r, list):
			return r[0];
		return r;

	@property
	def path_info( self ):
		return self._environ.get('PATH_INFO','');

	@property
	def request_method( self ):
		return self._environ['REQUEST_METHOD'];

	def _get_cookies( self ):
		if not hasattr( self, '_cookies'):
			cookies = {}
			cookie_str = self._environ.get('HTTP_COOKIE')
			if cookie_str:
				for c in cookie_str.split(';'):
					pos = c.find('=')
					if pos>0:
						cookies[c[:pos].strip()] = _2unicode(c[pos+1:]);
			self._cookies = cookies;
		return self._cookies;

	@property
	def cookies( self ):
		"""
		Return all cookies as dict. The cookie name is str and values is unicode.
		>>> r = Request({'HTTP_COOKIE':'A=123; url=http://www.example.com'})
		>>> r.cookies['A']
		u'123'
		>>> r.cookies['url']
		u'http://www.example.com'
		"""
		return dict(**self._get_cookies());

	def cookie(self, name , default=None):
		"""
		Return specified cookie value as unicode.Default to None if cookie not exists.
		>>> r = Request({'HTTP_COOKIE':'A=123;url=http://www.example.com'})
		>>> r.cookie('A')
		u'123'
		"""
		return self._get_cookies().get(name,default);

class Method:
	"""
	映射方法和方法编码

	>>> Method.get
	1
	"""
	get = 1;
	post = 2;
	intercept = 4;

	_map = {"get" : get,
		"post" : post,
		"intercept" : intercept}

	@classmethod
	def _str2code( cls, name ):
		tmp = name.lower();
		if tmp in cls._map:
			return cls._map[tmp];
		else: raise ValueError('值必须是 get,post 或者 intercept');

	
	@classmethod
	def getMethodCode( cls, name ):
		"""
		根据字符串或者整形获取代码

		>>> Method.getMethodCode('GEt');
		1
		>>> Method.getMethodCode(6);
		6
		>>> Method.getMethodCode('post');
		2
		>>> Method.getMethodCode('ok');
		Traceback (most recent call last):
			...
		ValueError: 值必须是 get,post 或者 intercept
		>>> Method.getMethodCode(['get','post']);
		3
		"""
		if isinstance( name, str):
			return cls._str2code(name);
		if isinstance( name, list):
			ret = 0;
			for s in name:
				ret |= cls._str2code( s );
			return ret;
		if isinstance( name, int):
			if name > 0 and name < 8: return name
			else: raise ValueError('请求方法代码在 1 ~ 7 之间');
		raise ValueError('无效的输入参数类型:%s'%type(name));

class ChainEntry( object ):
	def __init__( self, path, func ):
		self._path = path;
		self._path_pattern = re.compile(
				self._genPatterString( path ) );
		self._func = func;
		self._next_entry = None;

	def __str__( self ):
		return 'path:%s , function:%s'%(self._path, self._func.__name__);
		
	def addEntry( self, entry ):
		if self._next_entry == None:
			self._next_entry = entry;
		else:
			self._next_entry.addEntry( entry );

	args_patter = re.compile('\\\{\w+\\\}');
	@classmethod
	def _genPatterString( cls, mothod_patter ):
		"""
		将自定义的方法模式串转换为正则模式串

		>>> ms = '/{id}/paper?dest=123';
		>>> print ChainEntry._genPatterString(ms);
		^\/([\w|-]+)\/paper\?dest\=123$
		>>> print ChainEntry._genPatterString('/static/*');
		^\/static\/.*$
		"""
		mstr = re.escape(mothod_patter);
		mstr = cls.args_patter.sub('([\w|-]+)', mstr);
		mstr = mstr.replace('\*','.*');
		return '^' + mstr + '$';

	def _isMatch( self, path ):
		"""
		根据正则字符串将匹配到的参数返回
		"""
		match = self._path_pattern.match( path );
		if match:
			return match.groups();

	def intercept( self, path ):
		args = self._isMatch( path );
		if args != None:
			if self._func( *args ) == True: return True;
		if self._next_entry is None: return False;
		return self._next_entry.intercept( path );

class RouteEntry( ChainEntry ):
	def __init__( self, path, method, func):
		"""
		>>> re = RouteEntry('/', Method.get | Method.post, None );
		>>> print re._method;
		3
		"""
		super(RouteEntry, self).__init__(path, func);
		self._method = Method.getMethodCode( method );
	
	def __str__( self ):
		return 'path:%s , method:%s , function:%s'%(
				self._path, self._method, self._func.__name__);
	
	def route( self, path, method ):
		"""
		根据路径和方法开始路由

		>>> def Func1( name ):
		...		print 'execute Func1(), args:', name;
		...		return '<h1>Func1</h1>';
		>>> def Func2():
		...		return '<h2>Func2</h2>';
		>>> re = RouteEntry('/{name}/',Method.intercept, Func1);
		>>> re.addEntry( RouteEntry('/aindex', Method.post, Func2) );
		>>> print re.route('/aindex', 'post');
		<h2>Func2</h2>
		"""
		args = self._isMatch( path );
		if args != None: # 如果路径匹配成功
			code = Method.getMethodCode( method );
			if code & self._method : # 如果方法匹配成功
				return self._func( *args );
		if self._next_entry: # 如果还有下一个路由表项，继续路由
			return self._next_entry.route( path, method );
		NotFound(); # 所有的路由表项全部遍历，仍然没有找到

def _static_file_read( file_pos ):
	READ_SIZE = 8192
	with open(file_pos, 'rb') as fin:
		chuck = fin.read(READ_SIZE);
		while chuck:
			yield chuck
			chuck = fin.read(READ_SIZE);

def StaticRoute():
	root = ctx.app.document_root;
	fpath = ctx.request.path_info;
	absfpath = os.path.join(root, fpath[1:]);
	fext = os.path.splitext(fpath)[1];
	content_type = mimetypes.types_map.get(fext.lower(), 'application/octet-stream');
	ctx.response.set_header('content-type', content_type);
	return _static_file_read( absfpath );

def route( path, method ):
	"""
	一个路由装饰器，在函数上标记标记路径、方法

	>>> @route('/test/view.html', Method.get | Method.post)
	... def hello():
	...		return 'hello, world!';
	>>> hello.__route_path__
	'/test/view.html'
	>>> hello.__route_method__
	3
	>>> hello();
	'hello, world!'
	>>> hello.__name__
	'hello'
	"""
	def _decorator( func ):
		func.__route_path__ = path;
		func.__route_method__ = method;
		return func;
	return _decorator;

def intercept( path ):
	def _decorator( func ):
		func.__intercept_path__ = path;
		return func;
	return _decorator;

class Template:
	def __init__( self, template_name, **kw):
		"""
		Init a template object with template name, model as dict, and additional kw that append to model.
		>>> t = Template('hello.html', title='Hello', copyright='@2012')
		>>> t.model['title']
		'Hello'
		>>> t.model['copyright']
		'@2012'
		>>> t = Template('test.html', abc=u'ABC', xyz=u'XYZ');
		>>> t.model['abc'];
		u'ABC'
		"""
		self.template_name = template_name;
		self.model = dict( **kw );

class TemplateEngine( object ):
	"""
	Base template engine.
	"""
	def __call__( self, path, model ):
		return '<!-- override this method to render template -->';

class Jinja2TemplateEngine( TemplateEngine ):
	"""
	Render using jinja2 template engine.
	>>> import datetime
	>>> templ_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'test');
	>>> engine = Jinja2TemplateEngine( templ_path );
	>>> engine.add_filter('datetime', lambda dt: dt.strftime('%Y-%m-%d %H:%M:%S'));
	>>> engine('test.html',dict( name = 'dean', posted_at = datetime.datetime(2017,5,23,20,55,44)));
	'<p>hello, dean</p><span>2017-05-23 20:55:44</span>'
	"""
	def __init__( self, templ_dir, **kw):
		from jinja2 import Environment, FileSystemLoader;
		if not 'autoescape' in kw:
			kw['autoescape'] = True;
		self._env = Environment( loader=FileSystemLoader( templ_dir), **kw)

	def add_filter( self, name, fn_filter):
		self._env.filters[name] = fn_filter;

	def __call__( self, path, model):
		return self._env.get_template(path).render(**model).encode('utf-8')

def view( path ):
	"""
	A view decorator that render a view by dict.
	>>> @view('test/view.html')
	... def hello():
	...		return dict(name='Bob');
	>>> t = hello();
	>>> isinstance(t, Template);
	True
	>>> t.template_name
	'test/view.html'
	>>> t.model['name']
	'Bob'
	>>> @view('test/view.html')
	... def hello2():
	...		return ['a list'];
	>>> t = hello2();
	Traceback (most recent call last):
		...
	ValueError: Expect return a dict when using @view() decorator.
	"""
	def _decorator( func ):
		@functools.wraps(func)
		def _wrapper(*args, **kw):
			r = func(*args, **kw)
			if isinstance( r, dict):
				logging.info('Add Template: path:%s, function:%s'%(path,func.__name__));
				return Template( path, **r);
			raise ValueError('Expect return a dict when using @view() decorator.');
		return _wrapper;
	return _decorator;

class APIError( Exception ):
	def __init__( self, error, data, message ):
		super(APIError, self).__init__(message);
		self.error = error;
		self.data = data;

def api( func ):
	@functools.wraps( func )
	def _wrapper( *args, **kw):
		try:
			r = json.dumps( func(*args, **kw) );
		except APIError, e:
			r = json.dumps( dict(error=e.error, data=e.data, message=e.message) );
		except Exception, e:
			r = json.dumps( dict(error='internalerror', data=e.__class__.__name__, message=e.message) );
		ctx.response.set_header('content-type','application/json');
		return r
	return _wrapper;

def _load_module( module_name ):
	"""
	Load module from name as str.
	>>> m = _load_module('xml')
	>>> m.__name__
	'xml'
	>>> m = _load_module('xml.sax')
	>>> m.__name__
	'xml.sax'
	>>> m = _load_module('xml.sax.handler')
	>>> m.__name__
	'xml.sax.handler'
	"""
	last_dot = module_name.rfind('.');
	if last_dot == (-1):
		return __import__(module_name, globals(), locals());
	from_module = module_name[:last_dot];
	import_module = module_name[last_dot+1:];
	m = __import__(from_module, globals(), locals(), [import_module]);
	return getattr(m, import_module);

class WSGIApplication:
	def __init__( self, document_root = None ):
		self._route = None;
		self._intercept = None;
		self._template_engine = None;
		self._document_root = document_root;

	@property
	def document_root( self ):
		return self._document_root;

	@property
	def template_engine( self ):
		return self._template_engine;

	@template_engine.setter
	def template_engine( self, engine):
		self._template_engine = engine;

	def add_module( self, mod ):
		m = mod if type(mod) == types.ModuleType else _load_module(mod);
		logging.info('Add module: %s'%m.__name__);
		for name in dir(m):
			fn = getattr(m, name);
			self.add_url( fn );
			self.add_intercept( fn );

	def add_url( self, func ):
		if hasattr(func,'__route_path__') and \
			hasattr(func,'__route_method__'):
			tmp = RouteEntry(
					func.__route_path__,
					func.__route_method__,
					func);
			if self._route is None: self._route = tmp;
			else: self._route.addEntry( tmp );
			logging.info('Add route: %s'%str(tmp));

	def add_intercept(self, func ):
		if hasattr(func, '__intercept_path__'):
			tmp = ChainEntry(func.__intercept_path__, func);
			if self._intercept is None: self._intercept = tmp;
			else: self._intercept.addEntry( tmp );
			logging.info('Add intercept: %s'%str(tmp));

	def run( self, host='localhost', port=9000):
		from wsgiref.simple_server import make_server;
		server = make_server( host, port,
				self.get_wsgi_application( debug = True ));
		server.serve_forever();

	def get_wsgi_application( self, debug = False ):
		def start_route( path, method ):
			ret = [];
			if self._intercept != None: # 如果有拦截器
				if self._intercept.intercept( path ): # 如果被拦截器拦截
					return ret;

			if self._route != None: # 如果有路由表项
				ret = self._route.route( path, method ); #开始路由
				if isinstance( ret, Template): # 返回的路由结果如果是模板
					ret = self.template_engine( ret.template_name, ret.model );
			return ret;

		def wsgi( env, start_response ):
			ctx.app = self;
			ctx.request = Request( env );
			response = ctx.response = Response();
			path = ctx.request.path_info;
			method = ctx.request.request_method;
			try:
				ret = start_route( path, method );
				start_response(response.status, response.headers);
				return ret;
			except HttpError, e:
				start_response(e.status, e.headers);
				return ['<html><body><h1>',e.status,'</h1></body></html>'];
			except Exception, e:
				logging.exception(e);
				start_response('500 Internal Server Error',[]);
				return r'''<html><body><h1>500 Internal Error</h1></bdoy></html>''';
			finally:
				del ctx.app;
				del ctx.request;
				del ctx.response;

		return wsgi;

if __name__ == '__main__':
	import doctest;
	doctest.testmod();
