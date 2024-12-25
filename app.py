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
import pickle
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import re

# Constants
TEST_NAME = "רוני גבאי"
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


@app.route('/privacy_policy.html')
def privacy_policy():
    return render_template('privacy_policy.html')
@app.route('/terms_of_service.html')
def terms_of_service():
    return render_template('terms_of_service.html')

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
    
    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        try:
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

@app.route('/send_email', methods=['POST'])
def send_email():
    # Load credentials
    credentials = load_credentials()
    if not credentials:
        return jsonify({"error": "No valid credentials found. Please connect your email first."}), 400

    # Build Gmail API service
    service = build('gmail', 'v1', credentials=credentials)

    # Retrieve the students list from the session
    students = session.get('students')
    if not students:
        return jsonify({"Error": "No recipient list found. Please upload a recipient list first."}), 400
    # Parse request data
    data = request.get_json()
    if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400
    subject = data.get('subject', "Your Diploma is Ready!")
    body_template = data.get('body', "Hello, your diploma is attached.")

    

    # Iterate over the students and send emails
    results = []
    for student in students:
        to_email = student.get('email')
        print(f"Sending to email:{to_email}")
        #body = body_template.replace("{name}", student.get('name', 'Student'))
        # Convert text to HTML to support hebrew txt indent
        html_output = txt_to_html(body_template,student.get('name', 'Student'))
        body = html_output

        if not to_email:
            results.append({"name": student.get('name'), "error": "Missing email address"})
            continue
        
        x_position = session.get('x_position')
        y_position = session.get('y_position')

        # Get the uploaded template path from session
        pdf_file = session.get('uploaded_template')
        print(f"pdf_file:{pdf_file}")
        if not pdf_file or not os.path.exists(pdf_file):
            return jsonify({"error": "Uploaded template not found. Please upload a template first."}), 400
 
        # Create student diploma       
        create_student_diploma(student, test=False, pdf_file=pdf_file,x_pos=x_position,y_pos=y_position)

        # Path to the student's diploma PDF file
        pdf_filename = f"static/course/{student['name'].replace(' ', '_')}_diploma.pdf"
        print(f"pdf_file:{pdf_filename}")
        jpg_filename = f"static/course/{student['name'].replace(' ', '_')}_diploma.jpg"
        print(f"jpg_file:{jpg_filename}")
        # Create student diploma


        if not os.path.exists(pdf_filename):
            results.append({"name": student.get('name'), "error": "Diploma file not found"})
            print("file not found")
            continue

        try:
           
            message = MIMEMultipart()
            message['to'] = to_email or "rony.gabbai@gmail.com"
            message['subject'] = subject or "no subject"
            message['from'] = "me"


            # Add email body
            message.attach(MIMEText(body, "html", "utf-8"))
            # Attach the PDF file
            with open(pdf_filename, "rb") as pdf_file:
                pdf_attachment = MIMEApplication(pdf_file.read(), _subtype="pdf")
                pdf_attachment.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=os.path.basename(pdf_filename)
                )
                message.attach(pdf_attachment)

            # Attach the JPG file
            with open(jpg_filename, 'rb') as f:
                jpg_data = f.read()
                jpg_attachment = MIMEApplication(jpg_data, _subtype='jpeg')
                jpg_attachment.add_header('Content-Disposition', 'attachment', filename=jpg_filename)
                message.attach(jpg_attachment)  

            # Encode the email as base64
            try:
                raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            except Exception as e:
                print(f"Error encoding message: {e}")
            # Send the email
            #print(f"message:{message}")
            sent_message = service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
            results.append({"name": student.get('name'), "email": to_email, "message_id": sent_message['id']})
        except Exception as e:
            print("Send error")
            results.append({"name": student.get('name'), "email": to_email, "error": str(e)})

    return jsonify({"success": True, "results": results}), 200


# Place name location
@app.route('/place-name', methods=['POST'])
def place_name():
    """
    Handles placing the name on the PDF and returns the updated PDF URL.
    """
    try:
        # Extract data from the request
        student_name = TEST_NAME #request.form.get('student_name')
        x_position = request.form.get('x_position', int(WIDTH / 2))
        y_position = request.form.get('y_position', int(3*HEIGHT/4 ))
        # Save position
        session['x_position'] = x_position
        session['y_position'] = y_position
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
        print("D10")
        print(f"Error placing name: {e}")
        return jsonify({"error": "An error occurred while placing the name"}), 500

import unicodedata

def txt_to_html(txt, name, bullet_symbols=None):
    if bullet_symbols is None:
        bullet_symbols = ["💫"]  # Default bullet symbols
    
    html_template = """<!DOCTYPE html>
    <html lang="he">
    <head>
        <meta charset="UTF-8">
    </head>
    <body style="direction: rtl; text-align: right; font-family: Arial, sans-serif; color: #333333; margin: 20px;">
        {}
    </body>
    </html>"""
    # Regex to detect URLs
    url_pattern = re.compile(r"(http[s]?://[^\s]+)")

    # Replace {{name}} with the actual name
    txt = txt.replace("{{name}}", f'<span style="color: #ff6600;">{name}</span>')

    # Split text into lines
    lines = txt.strip().split("\n")

    html_body = ""
    for line in lines:
        if line.strip() == "":  # Skip empty lines
            continue
        elif any(line.startswith(symbol) for symbol in bullet_symbols):  # Handle general bullet symbols
            html_body += f'<p style="line-height: 1.4;font-weight: bold; margin-left: 10px;">{line}</p>\n'
        elif line.startswith("-"):  # List item
            html_body += f'<li style="margin-bottom: 10px;">{line[1:].strip()}</li>\n'
        else:  # Regular paragraph
            line = url_pattern.sub(r'<a href="\1" target="_blank" style="color: #0066cc; text-decoration: none;">\1</a>', line)
            html_body += f'<p style="line-height: 1.2;">{line}</p>\n'

    # Wrap in <ul> if it contains list items
    if "<li" in html_body:
        html_body = html_body.replace('<li', '<ul style="list-style-type: none; padding: 0;"><li', 1).replace('</li>\n', '</li></ul>\n', 1)

    
    # save the mail body
    #session['html_body'] = html_template.format(html_body)
    html_body =  html_template.format(html_body)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'html_body.html')
    try:
    # Write the HTML content to the file
        with open(filepath, 'w', encoding='utf-8') as html_file:
            html_file.write(html_body)
        print(f"HTML file saved to: {filepath}")
        return html_body
    except Exception as e:
        print(f"An error occurred while saving the HTML file: {e}")
        return None
    

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
        #os.remove(file_path)
        session['students'] = students
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

# Helper function to save credentials
def save_credentials(credentials):
    with open('token.pickle', 'wb') as token_file:
        pickle.dump(credentials, token_file)

# Helper function to load credentials
def load_credentials():
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token_file:
            return pickle.load(token_file)
    return None


@app.route('/connect_email', methods=['GET'])
def connect_email():
    # Create OAuth flow instance
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    flow.redirect_uri = url_for('oauth_callback', _external=True)
    
    # Get the authorization URL
    auth_url, _ = flow.authorization_url(prompt='consent')
    return redirect(auth_url)

def get_credentials():
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token_file:
            credentials = pickle.load(token_file)
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            return credentials
    else:
        return None

from googleapiclient.discovery import build

'''
@app.route('/send_email', methods=['POST'])
def send_email():
    credentials = get_credentials()
    if not credentials:
        return "No valid credentials found. Please connect your email first.", 400

    service = build('gmail', 'v1', credentials=credentials)

    # Replace with your email content
    message = {
        'raw': 'encoded_message_base64_here'
    }

    try:
        sent_message = service.users().messages().send(userId='me', body=message).execute()
        return f"Email sent successfully: {sent_message['id']}"
    except Exception as e:
        return f"An error occurred: {e}", 500
'''


@app.route('/oauth_callback', methods=['GET'])
def oauth_callback():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    flow.redirect_uri = url_for('oauth_callback', _external=True)
    
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    
     # Save credentials
    credentials = flow.credentials
    save_credentials(credentials)  # Replace with your logic for saving credentials

    #return "Email API connected successfully! You can now send emails."
    return redirect('/#email-configuration')
if __name__ == '__main__':
    # Run the Flask app in debug mode for development
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, ssl_context=(
        '/home/rony_gabbai/ssl/fullchain.pem',
        '/home/rony_gabbai/ssl/privkey.pem'
    ))
