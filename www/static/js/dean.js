function login( data ){
	if( data.error ) {
		$('#err_info').text( data.message );
		return false;
	}

	location.href = '/manage/blog';
}

function check( form ){
	if(form.username.value == ''){
		alert('用户名不能为空');
		form.username.focus();
		return false;
	}

	if(form.password.value == ''){
		alert('密码不能为空');
		form.password.focus();
		return false;
	}

	var jqxhr = $.post('/api/signin',{
		username: form.username.value,
		password: form.password.value
	}).done(login);
}

function logout(){
	$.get('/api/signout').done(
		function( data ){
			if( data.result == 'signout') location.href='/home';
		}
	);
}

function delBlog( id ){
	console.log('delete');
	getWebAPI('/api/blog/delete/'+id, null,
			function (data){
				if(data.result==='delete') location.href='/manage/blog';
			}
	);
}

function initBlogsVM(data){
	$('#div-blogs').show();
	var vm = new Vue({
		el:'#div-blogs',
		data:{
			blogs: data.blogs,
			page: data.page
		},
		methods:{
			previous:function(){
				return this.page.page_index - 1;
			},
			next:function(){
				return this.page.page_index + 1;
			},
			del:delBlog
		}
	});
}

function getBlogsByPage( webapi, index, size ){
	var data={page_index:index, page_size:size};
	getWebAPI( webapi, data, initBlogsVM);
	/*
	$.get( webapi ,{
		page_index: index,
		page_size:size
		}).done(
		function(data){
			if(data.error){
				alert(data.message);
			}else{
				initBlogsVM(data);
			}
		}
	);
	*/
}

function endAJAX( state , func){
	state.done(
		function (data){
			if(data.error){
				if(data.error ==='internalerror')
					alter('错误原因:'+data.error+'\n错误模块:'+data.data+'\n错误描述:'+data.message);
				else
					alter('错误原因:'+data.error+'\n错误描述:'+data.message);
			}else{
				func( data );
			}
		}
	).fail(
		function( xhr, status){
			alert('失败:'+xhr.status+'，原因：'+status);
		}
	);
}

function getWebAPI( url, data, func ){
	endAJAX($.get( url, data ), func);
}

function postWebAPI(url, data, func ){
	endAJAX($.post( url, data), func);
}
