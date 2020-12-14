import hashlib
import string
import time
import random
from urllib.parse import quote
import requests

appid = '' # 腾讯AI APPID
appkey = '' # 腾讯AI APPKEY
error_response = "AI罢工啦，待会再试试吧" # 调用失败的默认回复
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 '
                  'Safari/537.36 '
}


def getReqSign(params: dict, appkey) -> str:
    sign = ''
    for key, value in sorted(params.items()):
        if not value:
            continue
        sign = f'{sign}{key}={quote(value)}&'

    sign += f'app_key={appkey}'
    sign = hashlib.md5(sign.encode(encoding='UTF-8')).hexdigest().upper()
    return sign


def getParams(question):
    # 请求时间戳（秒级），用于防止请求重放（保证签名5分钟有效）
    t = time.time()
    time_stamp = str(int(t))
    # 请求随机字符串，用于保证签名不可预测
    nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, 10))
    params = {'app_id': appid,
              'question': question,
              'time_stamp': time_stamp,
              'nonce_str': nonce_str,
              'session': '10000'
              }
    params['sign'] = getReqSign(params, appkey)
    return params


def get_content(question):
    # 聊天的API地址
    url = "https://api.ai.qq.com/fcgi-bin/nlp/nlp_textchat"
    # 获取请求参数
    question = question.replace(" ", ",")
    question = question.encode('utf-8')
    print("处理后的str：" + str(question))
    payload = getParams(question)
    r = requests.post(url, data=payload, headers=headers)
    answer = str(r.json()["data"]["answer"])
    if answer == "":
        print("返回了空数据呢")
        answer = error_response
    else:
        print("收到的回复是：" + answer)
    return answer


def main():
    print(get_content("今天湛江天气怎么样"))


if __name__ == '__main__':
    main()
