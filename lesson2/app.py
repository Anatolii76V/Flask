from flask import Flask, render_template, request, redirect, url_for, make_response

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/welcome', methods=['POST'])
def welcome():
    user_name = request.form.get('name')
    user_email = request.form.get('email')

    resp = make_response(redirect(url_for('greet')))
    resp.set_cookie('user_name', user_name)
    resp.set_cookie('user_email', user_email)

    return resp


@app.route('/greet')
def greet():
    user_name = request.cookies.get('user_name')
    return render_template('greet.html', user_name=user_name)


@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('index')))
    resp.delete_cookie('user_name')
    resp.delete_cookie('user_email')

    return resp


if __name__ == '__main__':
    app.run(debug=True)
