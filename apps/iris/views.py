# apps/iris/views.py
from flask import Flask, flash, redirect, request, render_template, jsonify, abort, current_app, url_for
import pickle, os
from apps.dbmodels import IRIS, db, User, APIKey, UsageLog, UsageType
import numpy as np
from flask_login import current_user, login_required
from apps.iris.forms import IrisUserForm
from . import iris
# Load model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')
with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)
from apps.config import Config  #TARGET_NAMES = ['setosa', 'versicolor', 'virginica']
TARGET_NAMES = Config.IRIS_LABELS   # 라벨 읽기
@iris.route('/predict', methods=['GET', 'POST'])
@login_required
def iris_predict():
    form = IrisUserForm()
    if form.validate_on_submit():
        sepal_length = form.sepal_length.data
        sepal_width = form.sepal_width.data
        petal_length = form.petal_length.data
        petal_width = form.petal_width.data
        features=np.array([[sepal_length, sepal_width, petal_length, petal_width]])
        pred = model.predict(features)[0]
        new_usage_log=UsageLog( user_id=current_user.id,
            #api_key_id=None
            usage_type=UsageType.LOGIN, # LOGIN 타입으로 저장
            endpoint=request.path,
            remote_addr=request.remote_addr,
            response_status_code=200
            )
        db.session.add(new_usage_log)     # 새로운 객체를 데이터베이스 세션에 추가
        db.session.commit() # 변경 사항을 데이터베이스에 실제로 저장
        return render_template('iris/predict.html',
                               result=TARGET_NAMES[pred],
                               sepal_length=sepal_length, sepal_width=sepal_width,
                               petal_length=petal_length, petal_width=petal_width, form=form,
                               TARGET_NAMES=TARGET_NAMES
                              )
    return render_template('iris/predict.html',form=form)
@iris.route('/save_iris_data', methods=['POST'])
@login_required
def save_iris_data():
    if request.method == 'POST':        # HTML 폼에서 전송된 모든 데이터 가져오기
        sepal_length = request.form.get('sepal_length')
        sepal_width = request.form.get('sepal_width')
        petal_length = request.form.get('petal_length')
        petal_width = request.form.get('petal_width')
        predicted_class = request.form.get('predicted_class')
        confirmed_class = request.form.get('confirmed_class') # 이게 핵심
        new_iris_entry = IRIS( user_id=current_user.id,
            #api_key_id=
            sepal_length=float(sepal_length), # 저장하기 전에 숫자로 바꿔줘요
            sepal_width=float(sepal_width),
            petal_length=float(petal_length),
            petal_width=float(petal_width),
            predicted_class=predicted_class,
            confirmed_class=confirmed_class,  # 수정되었거나 저장된 값을 저장해요
            confirm =True
            )
        db.session.add(new_iris_entry)     # 새로운 객체를 데이터베이스 세션에 추가
        db.session.commit() # 변경 사항을 데이터베이스에 실제로 저장
        return redirect(url_for('iris.iris_predict')) # 예측 페이지로 다시 이동
    flash('데이터 저장 중 오류가 발생했습니다.', 'danger')
    return redirect(url_for('iris.iris_predict'))
@iris.route('/ai_results')
@login_required
def ai_results():
    # 현재 로그인한 사용자의 추론 결과를 가져오기
    # 생성 순서대로 가져오기
    user_results = IRIS.query.filter_by(user_id=current_user.id).order_by(IRIS.created_at.desc()).all()
    return render_template('iris/user_results.html',title='추론결과', results=user_results)
@iris.route('/ai_logs')
@login_required
def ai_logs():
    # 현재 로그인한 사용자의 AI 추론 로그 가져오기
    # 생성 순서대로 가져오기
    user_logs = UsageLog.query.filter_by(user_id=current_user.id).order_by(UsageLog.timestamp.desc()).all()
    return render_template('iris/user_logs.html',title='AI로그이력', results=user_logs)

"""
    if request.method == 'POST':
        try:
            sl = float(request.form['sepal_length'])
            sw = float(request.form['sepal_width'])
            pl = float(request.form['petal_length'])
            pw = float(request.form['petal_width'])
        except Exception as e:
            return render_template('iris/index.html', error='입력 오류: '+str(e))
        pred = model.predict([[sl, sw, pl, pw]])[0]
        return render_template('iris/index.html',
                               result=TARGET_NAMES[pred],
                               sepal_length=sl, sepal_width=sw,
                               petal_length=pl, petal_width=pw,
                               api_key=request.form.get('api_key'))
    return render_template('iris/index.html')
"""