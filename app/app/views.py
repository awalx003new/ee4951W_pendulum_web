#---------------------------------------------------------imports---------------------------------------------------------------#
from flask import Flask, jsonify, request, render_template, make_response, redirect, url_for, send_from_directory, flash, Request
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static')
# The 'static' argument is the folder with static files that is served at

# Set the secret key to some random bytes. Needs to be top secret!
# For POST request
app.secret_key = "ski u mah"

# Maximum file size is 16 MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

# Uploads folder is in current directory
app.config['UPLOAD_FOLDER'] = "./FileProcessing/Uploads"

DOWNLOAD_DIRECTORY = "./FileProcessing/Downloads"

UPLOAD_DESTINATION = "./FileProcessing/Uploads"
RESULTS_DESTINATION = "./FileProcessing/Results"

ALLOWED_EXTENSIONS = {'py'}
#PROCESSING_FILE = "upload.py"

# Create an 'Uploads' directory in a known location --> this directory is where files are saved to
#uploads_directory = os.path.join(app.instance_path, UPLOAD_DESTINATION)
#os.makedirs(uploads_directory, exist_ok=True)

#---------------------------------------------------------methods------------------------------------------------------------------#
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
# Receive form data from upload button
@app.route('/index', methods=['POST'])
def upload_file():
    # Check if the POST request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return render_template("index.html")

    #fileSize = request.cookies.get("filesize")

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        # Display this message in the website when the user has not chosen a file
        flash('No file selected for uploading', "warning")
        return render_template("index.html")

    if uploaded_file and allowed_file(uploaded_file.filename):
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
        processingFile = open(UPLOAD_DESTINATION + "/" + "upload.py", "w+")

        # write the "file_content" to the upload file object
        processingFile.write(fileContents)

        # Close the upload.py file object
        processingFile.close()

        # Retrieve the name of the userFile - without the file extension "py"
        results_custom_filename = nameOfFile.split(".")[0]

        # Create custom filename for results.csv file
        results_custom_filename = results_custom_filename + "_results.csv"

        # Now, actually create that file
        customResultsFile = open(RESULTS_DESTINATION + "/" + results_custom_filename, "x")

        # Close that file
        customResultsFile.close()

        # Name of file object is "results" - open it in read mode
        with open(RESULTS_DESTINATION + "/" + results_custom_filename, "r") as customResultsFile:
            resultsContents = customResultsFile.read()
            customResultsFile.close()
    else:
        # Display this message in the website when the user has chosen a non-Python file
        flash('The file type specified is not allowed for upload.  Allowed file type is .py', "danger")
        return render_template('index.html')

    #PLEASE note: What's below seems to work, but something I noticed is that if the test file has "import" lines, those modules that Python is looking for won't be found
    # Run new python script
    # Popen has an array of command line arguments; execute "python" program, with ("Uploads/" conconcatenated with "filename") command for process
    # "python3" is used because we are using a Linux operating system on the NVIDIA Jetson?
    #process = subprocess.Popen(["python3", UPLOAD_DESTINATION + "/" + "upload.py"])

    #try:
        # Wait for completion of child process
        #process.wait()
        #print("Program exited normally!\n")
    #except:
        #print("Exception occurred running program!\n")
        #process.terminate()
    #finally:
        #GPIO.cleanup()

    #-------------------------------------------------------------
    # Test the os.remove after affirming operation of running new python script
    # Remove test file and custom results file now that we are done with them
    #os.remove(UPLOAD_DESTINATION + "/" + "upload.py")
    #os.remove(RESULTS_DESTINATION + "/" + results_custom_filename)

    #-----------------------------------------------------------------
    return redirect(url_for('results_page'))
    #return render_template("index.html")
    #return "File upload is successful!"

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

# For button that redirects the user to our GitHub repository
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
    #repopulate app.routes with static IP address for controls lab
    #Use Sam's domain name (DNS) instead of local host
    #DNS=192.168.71.241
    #app.run(host="<IP_Address>", port=<port_number>, debug=True)
    app.run(debug=True)
