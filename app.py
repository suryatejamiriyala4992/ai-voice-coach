from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import shutil
from werkzeug.utils import secure_filename
from analysis import analyze_speech

UPLOAD_FOLDER = 'uploads'
STATIC_UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'super_secret_key'
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_path)

            print("TEMP FILE EXISTS:", os.path.exists(temp_path))
            if not os.path.exists(temp_path):
                flash("File could not be saved. Please try again.")
                return redirect(request.url)

            static_path = os.path.join(STATIC_UPLOAD_FOLDER, filename)
            shutil.copy(temp_path, static_path)

            try:
                feedback, transcript, word_freq, filler_count = analyze_speech(temp_path)
                session['transcript'] = transcript
                session['feedback'] = feedback
                session['word_freq'] = word_freq
                session['filler_count'] = filler_count
                session['audio_file'] = filename

                # ✅ Redirect to report after analysis
                return redirect(url_for('report'))

            except Exception as e:
                flash(f"Error analyzing audio: {e}")
                return redirect(request.url)
        else:
            flash("Invalid file type. Please upload a .wav, .mp3, or .m4a file.")
            return redirect(request.url)

    return render_template("index.html")

@app.route('/report')
def report():
    transcript = session.get('transcript')
    feedback = session.get('feedback')
    word_freq = session.get('word_freq')
    filler_count = session.get('filler_count')
    if not transcript or not feedback:
        flash("No report available. Please upload a file first.")
        return redirect(url_for('index'))
    return render_template("report.html", transcript=transcript, feedback=feedback, word_freq=word_freq, filler_count=filler_count)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/how-it-works')
def how_it_works():
    return render_template("how_it_works.html")

@app.route('/why-us')
def why_us():
    return render_template("why_us.html")

@app.errorhandler(413)
def file_too_large(e):
    return "File is too large. Please upload a file under 100MB.", 413

if __name__ == '__main__':
    app.run(debug=True)
