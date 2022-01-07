from django.shortcuts import render
import logging

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *

import qrcode

#引入器材辨識模型
import gymequippred as gep

import pyecharts.options as opts
from pyecharts.options import DataZoomOpts
from pyecharts.charts import Bar, Line, Grid, Tab
import pymongo
import pandas as pd
import os

logger = logging.getLogger("django")

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

def sport(ID):
    message = []
    client = pymongo.MongoClient('localhost', 27017)
    db = client[ID]
    collection = db['squat']
    collection1 = db['biceps_curl']

    list_tmp = []
    for i in collection.find():
        list_tmp.append(i)

    df = pd.DataFrame(list_tmp)
    df_list = df.values.tolist()

    list_tmp1 = []
    for r in collection1.find():
        list_tmp1.append(r)
    df1 = pd.DataFrame(list_tmp1)
    df_list1 = df1.values.tolist()

    x = []
    y1 = []
    y2 = []
    y3 = []

    x1 = []
    y11 = []
    y12 = []
    y13 = []

    for data in df_list:
        x.append(data[5])
        y1.append(data[3])
        y2.append(data[2])
        y3.append(data[4])

    for data1 in df_list1:
        x1.append(data1[5])
        y11.append(data1[3])
        y12.append(data1[2])
        y13.append(data1[4])

    def squat() -> Grid:
        b = Bar()
        l = Line()
        g = Grid()
        b.add_xaxis(x)
        b.add_yaxis("次數", y1, color="#EEE8AA", category_gap="35%", z=0)
        b.add_yaxis("重量", y3, color="#D2B48C", category_gap="35%", z=0)

        b.extend_axis(yaxis=opts.AxisOpts(type_='value', min_=0, max_=100, position='right',
                                          axislabel_opts=opts.LabelOpts(formatter='{value} '), interval=10))

        b.set_global_opts(title_opts=opts.TitleOpts(title=data[1] + "的深蹲訓練紀錄", pos_left="15%"),
                          toolbox_opts=opts.ToolboxOpts(is_show=True,
                                                        orient="horizontal",
                                                        feature={"saveAsImage": {"title": "儲存訓練紀錄"}}),
                          datazoom_opts=[DataZoomOpts()])

        l.add_xaxis(x)
        l.add_yaxis("分數", y2, yaxis_index=1, symbol='circle',
                    linestyle_opts=opts.LineStyleOpts(color='#6B8E23', width=1.5)
                    , label_opts=opts.LabelOpts(color='#6B8E23'))

        b.overlap(l)

        g.add(chart=b, grid_opts=opts.GridOpts(), is_control_axis_index=True)
        return g

    def biceps_curl() -> Grid:
        b1 = Bar()
        l1 = Line()
        g1 = Grid()

        # page = Page(layout=Page.DraggablePageLayout)

        b1.add_xaxis(x1)
        b1.add_yaxis("次數", y11, color="#EEE8AA", category_gap="35%", z=0)
        b1.add_yaxis("重量", y13, color="#D2B48C", category_gap="35%", z=0)

        b1.extend_axis(yaxis=opts.AxisOpts(type_='value', min_=0, max_=100, position='right',
                                           axislabel_opts=opts.LabelOpts(formatter='{value} '), interval=10))

        b1.set_global_opts(title_opts=opts.TitleOpts(title=data1[1] + "的二頭灣舉訓練紀錄", pos_left="15%"),
                           toolbox_opts=opts.ToolboxOpts(is_show=True,
                                                         orient="horizontal",
                                                         feature={"saveAsImage": {"title": "儲存訓練紀錄"}}),
                           datazoom_opts=[DataZoomOpts()])

        l1.add_xaxis(x1)
        l1.add_yaxis("分數", y12, yaxis_index=1, symbol='circle',
                     linestyle_opts=opts.LineStyleOpts(color='#6B8E23', width=1.5)
                     , label_opts=opts.LabelOpts(color='#6B8E23'))

        b1.overlap(l1)

        g1.add(chart=b1, grid_opts=opts.GridOpts(), is_control_axis_index=True)
        return g1

    tab = Tab()
    tab.add(squat(), "squat")
    tab.add(biceps_curl(), "biceps_curl")

    path = "./templates/" + ID
    if not os.path.isdir(path):
        os.mkdir(path)

    tab.render("./templates/" + ID + '/' + ID + ".html")

    message.append(TextSendMessage(text="https://traipro.aaacsolutions.xyz/trAInsformers/history/"+ID))

    return message


@csrf_exempt
def history(request, puserid):
    return render(request, puserid+'/'+puserid+'.html', locals())

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        message = []
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        # message.append(TextSendMessage(text=str(body)))

        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):  # 如果有訊息事件
                if event.message.type == 'text':
                    #回傳line user id 的 qrcode
                    if event.message.text == '註冊':
                        global puserid
                        puserid = event.source.user_id
                        print(puserid)
                        img = qrcode.make(puserid)
                        img.save("./static/" + puserid + ".png")

                        message.append(ImageSendMessage(original_content_url='https://525b-111-249-59-227.ngrok.io/static/' + puserid + ".png",
                                                        preview_image_url='https://525b-111-249-59-227.ngrok.io/static/' + puserid + ".png"))

                        line_bot_api.reply_message(event.reply_token, message)

                    elif event.message.text == "查詢器材名稱":
                        message.append(TextSendMessage(
                            text='請上傳圖片',
                            quick_reply=QuickReply(
                                items=[
                                    QuickReplyButton(
                                        action=CameraAction(label="拍照")
                                    ),
                                    QuickReplyButton(
                                        action=CameraRollAction(label="相簿")
                                    )
                                ]
                            )
                        ))
                        line_bot_api.reply_message(event.reply_token, message)



                    # 提供訓練歷史資料網址
                    elif event.message.text == "訓練紀錄":
                        puserid = event.source.user_id
                        message.append(TextSendMessage(text="https://traipro.aaacsolutions.xyz/trAInsformers/history/" + puserid))
                        #line_bot_api.reply_message(event.reply_token, sport(puserid))
                        line_bot_api.reply_message(event.reply_token, message)

                #回傳運動器材名稱
                elif event.message.type == 'image':
                    image_content = line_bot_api.get_message_content(event.message.id)
                    puserid = event.source.user_id
                    img_save_path = './gepimage/' + puserid + '.jpg'

                    with open(img_save_path, 'wb') as fd:
                        for chunk in image_content.iter_content():
                            fd.write(chunk)
                    pred = gep.equipred(img_save_path)

                    machine_name = {'Abductor&AdductorMachine 大腿內收外展機': 'https://youtu.be/a0eAQmuK5TA Precor Inner/Outer Thigh',
                                    'BicepsCurlMachine 二頭彎舉機': 'https://youtu.be/qiYAjdOW2t4?t=34',
                                    'CableMachine 滑輪訓練機': 'https://youtu.be/Ufw6TSuesV0',
                                    'ChestFlyMachine 蝴蝶機': 'https://youtu.be/r3bpEfMNQ7Q Precor Rear Delt/Pec Fly',
                                    'HackSquatMachine 哈克深蹲機': 'https://youtu.be/GamGGLcZu84',
                                    'LateralRaiseMachine': 'https://youtu.be/fuoOrPJ0h_o Real',
                                    'LatPulldownMachine': 'https://youtu.be/LjhIHI3Cg78?t=31',
                                    'LegExtensionMachine': 'https://youtu.be/th4fscPB-bw',
                                    'LegPressMachine 腿部推舉機':'https://youtu.be/LNjUqjQToF4',
                                    'LegRaiseMachine 雙槓抬腿機': 'https://youtu.be/982Mwu_MqeQ',
                                    'RowingMachine 划船機': 'https://youtu.be/LjhIHI3Cg78?t=146',
                                    'ShoulderPressMachine': 'https://youtu.be/avHidhh3Buw',
                                    'SittingLegPressMachine 坐式腿推機': 'https://youtu.be/evMn8Ss7bkc',
                                    'SmithMachine 史密斯架': 'https://youtu.be/H_sMtSLUPpE',
                                    'TricepsExtensionMachine': 'https://youtu.be/5u0Gufto8Z8'}

                    url = 'tmp'
                    if pred in machine_name:
                        url = machine_name[pred]

                    message.append(TextSendMessage(text=pred))
                    message.append(TextSendMessage(text=url))
                    line_bot_api.reply_message(event.reply_token, message)

        return HttpResponse()
    else:
        return HttpResponseBadRequest()
