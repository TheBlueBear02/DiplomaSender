from flask import Flask, render_template, request, redirect, url_for, flash
from flask import request, jsonify,session
import os
#from flask_mail import Mail, Message
import smtplib
import csv
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from io import BytesIO
import PyPDF2
from PIL import Image
from pdf2image import convert_from_path
# Email API related
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials


# Constants
TEST_NAME = "משה כהן"
TEST_EMAIL = "rony.gabbai@gmail.com"

WIDTH, HEIGHT = letter

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages
course_dir = os.path.join(app.root_path, 'static', 'course')
os.makedirs(course_dir, exist_ok=True)  # Create the directory if it doesn't exist
# Configure upload folder
#UPLOAD_FOLDER = 'static/uploads'
UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create folder if it doesn't exist
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    """
    Render the main page.
    """
    return render_template('index.html')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'csv', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload-template', methods=['POST']) 
def upload_template():
    print("upload_template() function called.")  # Debug log
    if 'diploma_template' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))

    file = request.files['diploma_template']

    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    print("rony1")
    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        try:
            print("rony2")
            file.save(filepath)
            session['uploaded_template'] = filepath
            print(f"Save session:{session['uploaded_template']}")
            flash(f'File uploaded successfully: {file.filename}')
        except Exception as e:
            flash(f'Error saving file: {str(e)}')
            return redirect(url_for('index'))        
    else:
        flash('Invalid file format. Please upload a PDF or PNG file.')

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


# Place name locattion 
@app.route('/place-name', methods=['POST'])
def place_name():
    """
    Handles placing the name on the PDF and returns the updated PDF URL.
    """
    try:
        # Extract data from the request
        student_name = request.form.get('student_name')
        x_position = request.form.get('x_position', int(WIDTH / 2))
        y_position = request.form.get('y_position', int(HEIGHT /2 ))

        print(f"Received student_name: {student_name}, x_position: {x_position}, y_position: {y_position}")

        # Ensure required parameters are provided
        if not student_name:
            print("Error: Student name is missing.")
            return jsonify({"error": "Student name is required"}), 400

        # Mock student data
        student = {"name": student_name}

        # Get the uploaded template path from session
        pdf_file = session.get('uploaded_template')
        print(f"pdf_file:{pdf_file}")
        if not pdf_file or not os.path.exists(pdf_file):
            return jsonify({"error": "Uploaded template not found. Please upload a template first."}), 400
        
        # Mock student data
        student = {"name": student_name}

        # Call the create_student_diploma function
         # Call the function with the file path
        create_student_diploma(student, test=False, pdf_file=pdf_file,x_pos=x_position,y_pos=y_position)

        # Assuming the output file path is determined in your function
        #pdf_url = f"/static/course/{student_name.replace(' ', '_')}_diploma.pdf"
        # Determine the relative web path for the updated PDF
        updated_pdf_url = f"/static/course/{student_name.replace(' ', '_')}_diploma.pdf"
        print(f"Diploma created successfully: {updated_pdf_url}")
        return jsonify({"success": True, "pdf_url": updated_pdf_url}), 200


    except Exception as e:
        print(f"Error placing name: {e}")
        return jsonify({"error": "An error occurred while placing the name"}), 500

import unicodedata

def is_hebrew(text):
    """
    Checks if the text contains primarily Hebrew characters.
    """
    hebrew_count = sum(1 for char in text if '\u0590' <= char <= '\u05FF')
    return hebrew_count > 0


# Generate student diploma
def create_student_diploma(student,test, pdf_file,x_pos,y_pos):
    if not test:
        student_name = student["name"]
        if is_hebrew(student_name):
            reversed_student_name = student_name[::-1]  # Reverse the student name
        else:
            reversed_student_name = student_name
    else: # test mode
        student_name = TEST_NAME
        if is_hebrew(student_name):
            reversed_student_name = student_name[::-1]  # Reverse the student name
        else:
            reversed_student_name = student_name
       
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    width, height = letter

    # Register and set the font that supports Hebrew
   
    pdfmetrics.registerFont(TTFont('Noto', 'Noto_Sans_Hebrew,Noto_Serif_Hebrew/Noto_Sans_Hebrew/static/NotoSansHebrew_Condensed-Bold.ttf'))
   # pdfmetrics.registerFont(TTFont('Noto', 'Noto_Serif_Hebrew/static/NotoSerifHebrew_Condensed-Bold.ttf'))
    can.setFont('Noto', 42)
    
    # Draw the student name at the placeholder location
    can.drawCentredString(int(x_pos), int(y_pos), reversed_student_name)
    #can.drawCentredString(width / 2.0, height - 350, reversed_student_name)

    can.save()
    
    # Move to the beginning of the StringIO buffer
    packet.seek(0)
    
    # Read the existing template PDF
    #template_pdf = PyPDF2.PdfReader(open("diploma_template.pdf", "rb"))
    template_pdf = PyPDF2.PdfReader(open(pdf_file, "rb"))

    existing_page = template_pdf.pages[0]
    
    # Create a new PDF with the student name
    new_pdf = PyPDF2.PdfReader(packet)
    overlay_page = new_pdf.pages[0]
    
    # Merge the overlay page with the template
    existing_page.merge_page(overlay_page)
    
    # Save the result to a new PDF
    output = PyPDF2.PdfWriter()
    output.add_page(existing_page)
    pdf_filename = f"static/course/{student_name.replace(' ', '_')}_diploma.pdf"
    jpg_filename = f"course/{student_name.replace(' ', '_')}_diploma.jpg"
    with open(pdf_filename, "wb") as output_stream:
        output.write(output_stream)
    
    # Convert the PDF to JPG
    convert_pdf_to_jpg(pdf_filename, student_name)

def convert_pdf_to_jpg(pdf_filename, student_name):
    images = convert_from_path(pdf_filename)
    jpg_filename = f"static/course/{student_name.replace(' ', '_')}_diploma.jpg"
    images[0].save(jpg_filename, 'JPEG')
    print(f"Saved {jpg_filename}")


@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    """
    Handle recipient list upload and process the CSV file.
    """
    if 'recipient_list' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['recipient_list']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the uploaded file temporarily
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Read and parse the CSV file
    try:
        students = read_students_from_csv(file_path)
        # Optionally delete the file after reading it
        os.remove(file_path)
        return jsonify({"success": True, "students": students}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to process CSV: {str(e)}"}), 500


# Read student data from the CSV file
def read_students_from_csv(file_path):
    students = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                first_name = row.get('first', '')
                last_name = row.get('last', '')
                email = row.get('email', '')
                full_name = f"{first_name} {last_name}"
                new = row.get('new', '')
                send = row.get('send', '')
                students.append({"name": full_name, "email": email, "new": new, "send": send})
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        raise e
    return students

# Create Email API connection
# Replace with your OAuth 2.0 credentials
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CLIENT_SECRETS_FILE = 'config/client_secrets.json'

@app.route('/connect_email', methods=['GET'])
def connect_email():
    # Create OAuth flow instance
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    flow.redirect_uri = url_for('oauth_callback', _external=True)
    
    # Get the authorization URL
    auth_url, _ = flow.authorization_url(prompt='consent')
    return redirect(auth_url)

@app.route('/oauth_callback', methods=['GET'])
def oauth_callback():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    flow.redirect_uri = url_for('oauth_callback', _external=True)
    
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    

    return "Email API connected successfully! You can now send emails."

if __name__ == '__main__':
    # Run the Flask app in debug mode for development
    app.run(debug=True)
