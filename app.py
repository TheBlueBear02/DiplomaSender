from flask import Flask, render_template, request, redirect, url_for, flash
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create folder if it doesn't exist
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    """
    Render the main page.
    """
    return render_template('index.html')

@app.route('/upload-template', methods=['POST'])
def upload_template():
    """
    Handle diploma template upload.
    """
    if 'diploma_template' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))

    file = request.files['diploma_template']

    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        flash(f'File uploaded successfully: {file.filename}')
        return redirect(url_for('index'))

@app.route('/upload-recipients', methods=['POST'])
def upload_recipients():
    """
    Handle recipient list upload.
    """
    if 'recipient_list' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))

    file = request.files['recipient_list']

    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        flash(f'Recipient list uploaded successfully: {file.filename}')
        return redirect(url_for('index'))

@app.route('/send-test-email', methods=['POST'])
def send_test_email():
    """
    Placeholder for email sending logic.
    """
    email_subject = request.form.get('email_subject')
    email_body = request.form.get('email_body')

    # Replace with real email sending code
    flash(f'Test email sent with subject: "{email_subject}"')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Run the Flask app in debug mode for development
    app.run(debug=True)
