function login( data ){
	if( data.error ) {
		$('#err_info').text( data.message );
		return false;
	}

	location.href = data.url;
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

var vm = null;

function initBlogsVM(data){
	$('#div-blogs').show();
	if(vm === null){
		vm = new Vue({
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
	} else {
		vm.blogs = data.blogs;
		vm.page = data.page;
	}
}

function getBlogsByPage( webapi, index, size ){
	console.log('webapi:'+webapi);
	var data={page_index:index, page_size:size};
	getWebAPI( webapi, data, initBlogsVM);
}

function endAJAX( state , func){
	state.done(
		function (data){
			if(data.error){
				if(data.error ==='internalerror')
					alert('错误原因:'+data.error+'\n错误模块:'+data.data+'\n错误描述:'+data.message);
				else
					alert('错误原因:'+data.error+'\n错误描述:'+data.message);
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
