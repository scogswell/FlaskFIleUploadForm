# README

A "complete" demo program flow example of using Flask to upload a file with additional form fields for extra information and not losing the ability to use flask-wtf/wtforms validation.

Lots of demo code shows how to upload a file in Flask, but doesn't show how to upload and maintain state with information about the file.

I wrote this because I couldn't find a good demo of how do do file uploads in Flask along with extra fields, being able to show progress during the upload, *and* not have all my work validating forms with wtforms go to waste.  I wrote and tested this with visual studio code and that's the extent of how I've tried to use it.  I personally tried this with Firefox, Chrome, and Safari on MacOS X and hey it works for me so it must be perfect.  

This uses packages for `Flask`, `Flask-wtf`, `email-validation` and their dependencies.  

## How to use this

 1. Make a virtual environment:

        python -m venv .venv
        . .venv.bin/activate

 2. Install requirements automatically (flask, flask-wtf, email-validator):

        python -m pip install --upgrade pip 
        pip install -r requirements.txt

 3. Set development server for demo if desired:

        export FLASK_ENV=development

 4. Run!  

        flask run  

 5. Navigate in web browser to displayed url http://127.0.0.1:5000/

 There are copious `print()` statments so you can follow program flow either in the terminal or in
 visual studio code. 

 This uses (some) of bootstrap4 for display (css but not js), particularly to get the progress bar graphic itself.  Bootstrap is not required otherwise. Templates are littered with bootstrap 'stuff' as a result, you could make it cleaner using either:

 `flask-bootstrap` (bootstrap 3) https://pythonhosted.org/Flask-Bootstrap/ 

 or

 `bootstrap-flask` (bootstrap4/bootstrap5) https://bootstrap-flask.readthedocs.io/en/stable/

But I have not in order to keep the code "simpler" and readable without being mired in abstraction for bootstrap.

Likewise, since this is just a demo for how to do a thing, it doesn't actually do anything with that thing, so there's no use of databasing to manage data. 

Clean out the "uploads" folder after you're done playing with it, since nothing deletes your fake uploads.