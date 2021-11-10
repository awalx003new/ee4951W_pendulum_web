#---------------------------------------------------------imports-------------------------------------------------------------------------#
from flask import Flask, jsonify, request, render_template, make_response, redirect, url_for, send_from_directory, flash, Request, Response
# Use for operating system functionalities
import os
# Use for generating random secret key
import secrets
# Use for running a python script
import subprocess
#import RPi.GPIO as GPIO
from werkzeug.utils import secure_filename
import time # Used for sleep()

# The 'static_folder' argument is the folder with static files that is served at
app = Flask(__name__, static_folder='static')

# Set the secret key to some random bytes. Needs to be top secret!
# Needed for POST request
app.secret_key = secrets.token_hex()

# Maximum file size is 16 MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

DOWNLOAD_DIRECTORY = "./FileProcessing/Downloads"
UPLOAD_DESTINATION = "."
RESULTS_DESTINATION = "."
INITIALIZE_SYSTEM = "initialize_system.py"

# Uploads folder is in current directory after changing directory to ./FileProcessing/Uploads directory
app.config['UPLOAD_FOLDER'] = UPLOAD_DESTINATION

ALLOWED_EXTENSIONS = {'py'}
# Name of test file
PROCESSING_FILE = "upload.py"

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
        # # Create "Uploads" folder
        # uploads_dir = "Uploads"
        #
        # absolutepath = os.path.abspath(__file__)
        #
        # fileDirectory = os.path.dirname(absolutepath)
        #
        # #Navigate to ./FileProcessing directory
        # newPath1 = os.path.join(fileDirectory, 'FileProcessing')
        #
        # #Navigate to ./Uploads directory
        # newPath2 = os.path.join(newPath1, uploads_dir)


        p1 = get_file_processing_path()
        #print("First - get file processing path")
        #print(os.getcwd())
        # print("This is p1")
        # print(p1)

        p2 = get_uploads_path(p1)
        #print("Second - get file processing path")
        #print(os.getcwd())
        # print("This is p2")
        # print(p2)


        # Make directory called "Uploads"
        # mode: read, write, and execute permissions for user, owner, and group
        mode = 0o777
        os.mkdir(p2, mode)

        # change directory to "Uploads"
        os.chdir(p2)

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


        # Retrieve the name of the userFile - without the file extension "py"
        results_custom_filename = nameOfFile.split(".")[0]

        # Create custom filename for results.csv file
        results_custom_filename = results_custom_filename + "_results.csv"

        #--------------------------------------------Create "Results" folder---------------------------------------------------

        p3 = get_results_path(p1);
        print("Third - get file processing path")
        print(os.getcwd())
        # print("This is p3")
        # print(p3)

        # Make directory called "Results"
        os.mkdir(p3, mode)

        # change directory to "Results"
        os.chdir(p3)

        # Now, actually create that file
        customResultsFile = open(RESULTS_DESTINATION + "/" + results_custom_filename, "x")

        # Close that file
        customResultsFile.close()

        # Name of file object is "results" - open it in read mode
        with open(RESULTS_DESTINATION + "/" + results_custom_filename, "r") as customResultsFile:
            resultsContents = customResultsFile.read()
            # "customResultsFile.close()" automatically called with "with...as" statement
        
        #Navigate up the directory TWICE to reset the current working directory for 
        #later calls to get_file_processing_path() and get_uploads_path()
        os.chdir("..")
        os.chdir("..")
	
        #print("Cur dir A")
        #print(os.getcwd())
    else:
        # Display this message in the website when the user has chosen a non-Python file
        flash('The file type specified is not allowed for upload.  Allowed file type is .py', "danger")
        return render_template('index.html')

    #--------------------------------------------------------------------------------------------------------------------------
    #print("Cur dir A")
    #Current working directory here is the Results folder
    #print(os.getcwd())
    #return redirect(url_for('results_page'))
    # Status code 204 is No Content - want to allow user to be able to click "Actuate" button on index.html page
    return Response(response=None, status=204)


def get_file_processing_path():
    # Create "Uploads" folder
    uploads_dir = "Uploads"

    absolutepath = os.path.abspath(__file__)

    #print("absolutepath")
    #print(absolutepath)

    fileDirectory = os.path.dirname(absolutepath)

    #print("fileDirectory")
    #print(fileDirectory)

    #Navigate to ./FileProcessing directory
    newPath1 = os.path.join(fileDirectory, 'FileProcessing')
    
    #print("newPath1 - get file processing path")
    #print(newPath1)

    return newPath1

def get_uploads_path(file_processing_path):
    # Create "Uploads" folder
    uploads_dir1 = "Uploads"

    #Navigate to ./Uploads directory

    newPath2 = os.path.join(file_processing_path, uploads_dir1)

    #print("newPath2 - get_uploads_path")
    #print(newPath2)

    return newPath2

def get_results_path(file_processing_path):
    results_dir = "Results"

    #Navigate to ./Results directory
    newPath3 = os.path.join(file_processing_path, results_dir)

    #print("newPath3 - get_results_path")
    #print(newPath3)

    return newPath3

def delete_files():
    #---------------------------------Remove contents of Results folder------------------------------------------------------

    #print("Current working directory in delete_files()")
    #print(os.getcwd())

    #Change back to app/app/ folder (from current working directory) so we can properly delete Results folder later on
    os.chdir("..")
    os.chdir("..")

    #print("Current working directory in delete_files()")
    #print(os.getcwd())

    newPath1 = get_file_processing_path()
    #print("newPath1")
    #print(newPath1)
    newPath2 = get_uploads_path(newPath1)
    #print("newPath2")
    #print(newPath2)
    newPath3 = get_results_path(newPath1)
    #print("newPath3")
    #print(newPath3)

    # Get list of all files in Results folder
    results_files_list = os.listdir(newPath3)

    # Remove all files in Results folder
    for i in results_files_list:
        os.remove(newPath3+"/"+i)
        #print("here A")

    try:
        os.rmdir(newPath3)
        #print("here B")
    except OSError as e:
        print("Error: %s : %s" % (newPath3, e.strerror))

    # ---------------------------------Remove contents of Uploads folder------------------------------------------------------
    # Here, we are still at the FileProcessing folder

    # Get list of all files in Uploads folder
    results_files_list = os.listdir(newPath2)

    # Remove all files in Uploads folder
    for j in results_files_list:
        os.remove(newPath2+"/"+j)
        #print("here C")

    # Delete Uploads folder
    try:
        os.rmdir(newPath2)
        #print("here D")
    except OSError as e:
        print("Error: %s : %s" % (newPath2, e.strerror))

@app.route('/call_subprocess')
def run_test_file():
    #print("1")
    firstPath = get_file_processing_path()
    #print("Fourth - get file processing path")
    #print(os.getcwd())
    #print("This is firstPath")
    #print(firstPath)

    secondPath = get_uploads_path(firstPath)
    #print("Fifth - get file processing path")
    #print(os.getcwd())
    #print("This is secondPath")
    #print(secondPath)
    
    #print("EXTRA COMMENTS HERE")


    # Create "Uploads" folder
    uploads_dir1 = "Uploads"
   
    absolutepath1 = os.path.abspath(__file__)
    #print("absolutepath1")
    #print(absolutepath1)

    fileDirectory1 = os.path.dirname(absolutepath1)
    #print("fileDirectory1")
    #print(fileDirectory1)

    #Navigate to ./FileProcessing directory
    newPath4 = os.path.join(fileDirectory1, 'FileProcessing')
    #newPath4 = fileDirectory1
    #print("newPath4")
    #print(newPath4)

    #Navigate to ./Uploads directory
    newPath5 = os.path.join(newPath4, uploads_dir1)
    #print("newPath5")
    #print(newPath5)

    os.chdir(newPath5)

    #print("Current working directory (run_test_file): ")
    #print(os.getcwd())

    #-----------------------------------Run Test File--------------------------------------------------------------------------------------

    #PLEASE note: What's below seems to work, but something I noticed is that if the test file has "import" lines, those modules that Python is looking for won't be found
    # Run new python script
    # Popen has an array of command line arguments; execute "python3" program, with ("Uploads/" conconcatenated with "filename") command for process
    # "python3" is used because we are using a Raspberry Pi terminal
    # process = subprocess.Popen(["python3", UPLOAD_DESTINATION + "/" + PROCESSING_FILE])
    # Run the initialize_system.py
    # Change directory so that we can run initialize_system.py
    os.chdir('/home/pi/pendulum/System')

    processA = subprocess.Popen(["python3", INITIALIZE_SYSTEM])
    # 20 second delay - wait for initialize_system.py to end
    time.sleep(10) 

    # FIX this - no hard coding!!!!!!!
    #os.chdir("/home/pi/pendulum/Uploads/ee4951W_pendulum_web/app/app/FileProcessing/Uploads")
    #os.chdir("/home/pi/pendulum/System")
    #os.symlink("/home/pi/pendulum/Uploads/ee4951W_pendulum_web/app/app/FileProcessing/Uploads","/home/pi/pendulum/System")
    #The line below is for LINUX testing
    process = subprocess.Popen(["python3", "/home/pi/pendulum/Uploads/ee4951W_pendulum_web/app/app/FileProcessing/Uploads" + "/" + PROCESSING_FILE])

    
    #The line below is for WINDOWS testing
    #process = subprocess.Popen(["python", UPLOAD_DESTINATION + "/" + PROCESSING_FILE])

    #Add timer - so that subprocess can stop after a certain amount of time
    #See https://stackoverflow.com/questions/42601478/flask-calling-python-function-on-button-onclick-event
    try:
        process.wait()
        print("Program exited normally!\n")
    except:
        print("Exception occurred running program!\n")
        process.terminate()
    finally:
        #Make sure this works
        #GPIO.cleanup()
        os.chdir("/home/pi/pendulum/Uploads/ee4951W_pendulum_web/app/app/FileProcessing/Uploads")
        delete_files()

    # For processA
    processA.terminate()
    return redirect(url_for('results_page'))

@app.route('/results')
def results_page():
    # Display this message in the website after the file has been uploaded
    flash('File uploaded successfully!', "success")
    return render_template("results.html")

@app.route('/Downloads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    try:
        return send_from_directory(DOWNLOAD_DIRECTORY, filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

# For the button that redirects the user to our GitHub repository
@app.route('/github_repo')
def gitHub_repo():
    return redirect("https://github.com/awalx003new/ee4951W_pendulum_web")

#--------------------------------Run the application-----------------------------------------
if __name__ == '__main__':
    print("line 1")
    os.chdir('/home/pi/pendulum/System')
    print("line 2")
    print("current working directory - main")
    print(os.getcwd())
    print("line 3")
    #counter = 0
    #counter = counter + 1
    #if counter== 1:
           # Initialize the system before accepting any files.
           #subprocess.Popen(["python3", SYSTEM_DESTINATION + INITIALIZE_SYSTEM])
    print("line 4")
    # Run the web client to start receiving files.
    #app.run(host="192.168.1.10", port=8000)

    os.chdir("/home/pi/pendulum/Uploads/ee4951W_pendulum_web/app/app")
    print("line 5")
    #repopulate app.routes with static IP address for controls lab
    #Use Sam's domain name (DNS) instead of local host
    #IMPORTANT: DNS=192.168.71.241
    #app.run(host="<IP_Address>", port=<port_number>, debug=True)
    app.run(debug=True)
    # Allow operating system to listen on all public IP Addresses
    # app.run(host='0.0.0.0')
