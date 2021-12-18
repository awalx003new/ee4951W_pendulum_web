# This is the web interface for the EE 4951W Remotely Accessed Inverted Pendulum

Explanation of the File Directory Structure:
(The base template used for the following is from: https://pythonise.com/series/learning-flask/jinja-template-inheritance)

Please note: “the website” refers to the website that you see when you execute “views.py” in a terminal and enter the DNS name (or static IP address) specified in the 2021 Senior Design Team’s Hand Off Report into a web browser’s address bar.

“Was left unedited” means that the file was downloaded (from the internet) to aid with the file directory structure or with custom CSS formatting.  Some of these files were determined to fit into the file directory structure based upon error messages displayed by the terminal when initially running the web server.  

File Directory Structure in this GitHub Repository:
app (folder)
├── app (folder)
│   ├── __init__.py (blank file)
│   ├── admin_views.py (Was left unedited)
│   ├── led.py (Was used to test a Raspberry Pi through the web server if you are not in the Controls Lab)
│   ├── test_script.py (Upload this file to the website to test ONLY the web server and no hardware)
│   ├── static (folder)
│   │   ├── css (folder)
│   │   │   ├── style.css (File for adding fonts, color, etc to visual elements)
│   │   │   ├── bootstrap.min.css (Was left unedited)
│   │   │   ├── bootstrap.min.css.map (Was left unedited)
│   │   │   └── font-awesome.min.css (Was left unedited)
│   │   ├── img (folder)
│   │   │   ├── flask.png (Was left unedited)
|   |   |   └── site_logo.png (File for the logo displayed on website)
│   │   └── js (folder)
│   │       ├── app.js (File for motion of the progress bar, etc)
│   │       ├── bootstrap.bundle.min.js (Was left unedited)
│   │       ├── bootstrap.bundle.min.js.map (Was left unedited)
│   │       └── jquery.slim.min.js (Was left unedited)
│   ├── templates (folder)
│   │   ├── admin (folder)
│   │   │   ├── dashboard.html (Was left unedited)
│   │   │   └── templates (folder)
│   │   │        └── admin_template.html (Was left unedited)
│   │   ├── public (folder)
│   │   │   └── templates (folder)
│   │   │        └── public_template.html (Was left unedited)
│   │   ├── base.html (File for the main web page of the website)
│   │   ├── index.html (File for the second web page of the website)
│   │   └── results.html (File for the third web page of the website)
│   └── views.py (Application root: File for all the web server operations: POST/GET requests, etc)
├── requirements.txt (Was left unedited)
└── run.py (Was left unedited)
