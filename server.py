import os
from flask import Flask, send_from_directory, render_template
from Utils.Util1 import response

app = Flask(__name__, template_folder='UI', static_folder=os.path.join("UI", "assets"), static_url_path='/assets')



@app.route('/timeline')
def timeline():
    return render_template('index.html')


@app.route('/')
def hello_world():
    # define response data
    data = {}
    message = "Hello API"
    statusCode = 200

    # send response
    return response(data, message, statusCode)

if __name__ == '__main__':
   app.run(host='0.0.0.0',port=8000,debug=True)