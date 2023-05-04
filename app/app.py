import os
import json
#from sklearn.pipeline import Pipeline

from os.path import join, dirname, realpath
from flask import Flask, request, redirect, url_for, send_from_directory, render_template, flash
from werkzeug.utils import secure_filename


from hello import p

UPLOAD_FOLDER = join(dirname(realpath('__file__')), 'static/uploads')
ALLOWED_EXTENSIONS = {'png', 'PNG', 'jpg', 'JPG', 'jpeg', 'JPEG', 'gif', 'GIF'}

app = Flask(__name__)
#app = Flask(__name__, template_folder='../templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.secret_key = 'key'

DAMAGE_LOCATION=""
SEVERIETY_OF_DAMAGE=""


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return render_template('index.html', result=None)


@app.route('/assessment', methods=['GET', 'POST'])
def upload_and_classify():
    global DAMAGE_LOCATION
    global SEVERIETY_OF_DAMAGE
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('assess'))

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('assess'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            model_results = p.pipe(filepath)
            DAMAGE_LOCATION=model_results['location']
            SEVERIETY_OF_DAMAGE=model_results['severity']
            
            return render_template('results.html', result=model_results, scroll='third', filename=filename)

    flash('Invalid file format. Please try again.')
    return redirect(url_for('assess'))
    
@app.route("/predict", methods = ["GET", "POST"])
def predict():
    if request.method == "POST":
        with open("converted_data.json","r") as f:
            cost_estimation_data=json.load(f)

        Total_cost=0
        brand = request.form["Brand"]
        Model=request.form["Model"]
        Damaged_Part=request.form.getlist("parts")
        for part in Damaged_Part:
            fd=(brand,Model,DAMAGE_LOCATION.upper(),SEVERIETY_OF_DAMAGE.upper(),part)
            fd=",".join(fd)
            print(fd)
            get_value=cost_estimation_data.get(fd)
            if get_value:
                Total_cost +=get_value
        if Total_cost:
            prediction_text="Your car damage estimation cost Rs. {}".format(Total_cost)
        else:
            prediction_text="Sorry We can't estimate your car damage cost"

        return render_template('home.html',prediction_text=prediction_text)
       


    return render_template("home.html")


@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False,)
