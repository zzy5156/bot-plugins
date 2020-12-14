import random
import threading
import traceback
import socketio
import json
import requests
import logging
import time
import chat
import weather

user_list = []
logisticNo_list = []
msg_count = 0
check_count = 0
total_count = 0
history = globals()
robotqq = "" #机器人QQ号
webapi = "http://127.0.0.1:8888" #Webapi接口 http://127.0.0.1:8888
get_data_url = "https://www.mxnzp.com/api/logistics/discern?logistics_no="
header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    }
sio = socketio.Client()
logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s', level=0, filename='new.log', filemode='a')


class Mess:
    def __init__(self, message1):
        self.FromQQ = message1['ToUin']
        self.ToQQ = message1['FromUin']
        self.Content = message1['Content']


def send_result(result):
    try:
        data = result.json()
        if data['Ret'] != 0:
            print(data)
        else:
            print("发送消息成功")
    except Exception as e:
        print(e)


def send(ToQQ, Content, sendToType, atuser, sendMsgType='TextMsg'):
    tmp = {}
    tmp['toUser'] = ToQQ
    tmp['sendToType'] = sendToType
    tmp['groupid'] = 0
    tmp['content'] = Content
    tmp['atUser'] = atuser
    tmp['sendMsgType'] =sendMsgType
    tmp1 = json.dumps(tmp)
    print(tmp1)
    result = requests.post(webapi + '/v1/LuaApiCaller?&qq=' + robotqq + '&funcname=SendMsg&timeout=10', data=tmp1)
    t1 = threading.Thread(target=send_result, args=(result,))
    t1.start()


@sio.event
def connect():
    global check_count
    check_count = 0
    print('connected to server')
    sio.emit('GetWebConn', robotqq)
    url = webapi + '/v1/Github/InstallService'
    result = requests.get(url)
    print(result)
    #取得当前已经登录的QQ链接

    beat() #心跳包，保持对服务器的连接


@sio.on('OnFriendMsgs')
def OnFriendMsgs(message):
    global msg_count
    ''' 监听好友消息 '''
    try:
        msg_count += 1
        print(message)
        tmp1 = message
        tmp2 = tmp1['CurrentPacket']
        tmp3 = tmp2['Data']
        a = Mess(tmp3)
        cm = a.Content.split(' ')
        if a.Content == '#存活确认':
            send(a.ToQQ, "还在呢", 1, 0)
        elif a.Content == '测试':
            send(a.ToQQ, "Null", 1, 0)
        if tmp3['MsgType'] == 'JsonMsg':
            data = json.loads(str(json.loads(tmp3['Content'])['Content']).split("</msg>", 1)[1])
            if data['app'] == 'com.tencent.map':
                msg = weather.get_now_weather(
                    str(data['meta']['Location.Search']['lng']) + "," + str(data['meta']['Location.Search']['lat']))
                send(a.ToQQ, msg, 1, 0)
        elif tmp3['MsgType'] == 'XmlMsg':
            data = json.loads(str(json.loads(tmp3['Content'])['Content']).split("<?xml", 1)[0])
            if data['app'] == 'com.tencent.map':
                msg = weather.get_now_weather(
                    str(data['meta']['Location.Search']['lng']) + "," + str(data['meta']['Location.Search']['lat']))
                send(a.ToQQ, msg, 1, 0)
    except:
        var = traceback.format_exc()
        print(var)


def fun(info, group):
    if str(group) not in history.keys():
        history[str(group)] = "####"
    if str(group) + "_count" not in history.keys():
        history[str(group) + "_count"] = 0
    if info == history[str(group)]:
        history[str(group) + "_count"] = history[str(group) + "_count"] + 1
    elif history[str(group) + "_count"] != 0:
        if history[str(group) + "_count"] > 4:
            ban = random.randint(1, history[str(group) + "_count"] + 1)
            send(group, "共 " + str(history[str(group) + "_count"] + 1) + " 条复读，生成的随机数为 " + str(ban) + " .", 2, 0)
        history[str(group) + "_count"] = 0
    history[str(group)] = info


@sio.on('OnGroupMsgs')
def OnGroupMsgs(message):
    global msg_count
    msg_count += 1
    print(message)
    try:
        info = message['CurrentPacket']['Data']['Content']
        group = message['CurrentPacket']['Data']['FromGroupId']
        uid = message['CurrentPacket']['Data']['FromUserId']
        name = message['CurrentPacket']['Data']['FromNickName']
        pid = message['CurrentPacket']['Data']['MsgSeq']
        msg_time = message['CurrentPacket']['Data']['MsgTime']
        msg_type = message['CurrentPacket']['Data']['MsgType']
        if msg_type == 'TextMsg':
            if info == "#about":
                send(group, "机器狼 For QQ V1.0.2 BETA（Python3 Ver.）", 2, 0)
            elif info == "#存活确认":
                send(group, "目前程序运行正常(｀・ω・´)", 2, 0)
        elif msg_type == 'AtMsg':
            info = json.loads(info)
            atUser = info['UserID'][0]
            if str(atUser) == str(robotqq):
                question = info['Content']
                question = question.split(" ", 1)
                answer = chat.get_content(question[1])
                # at = f'[ATUSER({uid})]\n'
                # print(at)
                # result = at + str(answer)
                # print(result)
                send(group, answer, 2, 0)
        elif msg_type == 'JsonMsg':
            data = json.loads(
                str(json.loads(message['CurrentPacket']['Data']['Content'])['Content']).split("</msg>", 1)[1])
            if data['app'] == 'com.tencent.map':
                msg = weather.get_now_weather(
                    str(data['meta']['Location.Search']['lng']) + "," + str(data['meta']['Location.Search']['lat']))
                send(message['CurrentPacket']['Data']['FromGroupId'], msg, 2,
                     message['CurrentPacket']['Data']['FromUserId'])
        elif msg_type == 'XmlMsg':
            data = json.loads(
                str(json.loads(message['CurrentPacket']['Data']['Content'])['Content']).split("<?xml", 1)[0])
            if data['app'] == 'com.tencent.map':
                msg = weather.get_now_weather(
                    str(data['meta']['Location.Search']['lng']) + "," + str(data['meta']['Location.Search']['lat']))
                send(message['CurrentPacket']['Data']['FromGroupId'], msg, 2,
                     message['CurrentPacket']['Data']['FromUserId'])
        elif msg_type == 'PicMsg':
            info = ""
            tmp = json.loads(message['CurrentPacket']['Data']['Content'])['GroupPic']
            for i in tmp:
                print(i)
                info += str(i['FileMd5'])
        fun(info, group)
    except:
        var = traceback.format_exc()
        print(var)


@sio.on('OnEvents')
def OnEvents(message):
    global msg_count
    msg_count += 1
    ''' 监听相关事件'''
    # print(message)
    # event_type = message['CurrentPacket']['Data']['EventName']
    # if event_type == 'ON_EVENT_GROUP_REVOKE':
    #     pid = message['CurrentPacket']['Data']['EventMsg']['MsgSeq']
    #     uid = message['CurrentPacket']['Data']['EventData']['AdminUserID']
    #     group = message['CurrentPacket']['Data']['EventData']['GroupID']


def beat():
    for i in range(5):
        print("第 " + str(i + 1) + " 次获取websocket")
        sio.emit('GetWebConn', robotqq)
        time.sleep(60)


def main():
    try:
        sio.connect(webapi, transports=['websocket'])
        # pdb.set_trace() 这是断点
        sio.wait()
    except BaseException as e:
        logging.info(e)
        print(e)


if __name__ == '__main__':
    main()
