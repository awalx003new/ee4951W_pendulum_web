from flask import Flask, render_template
app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')
#Dealing with favicon.ico a 404 status code
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',mimetype='image/vnd/microsoft.icon')
if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')
  #192.168.0.12 dats our ip address
    
    