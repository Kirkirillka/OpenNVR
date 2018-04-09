Vue.component('camera',{
    delimiters:['[[',']]'],
    props: ['source'],
    template:"<script>[[ source ]]</script>"
});

Vue.component('child', {
  // определяем входной параметр
  props: ['message'],
  // как и другие данные, входной параметр можно использовать
  // внутри шаблонов (а также и в методах, обращаясь через this.message)
  template: '<span>{{ message }}</span>'
})

const store = new Vuex.Store({
    state:{
        count: 0,
        users:[]
    },
    mutations:{
        increment(state){
            state.count++
        },
        updateUsers(state){
            fetch('/users/get',{credentials: 'include'})
                    .then(response=>response.json())
                    .then(response=>state.users=response);
        }
    }

})

store.commit('updateUser');
console.log(store.state.users)

var app=new Vue({
	el: '#app',
	data:{
		user:{
		    email:'Anonymous',
		    roles:[]
		},
		users:{},
		is_send:0,
		width:320,
		height:240,
		seen:'videosize',
		show:{
			main:false,
			services:false,
			users:false
		},
		sources:{
		    all:[],
		    free:[],
		    enabled:[],
		    picked:''
		},
		services:{

		},
	},
	delimiters: ['[[',']]'],
	created: function (){
	    this.setCurrentUser();
	    this.setUsers()
	    this.setConfig();
		this.setSources();
		this.setServices()
	},
	mounted:function(){
	    this.updateMessages();
	},
	methods:{
		setConfig:function(){
		    fetch('/config/get',{credentials: 'include'}).then(response=>response.json())
		                        .then(response=>function(data){ for(const key in response){app[key]=response[key]}}(response) )
		},
		setServices(){
		    fetch('/services/',{credentials:'include'}).then(response=>response.json()).then(response=>this.services=response);
		},
		setSources:function(){
			var sources=['free','all','enabled']

			sources.forEach(r => fetch('/cam/'+r.toString(),{credentials: 'include'})
			                    .then(response=>response.json())
			                    .then(response=>this.sources[r]=response)
			                    .then(console.log('Success'))
			);
		},
		setCurrentUser:function(){
		    fetch('/users/current',{credentials: 'include'}).then(response=>response.json()).then(response=>this.user=response)
		},
		setUsers(){
		    fetch('/users/get',{credentials:'include'}).then(r=>r.json()).then(r=>this.users=r);
		},
		addCam:function(data){
		    console.log('starting')
		    fetch('/cam/add',{
		        method:"POST",
		        credentials: 'include',
		        headers:{"Content-Type":"application/json",
		                   "Accept":'application/json, text/plain, */*'
		        },
		        body:JSON.stringify(this.sources.picked)
		    }).then(response=>response.json())
		      .then(response=>this.process_message(response))
		      .then(response=>this.setSources());
		},
		delCam:function(name){
		    var deleted=this.sources.enabled.findIndex(a=>a.name=name)
		    this.sources.enabled.splice(deleted,1)
		    fetch('/cam/del',{
		        method:'post',
		        credentials: 'include',
		        headers:{"Content-Type":"application/json",
		                   "Accept":'application/json, text/plain, */*'
		        },
		        body:JSON.stringify({'name':name})
		    }).then(response=>response.json())
		       .then(response=>this.process_message(response))
		       .then(response=>this.setSources());
		},
		delUser(id){
		    if (id ==undefined){
		        console.log('ID is not set');
		        return
		    };
		    var user_founded=this.users.findIndex(a=>a.id==id)
		    if(user_founded != undefined){
		        console.log('User deleted ' +id);
		        this.users.splice(user_founded,1)
		    }else{
		        console.log('Not found');
		    }
		},
		disableUser(id){
		    if (id ==undefined){
		        console.log('ID is not set');
		        return
		    };
		    var user_founded=this.users.find(a=>a.id==id)
		    if(user_founded != undefined){
		        console.log('User status changed ' +id);
		        user_founded.is_enabled=! user_founded.is_enabled;
		    }else{
		        console.log('Not found');
		    }
		},
		reinitialize:function(){
		    this.seen='reinitialize';
		    fetch('config/reinitialize',{credentials: 'include'})
		        .then(response=>response.json())
		        .then(response=>this.process_message(response))
		},
		updateConfig:function(){
		    var params={'height':this.height,
		                'width':this.width};
		    fetch('config/update',{
		        method:'post',
		        credentials: 'include',
		        headers:{"Content-Type":"application/json",
		                   "Accept":'application/json, text/plain, */*'
		        },
		        body:JSON.stringify(params)
		    }).then(response=>response.json())
		        .then(response=>this.process_message(response));
		},
		changeCondService(service,cond){
		    console.log(service,cond);
		    if (cond=='on'){cond='off'}else{cond='on'};
		    fetch('/service',{
                method:'post',
                credentials: 'include',
                headers:{"Content-Type":"application/json",
                           "Accept":'application/json, text/plain, */*'
                },
		        body:JSON.stringify({'name':service,'action':cond})
		    }).then(response=>response.json()).then(response=>this.services[service].status=cond);
		},
		init_cam:function(cam){
            console.log(cam);
		    if(this.sources.enabled.length==0){return false};

		    var canvas = document.getElementById('video-canvas'+cam.name);

			var url = 'ws://'+document.location.hostname+":"+cam.ws_port;
			var player = new JSMpeg.Player(url, {canvas: canvas});

			document.getElementById('start'+cam.name).onclick=function(){player.pause()};
			document.getElementById('pause'+cam.name).onclick=function(){player.play()};

			this.process_message({type:'notify',
			                       message:'Camera #'+cam.name+' was initilized.'
			                      });
		},
		process_message(result){
                alertify.notify(result.message,result.type);
		},
		updateMessages(){
		    fetch('/message/'+this.user.email,{credentials: 'include'}).then(response=>(response.json())).then(response=>console.log(response));
		    setTimeout(this.updateMessages,4000);
		}
	},
	computed: {
		canvas_size:function (){
			return {width:this.width,height:this.height};
		},
	}
})

