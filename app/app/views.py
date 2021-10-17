#---------------------------------------------------------imports---------------------------------------------------------------#
from flask import Flask, jsonify, request, render_template, make_response, redirect, url_for, send_from_directory, flash, Request
# Use for operating system functionalities
import os
# Use for generating random secret key
import secrets
# Use for running a python script
import subprocess
from werkzeug.utils import secure_filename

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

    #fileSize = request.cookies.get("filesize")

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        # Display this message in the website when the user has not chosen a file
        flash('No file selected for uploading', "warning")
        return render_template("index.html")

    if uploaded_file and allowed_file(uploaded_file.filename):
        # Create "Uploads" folder
        uploads_dir = "Uploads"

        absolutepath = os.path.abspath(__file__)
        #print(absolutepath)

        fileDirectory = os.path.dirname(absolutepath)
        #print(fileDirectory)

        #Navigate to ./FileProcessing directory
        newPath1 = os.path.join(fileDirectory, 'FileProcessing')
        #print(newPath1)

        #Navigate to ./Uploads directory
        newPath2 = os.path.join(newPath1, uploads_dir)
        #print(newPath1)

        # Make directory called "Uploads"
        # mode: read, write, and execute permissions for user, owner, and group
        mode = 0o777
        os.mkdir(newPath2, mode)

        # change directory to "Uploads"
        os.chdir(newPath2)

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

        #-----------------------------------Run Test File--------------------------------------------------------------------------------------

        #PLEASE note: What's below seems to work, but something I noticed is that if the test file has "import" lines, those modules that Python is looking for won't be found
        # Run new python script
        # Popen has an array of command line arguments; execute "python3" program, with ("Uploads/" conconcatenated with "filename") command for process
        # "python3" is used because we are using a Raspberry Pi terminal
        #subprocess.Popen(["python3", UPLOAD_DESTINATION + "/" + PROCESSING_FILE])

        #-----------------------------------End of running Test File--------------------------------------------------------------------------------------

        # Retrieve the name of the userFile - without the file extension "py"
        results_custom_filename = nameOfFile.split(".")[0]

        # Create custom filename for results.csv file
        results_custom_filename = results_custom_filename + "_results.csv"

        #--------------------------------------------Create "Results" folder---------------------------------------------------

        results_dir = "Results"

        #Navigate to ./Results directory
        newPath3 = os.path.join(newPath1, results_dir)

        # Make directory called "Results"
        os.mkdir(newPath3, mode)

        # change directory to "Results"
        os.chdir(newPath3)

        # Now, actually create that file
        customResultsFile = open(RESULTS_DESTINATION + "/" + results_custom_filename, "x")

        # Close that file
        customResultsFile.close()

        # Name of file object is "results" - open it in read mode
        with open(RESULTS_DESTINATION + "/" + results_custom_filename, "r") as customResultsFile:
            resultsContents = customResultsFile.read()
            # "customResultsFile.close()" automatically called with "with...as" statement
    else:
        # Display this message in the website when the user has chosen a non-Python file
        flash('The file type specified is not allowed for upload.  Allowed file type is .py', "danger")
        return render_template('index.html')

    #try:
        # Wait for completion of child process
        #process.wait()
        #print("Program exited normally!\n")
    #except:
        #print("Exception occurred running program!\n")
        #process.terminate()
    #finally:
        #GPIO.cleanup()

    # ---------------------------------Remove contents of Results folder------------------------------------------------------

    # Change back to FileProcessing folder (from current working directory) so we can properly delete Results folder later on
    os.chdir("..")

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

    #--------------------------------------------------------------------------------------------------------------------------
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

# For the button that redirects the user to our GitHub repository
@app.route('/github_repo')
def gitHub_repo():
    return redirect("https://github.com/awalx003new/ee4951W_pendulum_web")

#--------------------------------Run the application-----------------------------------------
if __name__ == '__main__':
    #repopulate app.routes with static IP address for controls lab
    #Use Sam's domain name (DNS) instead of local host
    #IMPORTANT: DNS=192.168.71.241
    #app.run(host="<IP_Address>", port=<port_number>, debug=True)
    app.run(debug=True)
    # Allow operating system to listen on all public IP Addresses
    # app.run(host='0.0.0.0')
