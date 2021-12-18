#---------------------------------------------------------imports-------------------------------------------------------------------------#
from flask import Flask, jsonify, request, render_template, make_response, redirect, url_for, send_from_directory, flash, Request, Response
# Use for operating system functionalities
import os
# Use for generating random secret key
import secrets
# Use for running a python script
import subprocess
import RPi.GPIO as GPIO
from werkzeug.utils import secure_filename
import time # Used for sleep()

# The 'static_folder' argument is the folder with static files that is served at
app = Flask(__name__, static_folder='static')

# Set the secret key to some random bytes. Needs to be top secret!
# Needed for POST request
app.secret_key = secrets.token_hex()

# Maximum file size is 16 MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

UPLOAD_DESTINATION = "."
RESULTS_DESTINATION = "."
INITIALIZE_SYSTEM = "initialize_system.py"
default_results_filename = "results.csv"

# Uploads folder is in current directory that gets navigated to later in the program
app.config['UPLOAD_FOLDER'] = UPLOAD_DESTINATION

ALLOWED_EXTENSIONS = {'py'}
# Name of test file
PROCESSING_FILE = "upload.py"

appapp = os.path.abspath(__file__)
appapp2 =os.path.dirname(appapp)
global processA
global process

import sys
sys.path.insert(0, '/home/pi/pendulum/System')
from motor import Motor
from System.system import System
import time
from sys import exit

# NOTE run "sudo python3 views.py" in the terminal

global popenErrorString

#---------------------------------------------------------methods------------------------------------------------------------------#
# Only allow .py file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#---------------------------------------------------------decorators---------------------------------------------------------------#
# For domain name
@app.route('/')
def home_page():
    return render_template("base.html")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Create route for index
@app.route('/index')
def actuatepage():
    os.chdir(appapp2)
    #First, make sure we are in the pendulum/System folder
    list_of_Paths = get_helpful_path()
    #Check if uploads folder exists
    uploads_folder_exist=os.path.isdir(list_of_Paths[3])
    #If uploads folder exists, enter this if statement to delete it
    if uploads_folder_exist==True:
        delete_uploads_files()
    os.chdir(list_of_Paths[0])
    return render_template("index.html")


# Redirect to route for index
# Receive form data from upload
@app.route('/index', methods=['POST'])
def upload_file():

    # Check if the POST request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return render_template("index.html")

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        # Display this message in the website when the user has not chosen a file
        flash('No file selected for uploading', "warning")
        return render_template("index.html")

    if uploaded_file and allowed_file(uploaded_file.filename):
        
        get_some_paths = get_helpful_path()
        
        # Make directory called "Uploads"
        # mode: read, write, and execute permissions for user, owner, and group
        mode = 0o777
        os.mkdir(get_some_paths[3], mode)

        # change directory to "Uploads"
        os.chdir(get_some_paths[3])

        # Get the file name
        nameOfFile = secure_filename(uploaded_file.filename)

        # Save uploaded file to "Uploads" folder in current directory
        uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], nameOfFile))

        # Open the ("Uploads/" conconcatenated with "filename") file for read
        userFile = open(UPLOAD_DESTINATION + "/" + nameOfFile, "r")

        fileContents = userFile.read()

        userFile.close()

        # Please note that "upload.py" is the test file
        # Open the ("Uploads/" conconcatenated with "upload.py") file for read/write.  Create upload.py if it does not already exist
        processingFile = open(UPLOAD_DESTINATION + "/" + PROCESSING_FILE, "w+")

        # write the "file_content" to the upload file object
        processingFile.write(fileContents)

        # Close the upload.py file object
        processingFile.close()
        
        os.chdir(get_some_paths[0])

    else:
        # Display this message in the website when the user has chosen a non-Python file
        flash('The file type specified is not allowed for upload.  Allowed file type is .py', "danger")
        return render_template('index.html')

    # Status code 204 is No Content - want to allow user to be able to click "Actuate" button on index.html page
    return Response(response=None, status=204)

      
def get_helpful_path():
    #Navigate to ./Downloads directory
    csv_dir = "Downloads"
    system_dir = "System"
    uploads_dir = "Uploads"
    pathList = []
    backwards1 = os.path.abspath(__file__) 
    #/home/pi/pendulum/Uploads/ee4951W_pendulum_web/app/app/views.py
    backwards2 = os.path.dirname(backwards1) 
    #/home/pi/pendulum/Uploads/ee4951W_pendulum_web/app/app
    backwards3 = os.path.dirname(backwards2) 
    #/home/pi/pendulum/Uploads/ee4951W_pendulum_web/app
    backwards4 = os.path.dirname(backwards3)
    #/home/pi/pendulum/Uploads/ee4951W_pendulum_web
    backwards5 = os.path.dirname(backwards4) 
    #/home/pi/pendulum/Uploads
    backwards6 = os.path.dirname(backwards5) 
    #/home/pi/pendulum   
    sysPath = os.path.join(backwards6, system_dir)
    downloadsPath = os.path.join(sysPath, csv_dir)
    uploadsPath = os.path.join(sysPath, uploads_dir)
    
    pathList.append(backwards2) #/home/pi/pendulum/Uploads/ee4951W_pendulum_web/app/app
    pathList.append(sysPath) #/home/pi/pendulum/System 
    pathList.append(downloadsPath) #/home/pi/pendulum/System/Downloads
    pathList.append(uploadsPath) #/home/pi/pendulum/System/Uploads
    
    
    return pathList
    
def delete_uploads_files():
    # ---------------------------------Remove contents of Uploads folder------------------------------------------------------
    
    paths = get_helpful_path()
    # Get list of all files in Uploads folder
    uploads_files_list = os.listdir(paths[3])

    # Remove all files in Uploads folder
    for j in uploads_files_list:
        os.remove(paths[3]+"/"+j)

    # Delete Uploads folder
    try:
        os.rmdir(paths[3])
    except OSError as e:
        print("Error: %s : %s" % (paths[3], e.strerror))
    os.chdir(paths[0])
    
@app.route('/call_subprocess')
def run_test_file():
    
    the_list = get_helpful_path()

    # If testing the software functionality but not actuating the PENDULUM, 
    # please comment the lines/blocks of code between the lines that only have the comment "software" 
    # P.S. they are only found in this function!!
    
    #software
    global processA
    global process
    mtr = Motor(17,27,22)
    mtr.brake()
    try:
        processA.terminate()
        print("Initialization actively terminated")
    except:
        print("Initialization already terminated")
    try:
        process.terminate()
        print("User file actively terminated")
    except:
        print("User file already terminated")
    mtr.brake()
    
    GPIO.cleanup()
    #software

    #-----------------------------------Run Test File-------------------------------------------------------------------------------------
    # Popen() has an array of command line arguments
    # "python3" is used because we are using a Raspbian OS terminal

    # Change directory so that we can run initialize_system.py
    #software
    os.chdir(the_list[1])
    #software
    
    # Run the initialize_system.py file
    #software
    processA = subprocess.Popen(["python3", INITIALIZE_SYSTEM])
    #software

    # The following waits for initialize_system.py to finish
    #software
    done = processA.poll()
    while done==None:
        done = processA.poll()
        time.sleep(0.5)
    #software

    # The line below is for Raspbian OS testing
    # subprocess.PIPE allows data to be sent to the process's stdin (standard input)
    process = subprocess.Popen(["python3", the_list[3] + "/" + PROCESSING_FILE], stdout = subprocess.PIPE, stderr = subprocess.PIPE)

    errorMessageList = process.communicate(timeout = None)

    # errorMessageList[0] is for stdout_data
    # errorMessageList[1] is for stderr_data

    global popenErrorString
    popenErrorString = errorMessageList[1]
    # Use popenErrorString in /results route 
    
    # The line below is for WINDOWS OS testing
    #process = subprocess.Popen(["python", UPLOAD_DESTINATION + "/" + PROCESSING_FILE])

    try:
        process.wait()
        print("Program exited normally!\n")
    except:
        print("Exception occurred running program!\n")
        process.terminate()
    
    # For processA
    #software
    processA.terminate()
    #software
    os.chdir(the_list[0])
    return redirect(url_for('results_page'))

@app.route('/results')
def results_page():
    # Display this message in the website to show 
    flash(popenErrorString, "danger")
    # Todo: Need to figure out how to display one flash message or the other (line 278 or line 281)
    # Display this message in the website after the file has been uploaded
    #flash('File uploaded successfully!', "success")
    return render_template("results.html")

@app.route('/Downloads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    try:
        something = get_helpful_path()
        # Download directory = something[2]
        # Get to new download directory
        return send_from_directory(something[2], filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

# For the button that redirects the user to our GitHub repository
@app.route('/github_repo')
def gitHub_repo():
    return redirect("https://github.com/awalx003new/ee4951W_pendulum_web")

#--------------------------------Run the application-----------------------------------------
if __name__ == '__main__':
    # Change to the directory that contains this Python file you are currently reading (views.py)
    os.chdir("/home/pi/pendulum/Uploads/ee4951W_pendulum_web/app/app")
    
    #IMPORTANT: DNS=192.168.71.241
    # Uncomment the line below is to run the server in debug mode - any errors will be indicated in the web browser 
    #app.run(debug=True)
    # Allow operating system to listen on all public IP Addresses
    app.run(host='0.0.0.0', port=8080, threaded=True)


