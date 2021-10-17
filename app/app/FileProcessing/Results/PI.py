#handle a POST request
from flask import Flask, render_template, request, url_for, jsonify, make_response
import subprocess
import os
app = Flask(__name__)

UPLOAD_DESTINATION = "Uploads/"

RESULTS_DESTINATION = "Results/"

@app.route('/')
def home():
    return "ANDI'S PIE"

@app.route('/favicon.ico') #brings up 500 status code, does not currently affect performance
def favicon():             # TODO: look into 500 status code later
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',mimetype='image/vnd/microsoft.icon')

@app.route('/tests/endpoint', methods=['POST'])
def my_test_endpoint():
    # Receive post
    input_json = request.get_json(force=True)

    # Put file content into a file caled upload.py
    filename=input_json['filename'].encode("ascii")
    file_content=input_json['file_content'].encode("ascii")
    upload = open(UPLOAD_DESTINATION + filename, "w")
    upload.write(file_content)
    upload.close()

    # Run python script
    subprocess.call(["python", UPLOAD_DESTINATION + filename])

    # Get results file
    results_filename = filename.split(".")[0]
    results_filename = results_filename + "_results.csv"
    with open(RESULTS_DESTINATION + results_filename, 'r') as results:
        results_content = results.read()
        results.close()

    # Remove test file and results file now that were done with them
    os.remove(UPLOAD_DESTINATION + filename)
    os.remove(RESULTS_DESTINATION + results_filename)

    # Return results file content
    dictToReturn = {'results_filename':results_filename, 'results_content':results_content}
    return make_response(jsonify(dictToReturn),200)

if __name__ == '__main__':
    app.run(host="localhost", port=8000)
    # UNCOMMENT IF RUNNING PI.PI ON PI
    #app.run(host="192.168.1.10", port=8000)
