# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request
import csv

from bs4 import BeautifulSoup
from slackclient import SlackClient
import slackclient
from flask import Flask, request, make_response, render_template

import mylib
app = Flask(__name__)

slack_token = 'xoxb-502213453520-507690715685-dQINZPYc0mtZE18q13h8Vrgw'
slack_client_id = "502213453520.508890751350"
slack_client_secret = "2fbe9551751ccffabc3d51da01bf8763"
slack_verification = "q7zUJP26cHh8nYzIK9b1H3rC"
sc = SlackClient(slack_token)

# 크롤링 함수 구현하기
def _crawl_naver_keywords(text):
    #함수를 구현해 주세요
    keywords = []
    # imgs = []
    if '브랜드' in text:
        url = "https://store.musinsa.com/app/usr/brand_rank"
        sourcecode = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(sourcecode, "html.parser")
        rank_area = soup.find('ul',class_='brandRanking')
        top = 10
        for item in rank_area.find_all('div',class_='li_inner')[:top]:
            keywords.append(item.find('p',class_='brand_name_en').get_text())
            # imgs.append('https:'+ item.find('img')['src'])
        result = '오늘의 무신사 브랜드 랭킹 Top{}\n\n'.format(top)
        for i in range(top):
            result += '{}위 : {}\n'.format(i+1,keywords[i])#{}\n'.format(i+1,keywords[i],imgs[i])
        return result
    else:
        keywords.append('저는 무신사의 인기 브랜드순위를 알려드립니다.\n "@무신사봇 브랜드"를 입력해보세요.')

    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(keywords)

# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        keywords = _crawl_naver_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )
        return make_response("App mention message has been sent", 200,)

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                            })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})

@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"

if __name__ == '__main__':
    app.run('127.0.0.1', port=5000)
