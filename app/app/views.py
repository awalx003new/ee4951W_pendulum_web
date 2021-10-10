########  imports  ##########
from flask import Flask, jsonify, request, render_template, make_response, redirect, url_for, send_from_directory, flash, Request
import os
from werkzeug.utils import secure_filename
app = Flask(__name__, static_folder='static')
# The 'static' argument is the folder with static files that is served at

# Set the secret key to some random bytes. Needs to be top secret!
# For POST request
app.secret_key = b'naan68P"Kl5Gif&re/Hetunp/'

# Maximum file size is 16 MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

@app.route('/')
def home_page():
    return render_template("base.html")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Create route for index
@app.route('/index')
def actuatepage():
    return render_template("index.html")

# *before* redirecting to route for index
@app.route('/index', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        uploaded_file.save(uploaded_file.filename)
    return redirect(url_for('index'))

#@app.route('/test', methods=['POST'])
#def testfn():
    # GET request
    #if request.method == 'GET':
    #    message = {'greeting':'Hello from Flask!'}
    #    return jsonify(message)  # serialize and use JSON headers
    # POST request
    #if request.method == 'POST':
    #req=request.get_json()
    #print(req)  # parse as JSON
    #res= make_response(jsonify(req),200)
    #return res
    #    return 'Sucesss', 200

#@app.route('/getdata/<index_no>', methods=['GET','POST'])
#def data_get(index_no):

    #if request.method == 'POST': # POST request
        #print(request.get_text())  # parse as text
        #return 'OK', 200

    #else: # GET request
        #return 't_in = %s ; result: %s ;'%(index_no, data[int(index_no)])
#############################
# Additional code goes here #
#############################
#########  run app  #########

if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0')
    #repopulate app.routes with statc IP address for controls lab
    #Use Sam's domain name (DNS) instead of local host
    #DNS=192.168.71.241
    app.run(debug=True)
