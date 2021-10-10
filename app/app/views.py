#---------------------------------------------------------imports---------------------------------------------------------------#
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

#UPLOAD_DESTINATION = "instance/Uploads/"
#PROCESSING_FILE = "upload.py"

# Create an 'Uploads' directory in a known location --> this directory is where files are saved to
#uploads_directory = os.path.join(app.instance_path, UPLOAD_DESTINATION)
#os.makedirs(uploads_directory, exist_ok=True)

#---------------------------------------------------------decorators---------------------------------------------------------------#
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

    # Get the file name and encode it in ASCII format
    #nameOfFile = uploaded_file.filename
    #print(nameOfFile)
    #nameOfFile.encode(encoding="ascii")

    # Store the Contents of the uploaded file as a string and then encode the contents in ASCII format
    #fileContents = uploaded_file.read()
    #print("file Contents printed = " + fileContents)
    #fileContents.encode(encoding="ascii")

    # Open upload.py and write the contents of the uploaded file there
    # Since upload.py does not already exist, it will get created automatically
    #processingFile = open(UPLOAD_DESTINATION + PROCESSING_FILE, "w")
    #processingFile.write(fileContents)
    #processingFile.close()

    # Remove the created "Uploads" directory, otherwise, each time that the web server is run, directory creation is recursive
    #os.rmdir(UPLOAD_DESTINATION)

    return redirect(url_for('index'))

@app.route('/github_repo')
def gitHub_repo():
    return redirect("https://github.com/awalx003new/ee4951W_pendulum_web")

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
