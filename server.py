from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'GET':
        res = request.args.get('get_value')
    elif request.method == 'POST':
        res = request.form['post_value']

    return res


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=80)
