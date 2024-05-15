from bson import ObjectId
from pymongo import MongoClient
import requests
from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider

import json
import sys

app = Flask(__name__)


client = MongoClient('localhost', 27017)
db = client.fifacoli

#####################################################################################
# 이 부분은 코드를 건드리지 말고 그냥 두세요. 코드를 이해하지 못해도 상관없는 부분입니다.
#
# ObjectId 타입으로 되어있는 _id 필드는 Flask 의 jsonify 호출시 문제가 된다.
# 이를 처리하기 위해서 기본 JsonEncoder 가 아닌 custom encoder 를 사용한다.
# Custom encoder 는 다른 부분은 모두 기본 encoder 에 동작을 위임하고 ObjectId 타입만 직접 처리한다.


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)


# 위에 정의되 custom encoder 를 사용하게끔 설정한다.
app.json = CustomJSONProvider(app)

# 여기까지 이해 못해도 그냥 넘어갈 코드입니다.
# #####################################################################################


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/article')
def article():
    return render_template('article.html')

# ------------------------------------------------------------index.html


@app.route('/list', methods=['POST'])
def search_nickname():
    #  클라이언트로부터 닉네임과 api key를 받는다
    api_key = request.form["give_key"]
    character_name = request.form["give_name"]
    # 헤더부분
    headers = {
        "x-nxopen-api-key": api_key,
    }
    # ouid
    url_string = 'https://open.api.nexon.com/fconline/v1/id?nickname='+character_name
    response = requests.get(url_string, headers=headers)
    ouid = response.json()['ouid']

    # 닉네임과 레벨
    url_string = 'https://open.api.nexon.com/fconline/v1/user/basic?ouid='+ouid
    response = requests.get(url_string, headers=headers)
    nickname = response.json()['nickname']
    level = response.json()['level']

    # 최고등급&달성 날짜
    url_string = 'https://open.api.nexon.com/fconline/v1/user/maxdivision?ouid='+ouid
    response = requests.get(url_string, headers=headers)
    matchtype = response.json()[0]['matchType']
    division = response.json()[0]['division']
    achieve_date = response.json()[0]['achievementDate']
    achieve_date = achieve_date.split('T')[0]

    url_string = 'https://open.api.nexon.com/static/fconline/meta/matchtype.json'
    response = requests.get(url_string)
    for i in response.json():
        if (i['matchtype'] == matchtype):
            matchtype = i['desc']
        else:
            continue
    url_string = 'https://open.api.nexon.com/static/fconline/meta/division.json'
    response = requests.get(url_string)
    for i in response.json():
        if (i['divisionId'] == division):
            division = i['divisionName']
        else:
            continue

    if (division == '슈퍼챔피언스'):
        div_img = 'https://ssl.nexon.com/s2/game/fo4/obt/rank/large/update_2009/ico_rank0.png'
    elif (division == '챔피언스'):
        div_img = 'https://ssl.nexon.com/s2/game/fo4/obt/rank/large/update_2009/ico_rank1.png'
    elif (division == '슈퍼챌린지'):
        div_img = 'https://ssl.nexon.com/s2/game/fo4/obt/rank/large/update_2009/ico_rank2.png'
    elif (division == '챌린지1'):
        div_img = 'https://ssl.nexon.com/s2/game/fo4/obt/rank/large/update_2009/ico_rank3.png'
    elif (division == '챌린지2'):
        div_img = 'https://ssl.nexon.com/s2/game/fo4/obt/rank/large/update_2009/ico_rank4.png'
    elif (division == '챌린지3'):
        div_img = 'https://ssl.nexon.com/s2/game/fo4/obt/rank/large/update_2009/ico_rank5.png'
    elif (division == '월드클래스1'):
        div_img = 'https://ssl.nexon.com/s2/game/fo4/obt/rank/large/update_2009/ico_rank6.png'
    elif (division == '월드클래스2'):
        div_img = 'https://ssl.nexon.com/s2/game/fo4/obt/rank/large/update_2009/ico_rank7.png'
    elif (division == '월드클래스3'):
        div_img = 'https://ssl.nexon.com/s2/game/fo4/obt/rank/large/update_2009/ico_rank8.png'
    elif (division == '프로1'):
        div_img = 'https://ssl.nexon.com/s2/game/fo4/obt/rank/large/update_2009/ico_rank9.png'
    elif (division == '프로2'):
        div_img = 'https://ssl.nexon.com/s2/game/fo4/obt/rank/large/update_2009/ico_rank10.png'
    elif (division == '프로3'):
        div_img = 'https://ssl.nexon.com/s2/game/fo4/obt/rank/large/update_2009/ico_rank11.png'
    elif (division == '세미프로1'):
        div_img = 'https://ssl.nexon.com/s2/game/fo4/obt/rank/large/update_2009/ico_rank12.png'
    elif (division == '세미프로2'):
        div_img = 'https://ssl.nexon.com/s2/game/fo4/obt/rank/large/update_2009/ico_rank13.png'
    elif (division == '세미프로3'):
        div_img = 'https://ssl.nexon.com/s2/game/fo4/obt/rank/large/update_2009/ico_rank14.png'

    doc = {
        "ouid": ouid,
        "nickname": nickname,
        "level": level,
        "matchtype": matchtype,
        "division": division,
        "achieve_date": achieve_date,
        "div_img": div_img
    }
    existing_doc = db.fifa.find_one({'nickname': nickname})
    if existing_doc is None:
        db.fifa.insert_one(doc)
   
    return jsonify({'result': doc})


@app.route('/match', methods=['POST'])
def match_history():
    db.fifaMatch.drop()
    # nickname & api_key
    api_key = request.form["give_key"]
    character_name = request.form["give_name"]
    headers = {
        "x-nxopen-api-key": api_key,
    }
    # ouid
    url_string = 'https://open.api.nexon.com/fconline/v1/id?nickname='+character_name
    response = requests.get(url_string, headers=headers)
    ouid = response.json()['ouid']

    url_string = 'https://open.api.nexon.com/fconline/v1/user/match?ouid=' + \
        ouid+'&matchtype=50&offset=0&limit=20'
    response = requests.get(url_string, headers=headers)
    for i in response.json():
        match_id = i
        url_string = 'https://open.api.nexon.com/fconline/v1/match-detail?matchid='+match_id
        result = requests.get(url_string, headers=headers)
        id1 = result.json()['matchInfo'][0]['ouid']
        nickname1 = result.json()['matchInfo'][0]['nickname']
        match_result1 = result.json(
        )['matchInfo'][0]['matchDetail']['matchResult']
        scored1 = result.json()['matchInfo'][0]['shoot']['goalTotal']
        id2 = result.json()['matchInfo'][1]['ouid']
        nickname2 = result.json()['matchInfo'][1]['nickname']
        match_result2 = result.json(
        )['matchInfo'][1]['matchDetail']['matchResult']
        scored2 = result.json()['matchInfo'][1]['shoot']['goalTotal']
        if (nickname1 == character_name):
            doc = {
                'player_id': id1,
                'player_nickname': nickname1,
                'player_result': match_result1,
                'player_scored': scored1,
                'opponent_id': id2,
                'opponent_nickname': nickname2,
                'opponent_result': match_result2,
                'opponent_scored': scored2
            }
            db.fifaMatch.insert_one(doc)
        else:
            doc = {
                'player_id': id2,
                'player_nickname': nickname2,
                'player_result': match_result2,
                'player_scored': scored2,
                'opponent_id': id1,
                'opponent_nickname': nickname1,
                'opponent_result': match_result1,
                'opponent_scored': scored1,
            }
            db.fifaMatch.insert_one(doc)
    all_matchs = list(db.fifaMatch.find({}))
    return jsonify({'result': all_matchs})

# ------------------------------------------------------------article.html
@app.route('/memos', methods=['POST'])
def save_article():
    # 클라이언트로부터 제목과 내용 받기.
    title_receive = request.form['title_give']
    content_receive = request.form['content_give']

    # 받은 데이터로 db에 들어갈 article 만들기
    article = {
        'title': title_receive,
        'content': content_receive,
        'like': 0
    }

    # 몽고db에 저장
    db.memos.insert_one(article)

    return jsonify({'result': 'success', 'msg': '포스팅 성공!'})

# db에서 articles 추출


@app.route('/memos', methods=['GET'])
def show_articles():
    # 모든 document 찾기 ({'_id':False} 이부분을 추가하지 않으면 에러뜸 왜지..? ==>해결)
    table = list(db.memos.find().sort('like', -1))

    return jsonify({'result': 'success', 'articles': table})

# 좋아요 기능 생성


@app.route('/memos/like', methods=['POST'])
def like_article():
    # 클라이언트로부터 title 받기.
    title_receive = request.form['title_give']
    article = db.memos.find_one({'title': title_receive})

    # 받은 title에 해당하는 like +1
    new_like = article['like'] + 1

    # 몽고db에 업데이트
    result = db.memos.update_one({'title': title_receive}, {
                                 '$set': {'like': new_like}})

    return jsonify({'result': 'success', 'msg': '좋아요 완료!'})

# 수정할 title,content를 db에 업데이트


@app.route('/memos/edit', methods=['POST'])
def edit_articles():
    # 클라이언트로부터 수정된 title,content 받고 업데이트.
    id = request.form['id_give']
    title_receive = request.form['title_give']
    db.memos.update_one({'_id': ObjectId(id)}, {
                        '$set': {'title': title_receive}})
    content_receive = request.form['content_give']
    db.memos.update_one({'_id': ObjectId(id)}, {
                        '$set': {'content': content_receive}})

    return jsonify({'result': 'success', 'msg': '수정 완료!'})

# 해당 도큐멘트를 제거


@app.route('/memos/discard', methods=['POST'])
def discard_article():
    # 클라이언트로부터 삭제할 title을 받음.
    title_receive = request.form['title_give']
    # 해당 title에 해당하는 도큐먼트 삭제.
    db.memos.delete_one({'title': title_receive})

    return jsonify({'result': 'success', 'msg': '삭제 완료!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
