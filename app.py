from flask import Flask, request, jsonify
import os
import sys
from dotenv import load_dotenv
from flask_cors import CORS
import subprocess
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok = True)

def send_email(receiver_email, attachment_path):
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT"))
    username = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")

    msg = EmailMessage()
    msg["Subject"] = "TOPSIS Result"
    msg["From"] = "topsis@app.local"
    msg["To"] = receiver_email
    msg.set_content("Please find attached TOPSIS output file.")

    with open(attachment_path, "rb") as f:
        file_data = f.read()
    msg.add_attachment(
        file_data,
        maintype = "application",
        subtype = "octet-stream",
        filename = "output.csv"
    )

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(username, password)
        server.send_message(msg)

@app.route("/upload", methods = ["POST"])
def upload():
    try:
        file = request.files["dataset"]
        weights = request.form["weights"]
        impacts = request.form["impacts"]
        email = request.form["email"]
        print("✅ Received data:")
        print("File:", file.filename)
        print("Weights:", weights)
        print("Impacts:", impacts)
        print("Email:", email)

        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        output_path = os.path.join(UPLOAD_FOLDER, "output.csv")
        file.save(input_path)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        TOPSIS_PATH = os.path.join(BASE_DIR, "Topsis", "topsis.py")

        cmd = [
            sys.executable,
            TOPSIS_PATH,
            input_path,
            weights,
            impacts,
            output_path
        ]
        result = subprocess.run(cmd, capture_output = True, text = True)
        print("TOPSIS STDOUT:\n", result.stdout)
        print("TOPSIS STDERR:\n", result.stderr)

        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 400

        send_email(email, output_path)
        return jsonify({"message": "Report generated and emailed successfully!"})

    except Exception as e:
        print("SERVER ERROR:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug = True)