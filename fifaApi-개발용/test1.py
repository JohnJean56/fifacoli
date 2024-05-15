from bson import ObjectId
from pymongo import MongoClient
import requests
from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider

import json
import sys

api_key = 'test_c006a02666edc9d92e3b993173d7ea8e3da41b0f752126e8fb9a0371bb7caab2a22e4f95966664fc580deb5e7f6262c3'
ouid = 'adbd529ea104ab93b4a633915013d972'
character_name = '희꼬재추'


headers = {
    "x-nxopen-api-key": api_key,
}
#내 최고동급
url_string = 'https://open.api.nexon.com/fconline/v1/user/maxdivision?ouid=adbd529ea104ab93b4a633915013d972'
response = requests.get(url_string, headers=headers)
matchtype = response.json()[0]['matchType']
division = response.json()[0]['division']
achieve_date = response.json()[0]['achievementDate']
achieve_date = achieve_date.split('T')[0]
#print(matchtype,division,achieve_date)

#최고등급 숫자가 의미하는건 무엇인지
url_string = 'https://open.api.nexon.com/static/fconline/meta/matchtype.json'
response = requests.get(url_string)
#print(response.json())
for i in response.json():
       if (i['matchtype'] == matchtype):
           matchtype = i['desc']
       else:
           continue
url_string = 'https://open.api.nexon.com/static/fconline/meta/division.json'     
response = requests.get(url_string)  
#print(response.json()) 
for i in response.json():
       if (i['divisionId'] == division):
           division = i['divisionName']
       else:
           continue  
       
url_string = 'https://open.api.nexon.com/fconline/v1/user/match?ouid=adbd529ea104ab93b4a633915013d972&matchtype=50&offset=0&limit=5'
response = requests.get(url_string, headers=headers)
for i in response.json() :
       match_id = i
       url_string = 'https://open.api.nexon.com/fconline/v1/match-detail?matchid='+match_id
       result = requests.get(url_string, headers=headers)
       id1 = result.json()['matchInfo'][0]['ouid']
       nickname1 = result.json()['matchInfo'][0]['nickname']
       match_result1 = result.json()['matchInfo'][0]['matchDetail']['matchResult']
       scored1 = result.json()['matchInfo'][0]['shoot']['goalTotal']
       id2 = result.json()['matchInfo'][1]['ouid']
       nickname2 = result.json()['matchInfo'][1]['nickname']
       match_result2 = result.json()['matchInfo'][1]['matchDetail']['matchResult']
       scored2 = result.json()['matchInfo'][1]['shoot']['goalTotal']
       doc = {
           'player_1_id':id1,
           'player_1_nickname':nickname1,
           'player_1_result':match_result1,
           'player_1_scored':scored1,
           'player_2_id':id2,
           'player_2_nickname':nickname2,
           'player_2_result':match_result2,
           'player_2_scored':scored2,
       }
       print(doc)
       
       
#print(response.json())

# name = '\ud76c\uaf2c\uc7ac\ucd94\u000d'
# encoded = name.encode('latin-1')
# print(encoded)
# .encode('utf-8').decode('iso-8859-1')
