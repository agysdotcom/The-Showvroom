from flask import Flask, request, jsonify
from fpdf import FPDF
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Vehicle Sale Submission - The Showvroom', 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, label, 0, 1, 'L')
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

@app.route('/submit-car', methods=['POST'])
def submit_car():
    data = request.form.to_dict()

    pdf = PDF()
    pdf.add_page()

    pdf.chapter_title('Vehicle Type')
    pdf.chapter_body(f"Type: {data.get('vehicle_type', 'N/A')}")

    pdf.chapter_title('Vehicle Details')
    details_keys = ['make', 'model', 'year', 'variant', 'mileage', 'price', 'transmission', 'fuel',
                    'engine_size', 'color', 'condition', 'reg_number', 'vin', 'location', 'features', 'notes']
    body = ''
    for key in details_keys:
        body += f"{key.capitalize().replace('_', ' ')}: {data.get(key, 'N/A')}\n"
    pdf.chapter_body(body)

    pdf.chapter_title('Seller Details')
    seller_keys = ['seller_name', 'phone', 'email', 'city', 'contact_notes']
    body = ''
    for key in seller_keys:
        body += f"{key.capitalize().replace('_', ' ')}: {data.get(key, 'N/A')}\n"
    pdf.chapter_body(body)

    pdf_bytes = pdf.output(dest='S').encode('latin1')

    try:
        msg = EmailMessage()
        msg['Subject'] = 'New Vehicle Sale Submission'
        msg['From'] = 'your_email@example.com'
        msg['To'] = 'your_sales_email@example.com'
        msg.set_content('A new vehicle sale submission was received. See attached PDF.')
        msg.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename='vehicle_submission.pdf')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('your_email@example.com', 'your_app_password')
            smtp.send_message(msg)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

    return jsonify({'status': 'success', 'message': 'Form received and emailed.'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
