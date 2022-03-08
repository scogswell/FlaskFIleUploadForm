# A "complete" demo program flow example of using Flask to upload a file, with a form for 
# additional information and maintaining flask-wtf/wtforms validation.  
#
# 1. Make a virtual environment:
#       python -m venv .venv
#       . .venv.bin/activate
# 2. Install requirements automatically (flask, flask-wtf, email-validator):
#       python -m pip install --upgrade pip 
#       pip install -r requirements.txt
# 3. Set development server for demo if desired:
#       export FLASK_ENV=development
# 4. Run!  
#       flask run  
#       (alternately) python app.py
# 5. Navigate in web browser to displayed url http://127.0.0.1:5000/
#
# There are copious print() statments so you can follow program flow either in the terminal or in
# visual studio code. 
#
# This uses (some) of bootstrap4 for display, particularly to get the progress bar graphic itself.  
# Bootstrap is not required otherwise.  
# Templates are littered with bootstrap 'stuff' as a result, you could make it cleaner using either
# flask-bootstrap (bootstrap 3) https://pythonhosted.org/Flask-Bootstrap/ 
# or bootstrap-flask (bootstrap4/bootstrap5) https://bootstrap-flask.readthedocs.io/en/stable/
#
# Steven Cogswell 
#
# This is based on upload/progress display from https://pythonise.com/categories/javascript/upload-progress-bar-xmlhttprequest
#
# 
import os, uuid
from flask import Flask, render_template, request, make_response, jsonify, redirect, url_for, flash, send_from_directory
from forms import UploadForm
from werkzeug.utils import secure_filename

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
print("Remember FLASK_ENV=development for debugging")

app.config.update(
    UPLOADED_PATH=os.path.join(basedir, 'uploads'),  # storage for uploaded files  
    SECRET_KEY = "you-know-this"  # a SECRET_key is required for csrf forms in wtforms
)

# this is the entry point but this is just a demo program so get right to it. 
@app.route('/')
def index():
    return redirect(url_for('upload_file'))


@app.route("/upload-file", methods=["GET", "POST"])
def upload_file():
    """This routine does all the work.  The lifecycle is: 
        1. First pass: upload_file() is a blank form (name/email fields and continue button) are shown.  
           File upload widget is not shown.
        2. If, on submission, the form does not validate the name/email fields, go back to step 1
        3. If form validates, lock the name/email fields and show the upload file section
        4. The actual upload is done via XMLHttpRequest in progress.js.  The page elements are manipulated by 
           progress.js to display a progress bar and provide cancel buttons and success/error displays.  
           As part of the file upload, progress.js also pushes the form data for name/email/csrf_token along as part 
           of the request, so that in the next step we have "normal" form elements and validation available to us.  
           Also it passes along the original filename, and the file it was stored in the uploads directory. In this 
           program we save the file with a uuid for a filename so no clashes if the same file gets uploaded twice.
           When progress.js has finished POST'ing the file and additional form data, upload_file() is called again via
           javascript with a file available in the form data, upload_file() sees this and then saves the file to the local
           uploads directory set in the app.config.
           During the XMLHttpRequest upload_file() has to communicate with the javascript via JSON so it can't 
           return a template when finished.  
        5. To process the uploaded file and form data and get another template to render after the upload finishes, as a final step, 
           the upload in progress.js fires the "submit" event on the  form (which previously validated) and sends 
           everything to "completed_upload()".  We now have available to usall the data from the previous form (name/email),
           the filename of the original uploaded file, and the filename  of the file when it was saved in the uploads folder.
           You can then use database stuff (e.g. flask-sqlalchemy) to store these records.  
    """
    form = UploadForm()
    # Generate a unique uuid, we will save the file with this as the filename into the uploads folder
    # to prevent clashing
    uuidname = uuid.uuid4()  
    print("the chosen uuid name is [{}]".format(uuidname))
    print("/upload-files: here we are")
    print("/upload-files: name: [{}]".format(form.name.data))
    print("/upload-files: email: [{}]".format(form.email.data))
    # States we could get here in:
    #    A. form UploadForm not validated, either first display or a field validation failure from being submitted.  
    #    B. form UploafForm validated, but no 'file' in POST data, we haven't uploaded anything yet, show the upload file controls
    #    C. form UploadForm validated, 'file' is in POST data, everything was submitted and the XMLHttpUpload function
    #       in progress.js transferred the file data.
    #
    # If the form has validated, then we've already been through this at least once, set the flag "okaytogo=True"
    # to tell the template upload_file.html to show the upload file field and button. 
    if form.validate_on_submit():
        # This is state (B) or (C) above 
        print("Form validated")
        print("name: [{}]".format(form.name.data))
        print("email: [{}]".format(form.email.data))
        # If no 'file' is available then we're just on the pass showing the upload button, it hasn't 
        # actually uploaded a file yet.  
        if 'file' not in request.files:
            # This is state (B) above 
            return render_template("upload_file.html", form=form, uuidname=uuidname, okaytogo=True)
        else:
            # At this point all the javascript from progress.js ran and submitted the file upload, along
            # with replicated form data for name/email/csrf_token so we have those available and the 
            # form validated. 
            if request.method == "POST":
                # This is state (C) above 
                print("/upload-files: processing POST information")
                file = request.files["file"]
                for key, f in request.files.items():
                    if key.startswith('file'):
                        # Note, when working with submitted data use werkzeug's secure_filename() 
                        # to sanitize things to keep shady things from happening.  
                        # the uuid should be secure by default but why not make sure.  
                        # These two parameters are hidden fields sent up along with the 
                        # file in the XMLHttpupload function.
                        # We set the values for the hidden fields in the XMLHttpupload function 
                        # in progress.js and not here because this form will never get submitted
                        # at this point as we're running the endpoint for json function.  
                        originalfilename=secure_filename(form.original_filename.data)
                        savedfilename = secure_filename(form.saved_filename.data)
                        print("/upload-file: original filename is [{}]".format(originalfilename))
                        print("/upload-file: saved filename is [{}]".format(savedfilename))
                        print("/upload-file: Saving file into uploads directory...")
                        # This is a possible long-time operation of taking all the uploaded data
                        # which was part of the POST submission and saving the file into the 
                        # uploads directory.  
                        f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
                        print("/upload-file: File is saved: {} is {}".format(f.filename, file))
                        # Signal the XMLHttpUpload function in progress.js that we're done. 
                        # the upload() function in progress.js will then fire the form submit
                        # and take us to the completed_upload() function
                        res = make_response(jsonify({"message": "File uploaded"}), 200)
                return res
    else:
        if 'file' not in request.files:
            # This is state (A) above 
            print("Form did not validate {}".format(form.errors))
            return render_template("upload_file.html", form=form, uuidname=uuidname, okaytogo=False)
        else:
            # This path happens if there's an upload error, and doesn't return a template beacuse the 
            # XMLHttpUpload function will put up an error message on the form to read. 
            print("/upload-file: Some sort of validation error happened during upload: {}".format(form.errors))
            print("Make sure you're sending all your validating fields back in the javascript function")
            # Tell the javascript upload function there was an error 
            res = make_response(jsonify({"message": "Data did not validate"}), 400)
            return res

    return render_template("upload_file.html", form=form, uuidname=uuidname)

@app.route("/complete", methods=["GET", "POST"])
def completed_upload():
    """This function gets called after the upload_file() form has validated, and the file uploaded via POST.
    """
    form=UploadForm()
    # again, don't trust filenames that might be shady.  Use secure_filename from werkzeug.  
    secure_original_name = secure_filename(form.original_filename.data)
    secure_saved_name = secure_filename(form.saved_filename.data)
    print("/complete: name is [{}] email is [{}]".format(form.name.data, form.email.data))
    print("/complete: original file name is [{}]".format(secure_original_name))
    print("/complete: saved filename is [{}]".format(secure_saved_name))
    # This should validate, since everything was validated before we came in.  
    if form.validate_on_submit():
        print("/complete: we have validated")
        # You could do more things like do database work storing information since you have all the 
        # information now in the UploadForm() data.
        return render_template('completed.html', form=form)
    else:
        # Everything validated before so we shouldn't get here unless something went terribly terribly wrong.  
        print("/complete: errors {}".format(form.errors))
        for error in form.name.errors:
            flash("Name: {}".format(error))
        for error in form.email.errors:
            flash("Email: {}".format(error))    
        return redirect(url_for('upload_file'))

@app.route("/download", methods=[ "GET", "POST"])
def download_file():
    """Provide a download link to get the file back, just to demonstrate using the attachment_filename
       paramater so you can return the file with it's original name from the uuid storage name. 
       As usual use werkzeug's secure_filename to make sure the filename isn't doing some shady stuff.
    """
    uuid = request.args.get('uuid')
    filename = secure_filename(request.args.get('filename'))
    storagedirectory = app.config['UPLOADED_PATH']
    print("Download {} as {}".format(uuid, filename))
    return send_from_directory(directory=storagedirectory, path=uuid, as_attachment=True, attachment_filename=filename)


if __name__ == '__main__':
    app.run(debug=True)