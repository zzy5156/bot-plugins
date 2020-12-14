import json
import requests

token = "" # 彩云天气API token


def get_now_weather(place_2):
    try:
        json_text = requests.get(
            str.format("https://api.caiyunapp.com/v2.5/" + token + "/" + place_2 + "/realtime.json")).content
        data = json.loads(json_text.decode(encoding='UTF-8', errors='ignore'))
        status = data['status']
        if status == 'failed':
            return "彩云天气暂时不可用，请稍后再试"
        else:
            json_text_1 = requests.get(
                str.format("https://api.caiyunapp.com/v2.5/" + token + "/" + place_2 + "/minutely.json")).content
            self_realtime_data = json.loads(json_text_1.decode(encoding='UTF-8', errors='ignore'))
            now_data = self_realtime_data['result']['forecast_keypoint']
            a_place = "".join(str(data['location']))
            tem = data['result']['realtime']['temperature']
            pm25 = data['result']['realtime']['air_quality']['pm25']
            source = data['result']['realtime']['precipitation']['local']['datasource']
            wea = data['result']['realtime']['skycon']
            if wea == 'CLEAR_DAY' or wea == 'CLEAR_NIGHT':
                wea = "晴"
            elif wea == 'PARTLY_CLOUDY_DAY' or wea == 'PARTLY_CLOUDY_NIGHT':
                wea = "多云"
            elif wea == 'CLOUDY':
                wea = "阴"
            elif wea == 'WIND':
                wea = "大风"
            elif wea == 'LIGHT_HAZE':
                wea = "轻度雾霾"
            elif wea == 'MODERATE_HAZE':
                wea = "中度雾霾"
            elif wea == 'HEAVY_HAZE':
                wea = "重度雾霾"
            elif wea == 'LIGHT_RAIN':
                wea = "小雨"
            elif wea == 'MODERATE_RAIN':
                wea = "中雨"
            elif wea == 'HEAVY_RAIN':
                wea = "大雨"
            elif wea == 'STORM_RAIN':
                wea = "暴雨"
            elif wea == 'FOG':
                wea = "雾"
            elif wea == 'LIGHT_SNOW':
                wea = "小雪"
            elif wea == 'MODERATE_SNOW':
                wea = "中雪"
            elif wea == 'HEAVY_SNOW':
                wea = "大雪"
            elif wea == 'STORM_SNOW':
                wea = "暴雪"
            elif wea == 'DUST':
                wea = "浮尘"
            elif wea == 'SAND':
                wea = "沙尘"
            send_data = "经纬度：" + a_place + "\n天气：" + wea + "\n降雨预报：" + now_data + "\n温度：" + str(
                tem) + " ℃\npm2.5：" + str(pm25) + "\n数据来源：彩云科技(" + source + ")"
            return send_data
    except:
        return "获取当前天气失败，请稍后再试"
