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
				}
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

var editor = null;
function getEditorComp(){
	var template = [
"<div class='uk-modal-dialog uk-modal-dialog-blank' style='height:100%'>",
	"<div class='uk-width-1-2 uk-container-center uk-panel-box'>",
	"<a id='mdlg-close'class='uk-modal-close uk-close uk-align-right'></a>",
	"<div v-if='updated' class='uk-form uk-form-stacked' >",
		"<div class='uk-form-row'>",
			"<input placeholder='标题' v-model='title' />",
		"</div>",
		"<div class='uk-form-row'>",
			"<div class='uk-form-controls'>",
				"<textarea rows='3' class='uk-width-1-1' placeholder='简介' v-model='summary'></textarea>",
			"</div>",
		"</div>",
		"<div class='uk-form-row'>",
			"<textarea id='editor' ></textarea>",
			"<textarea v-model='content' style='display:none'></textarea>",
		"</div>",
		"<div class='uk-form-row'>",
			"<button class='uk-button uk-button-primary'>保存</button>",
			"<a href='#' v-on:click='save'>test</a>",
		"</div>",
	"</div>",
	"</div>",
"</div>"
	].join('');

	var blogEditor = {
		props : ['blog'],
		data:function(){ 
			return {
				title:'',id:'',summary:'',content:'',
			} 
		},
		methods : {
			save: function(){
				console.log('save');
				var api = '/api/blog/save'+this.id;
				this.content = editor.currentvalue;
				var data = { 
					title:this.title,
					summary:this.summary,
					content:this.content
				};
				postWebAPI( api, data, this.save_ok );
			},
			save_ok: function( data ) {
				if( data.result == 'ok' ) {
					$('#mdlg-close').trigger('click');
					this.$emit('update');
				}
			}
		},
		computed : {
			isnew: function(){
				return this.blog === null;
			},
			updated: function(){
				var flag = this.isnew;
				this.id = flag ? '' : '/'+this.blog.id;
				this.title = flag ? '' : this.blog.title;
				this.summary = flag ? '' : this.blog.summary;
				this.content = flag ? '' : this.blog.content;
				if( editor != null) {
					editor.editor.setValue(flag?'':this.content);
				}
				return true;
			}
		},
		created: function(){
			this.$nextTick( function(){
				editor = UIkit.htmleditor('#editor',
					{markdown:true,height:'300px'});
			});
		},
		template: template
	}
	return blogEditor;
}

function getCatalogComp(){
	var template = [
"<li>",
	"{{catalog.name}}",
	"&nbsp<a href='#' v-on:click='insert(catalog)'><i class='uk-icon-plus'></i></a>",
	"&nbsp<a href='#' v-on:click='remove(catalog.id)'><i class='uk-icon-close'></i></a>",
	"<ul v-for='cata in catalog.catas'>",
		"<li is='catalog' :catalog='cata' @insert='insert' @remove='remove'></li>",
	"</ul>",
"</li>"
	].join('');

	var baseConfig = {
		props : ['catalog'],
		template : template,
		methods:{
			'insert': function( catalog ){
				this.$emit('insert', catalog);
			},
			'remove': function( cid){
				this.$emit('remove',cid);
			}
		}
	}

	baseConfig['components']={'catalog':baseConfig};

	return baseConfig;
}
