from fastapi import FastAPI, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.endpoints import WebSocketEndpoint, HTTPEndpoint
from starlette.responses import HTMLResponse
from starlette.routing import Route, WebSocketRoute
import datetime, ast, random, time, json
from typing import List, Optional
from pydantic import BaseModel
from redis import StrictRedis, ConnectionPool, Redis
redis_db0 = StrictRedis(connection_pool=ConnectionPool( host='localhost', port=6379, db=4))
redis_db1 = StrictRedis(connection_pool=ConnectionPool( host='localhost', port=6379, db=5))

info = {}
socket_user = {}
msg_dict = {}
msg_txt = {}

html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Chat</title>
        </head>
        <body>
            <h1>WebSocket Chat</h1>
            <div style="width: 200px;height: 300px;display: grid;">
                <ul id='user_list'></ul>
            </div>
            <div style="width: 400px;height: 300px;display: grid;">
                <form action="" onsubmit="sendMessage(event)">
                    <select name="" id="class_">
                        <caption>101</caption>
                        <caption>102</caption>
                        <caption>103</caption>
                    </select>
                    <input type="text" id="messageText" autocomplete="off" placeholder="" />
                    <button>Send</button>
                </form>
                <ul id='messages'>
            </div>
            </ul>
            <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
            <script>		
                document.getElementById("messageText").placeholder = "第一次输入内容为昵称";

                var ws = new WebSocket("ws://localhost:8000/ws");
                var count = 0;
                var appId = '101';
                var person = '';
                var user_list = [];

                // ws.onopen = function(evt) {
                // 	console.log("Connection open ...");
                // 	person =  getName();
                // 	console.log("用户准备登陆:" + person);
                // 	ws.send('{"seq":"' + sendId() + '","cmd":"login","data":{"userId":"' + person + '","appId":'+ appId +'}}');
                // 	setInterval(heartbeat, 30 * 1000)
                // };

                // 接收
                ws.onmessage = function (event) {
                    res = JSON.parse( event.data )
                    if (count == 1) {
                        console.log(event.data)
                    }
                    console.log(typeof res,res)
                    if (res['cmd']!='heartbeat'){
                        msg = res['data']['userId']+': '+ res['data']['msg']+'-->'+ res['seq']
                        // 获取id为messages的ul标签内
                        var messages = document.getElementById('messages');
                        // 创建li标签
                        var message = document.createElement('li');
                        // 创建内容
                        var content = document.createTextNode(msg);
                        // 内容添加到li标签内
                        message.appendChild(content);
                        // li标签添加到ul标签内
                        messages.appendChild(message);
                    }
                };

                // 发送			
                function sendMessage(event) {
                    console.log(count);
                    var input = document.getElementById("messageText");
                    if (count == 0) {
                        // 发送昵称
                        var msg_data = {'seq': sendId(), 'cmd': "login", 'data': {'userId': input.value, 'appId': appId}}
                        ws.send(JSON.stringify(msg_data) );
                        setInterval(heartbeat, 30 * 1000);
                        document.getElementById("messageText").placeholder = "";
                        count = parseInt(count) + 1;
                        person = input.value;
                    } else {
                        console.log('count', input.value, person);
                        sendmsg(input.value, appId, person);
                    }
                    input.value = ''
                    event.preventDefault()
                };
                function sendmsg(msg, appId, person) {
                    if (msg != "") {
                        var data = {
                            appId: appId,
                            userId: person,
                            msgId: sendId(),
                            message: msg,
                            }
                        axios.post('http://127.0.0.1:8000/send_msg', data)
                        .then(function (response) {
                            console.log(response);
                        })
                        .catch(function (error) {
                            console.log(error);
                        });
                    }
                };
                function sendId() {
                    let timeStamp = currentTime();
                    let randId = randomNumber(100000, 999999);
                    let id = timeStamp + "-" + randId;
                    return id
                }
                function currentTime() {
                    let timeStamp = (new Date()).valueOf();
                    return timeStamp
                }
                function randomNumber(minNum, maxNum) {
                    switch (arguments.length) {
                        case 1:
                            return parseInt(Math.random() * minNum + 1, 10);
                            break;
                        case 2:
                            return parseInt(Math.random() * (maxNum - minNum + 1) + minNum, 10);
                            break;
                        default:
                            return 0;
                            break;
                    }
                }
                // 获取该房间在线人的信息
                function get_userlist() {
                    axios.get('http://127.0.0.1:8000/get_userlist')
                    .then(function (response) {
                        // 获取id为messages的ul标签内
                        var messages = document.getElementById('user_list');
                        var res = [];
                        for (const key in response['data']['101']) {
                            res.push(key)
                        }
                        console.log('101',res)
                        var cha = res.filter((val)=>!new Set(user_list).has(val));
                        if (cha){
                            for (const key in cha) {					
                                // 创建li标签
                                var message = document.createElement('li');
                                // 创建内容
                                var content = document.createTextNode(cha[key] );
                                // 内容添加到li标签内
                                message.appendChild(content);
                                // li标签添加到ul标签内
                                messages.appendChild(message);
                                user_list.push(cha[key]);
                            };
                        }				
                        // timerId = setTimeout(get_userlist, 5000);
                    })
                    .catch(function (error) {
                        console.log(error);
                    });
                };
                setInterval(get_userlist, 30 * 1000);
                // 心跳函数
                function heartbeat() {
                    console.log("定时心跳:" + person);
                    ws.send('{"seq":"' + sendId() + '","cmd":"heartbeat","data":{}}');
                }		
                // 跑websocket并发和压测
                // async function load_add () {
                // 	var ws = new WebSocket("ws://localhost:8000/ws");
                // 	count = parseInt(count) + 1;
                // 	var content = "我是小大"+count;
                // 	console.log(content, typeof content)
                // 	//添加事件监听
                // 	ws.addEventListener('open', function () {
                // 		ws.send(content)
                // 	});
                // 	timerId = setTimeout(load_add, 100)
                // }
                // load_add()
            </script>
        </body>
    </html>
"""

class Homepage(HTTPEndpoint):
    async def get(self, request):
        return HTMLResponse(html)

# WebSocket工具类
class Echo(WebSocketEndpoint):
    encoding = "text"

    # 修改socket,获取该会话临时key
    async def alter_socket(self, websocket):
        socket_str = str(websocket)[1:-1]
        socket_list = socket_str.split(' ')
        socket_only = socket_list[3]
        return socket_only

    # 获取序列化信息
    async def get_appid(self, websocket):
        msg_ = await websocket.receive_text()
        print('获取序列化信息',type(msg_))
        msg = ast.literal_eval(msg_)
        return msg

    # 连接 存储
    async def on_connect(self, websocket):
        await websocket.accept()
        # 用户输入名称
        msg = await self.get_appid(websocket)
        print("连接 存储", msg)
        name = msg['data']['userId']
        appid = msg['data']['appId']
        socket_only = await self.alter_socket(websocket)
        socket_user[socket_only] = [name, appid]
        # 添加连接池 ,按是否群聊，保存用户名
        if appid not in info:
            info[appid] = {}
        info[appid][name] = websocket
        # 添加消息结构体池
        if appid not in msg_dict:
            msg_dict[appid] = {}
        msg_dict[appid][name] = [f"{name}-加入了聊天室:{appid}"]
        # 添加消息记录池
        if appid not in msg_txt:
            msg_txt[appid] = []
        msg_txt[appid].append(f"{name}_加入了聊天室:{appid}")
        # print("连接 存储", socket_only, info, msg_dict, msg_txt)
        # 先循环 告诉之前的用户有新用户加入了
        res_data = {'seq': sendId(), 'cmd': 'login', 'data': { 'msg': '加入了聊天室', 'userId': name, 'appId': appid }}
        for wbs in info[appid]:
            await info[appid][wbs].send_text(json.dumps(res_data))

    # 收发
    async def on_receive(self, websocket, data):
        socket_only = await self.alter_socket(websocket)
        res = socket_user[socket_only]
        msg = await self.get_appid(websocket)
        print(msg)
        if msg['cmd'] == 'heartbeat':       #心跳💗
            res_data = {'seq': msg['seq'], 'cmd': msg['cmd'], 'response': { 'code': 200, 'codeMsg': "Success", 'data': {}}}
            for wbs in info[res[1]]:
                await info[res[1]][wbs].send_text(json.dumps(res_data))
        # for wbs in info:
        #     await info[msg['data']['appId'] ][wbs].send_text(f"{msg['data']['userId']}: {data}:{msg['data']['appId'] }")

    # 断开 删除
    async def on_disconnect(self, websocket, close_code):
        socket_only = await self.alter_socket(websocket)
        res = socket_user[socket_only]
        # 删除连接池
        info[res[1]].pop(res[0])
        res_data = {'seq': sendId(), 'cmd': 'logout', 'data': { 'msg': '退出了聊天室', 'userId': res[0], 'appId': res[1] }}
        for wbs in info[res[1]]:
            await info[res[1]][wbs].send_text(json.dumps(res_data) )

def sendId():
    time_ = str(int(time.time()) )
    res = time_ + "-" + str(random.randint(100000, 999999) )
    return res

# 路由
routes = [
    Route("/", Homepage),
    WebSocketRoute("/ws", Echo)
]
# 输入字段验证类


class SendMsg(BaseModel):
    appId: str
    userId: str
    msgId: str
    message: str


app = FastAPI(routes=routes)

# 跨域，cors伪装保护
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.post("/send_msg")
async def send_msg(msg_data: SendMsg):
    """appId:str, userId:str, msgId:str, msg:str"""
    if msg_data.appId not in msg_dict:
        msg_dict[msg_data.appId] = {}
    msg_dict[msg_data.appId][msg_data.userId].append( msg_data.message+msg_data.msgId)
    msg_txt[msg_data.appId].append( msg_data.userId + msg_data.msgId+msg_data.message)

    res_data = {'seq': msg_data.msgId, 'cmd': 'send', 'data': { 'msg': msg_data.message, 'userId': msg_data.userId, 'appId': msg_data.appId }}
    for wbs in info[msg_data.appId]:
        await info[msg_data.appId][wbs].send_text( json.dumps(res_data) )
    return msg_txt


@app.get("/get_userlist")
async def get_userlist(type:int=0):
    """, token: str = Header(None)"""
    info_ = {v: {i: "详细信息" for i in info[v]} for v in info}
    if type==0:
        res = info_
    else:
        res = {'info_':info_, 'socket_user':socket_user, 'msg_dict':msg_dict,'msg_txt':msg_txt }
    return res
