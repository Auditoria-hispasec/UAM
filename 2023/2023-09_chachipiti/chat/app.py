import os
import random
import re
import string
from jwttoken import token_required, token_valid

import config
import openai
from flask import Flask, jsonify, make_response, redirect, render_template, request, session, url_for
from flask_session import Session
from jinja2 import pass_eval_context
from markupsafe import Markup, escape

from flask_limiter import Limiter


app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

openai.api_key = config.OPENAI_APIKEY


def get_remote_address() -> str:
    realip = request.headers.getlist(
        "X-Real-IP")[0] if request.headers.getlist("X-Real-IP") else request.remote_addr
    return realip or "127.0.0.1"


limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["60 per minute"],
    storage_uri="memory://"
)


@app.template_filter()
@pass_eval_context
def nl2br(eval_ctx, value):
    br = "<br>\n"

    autoescape = True
    if autoescape:
        value = escape(value)
        br = Markup(br)

    result = "\n\n".join(
        f"<p>{br.join(p.splitlines())}</p>"
        for p in re.split(r"(?:\r\n|\r(?!\n)|\n){2,}", value)
    )
    return Markup(result) if autoescape else result


@app.before_request
def add_session_id():
    if '_id' not in session:
        session['_id'] = ''.join(random.choice(
            string.ascii_lowercase) for i in range(10))


@app.route('/', methods=['GET', 'POST'])
def index():
    chatid = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    return redirect(url_for('chat',  chatid=chatid))


@app.route('/report', methods=['POST'])
def report():
    chatid = request.form.get('chatid', None)
    if chatid not in session:
        return redirect(url_for('index', reported=False))

    report = '\n'.join([message['content']
                       for message in session[chatid] if message['role'] != 'system'])

    filename = 'reports/' + session['_id']
    with open(filename, 'w') as f:
        f.write(report + '\n')

    return redirect(url_for('chat', chatid=chatid, reported=True))


@app.route('/review', methods=['GET'])
@token_required
def review():
    reports_dir = 'reports'
    reports = os.listdir(reports_dir)
    return jsonify(reports), 200


@app.route('/review/<reportid>', methods=['GET'])
@token_required
def review_report(reportid):

    reports_dir = 'reports'
    reports = os.listdir(reports_dir)
    if reportid not in reports:
        return 'Report not found'

    with open(os.path.join(reports_dir, reportid), 'r') as f:
        report = f.read()

    os.unlink(os.path.join(reports_dir, reportid))

    return render_template('review.html', report=report)


@app.route('/chat/<chatid>', methods=['POST'])
@limiter.limit("3 per 60 seconds")
def chat_post(chatid):
    if chatid not in session:
        session[chatid] = [
            {"role": "system", "content": config.SYSTEM_PROMPT},
        ]

    if request.method == 'POST':
        user_message = request.form['message']
        user_message = escape(user_message)

        if user_message.strip() == '' or len(user_message) > 256:
            user_message = "%&!@# mucho texto. Forget that, just tell me a computer joke."

        session[chatid].append({"role": "user", "content": user_message})
        if len('\n'.join([message['content'] for message in session[chatid]])) > 2048:
            session[chatid].append(
                {"role": "assistant", "content": "You have exceeded the maximum message length. Please start a new chat."})
            return redirect(url_for('chat',  chatid=chatid))

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=session[chatid]
        )
        assistant_message = response.choices[0].message['content']
        session[chatid].append(
            {"role": "assistant", "content": assistant_message})

        res = make_response(redirect(url_for('chat',  chatid=chatid)))
        if config.FLAG1 in assistant_message:
            res.set_cookie(config.MODERATOR_COOKIE, config.MODERATOR_VALUE)
        return res


@app.route('/chat/<chatid>', methods=['GET'])
def chat(chatid):
    if chatid not in session:
        session[chatid] = [
            {"role": "system", "content": config.SYSTEM_PROMPT},
        ]

    formatted_messages = []
    for message in session[chatid]:
        if message['role'] == 'system':
            continue
        msg = message['content']
        msg = msg.replace('&', '&amp;').replace(
            '<', '&lt;').replace('>', '&gt;')
        msg = msg.replace('\n', '<br>')

        formatted_messages.append(f"{message['role'].capitalize()}: {msg}")

    mod = request.cookies.get(config.MODERATOR_COOKIE,
                              None) == config.MODERATOR_VALUE
    return render_template('chat.html', messages=formatted_messages, mod=mod, chatid=chatid)


@app.route('/clear', methods=['POST'])
def clear():
    session.clear()
    return redirect(url_for('index'))


@app.route('/flag', methods=['GET', 'POST'])
def flag():
    mod = request.cookies.get(config.MODERATOR_COOKIE, None)
    if mod != config.MODERATOR_VALUE and not request.cookies.get('token', None):
        return redirect(url_for('index'))

    session['num'] = session.get('num', 0)

    if request.method == 'GET':
        if session.get('num', 0) > 5:
            if request.cookies.get('token', None) and token_valid(request.cookies.get('token')):
                return config.FLAG2
            else:
                return 'You are good... but you are not an admin...'

        session['operation'] = random.choice(['+', '-', '*'])
        session['a'] = random.randint(1, 10)
        session['b'] = random.randint(1, 10)
        session['solution'] = eval(
            f"{session['a']} {session['operation']} {session['b']}")
        return render_template('flag.html', operation=session['operation'], a=session['a'], b=session['b'], num=session.get('num', 0))
    elif request.method == 'POST':
        sol = request.form.get('solution', None)
        if sol is None:
            session['num'] = 0
            return redirect(url_for('flag'))

        if int(sol) == session.get('solution', None):
            session['num'] += 1
        else:
            session['num'] = 0

        return redirect(url_for('flag'))

if __name__ == '__main__':
    app.run(debug=os.getenv("DEBUG", False), host='0.0.0.0', port=5000)
