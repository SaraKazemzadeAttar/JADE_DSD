import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def generate_random_code():
    random_number = random.randint(1000, 9999)
    strnum = str(random_number)
    return strnum

def send_code(email):
    msg = MIMEMultipart()
    msg['From'] = "shahedap.footballfantasy@gmail.com"
    msg['To'] =email
    msg['Subject'] = "Validification"
    
    otp_code = generate_random_code()
    body = f"Hey! Here is your verification code: {otp_code}"
    msg.attach(MIMEText(body, 'plain'))
    
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "shahedap.footballfantasy@gmail.com"
    smtp_password = "vfecuirpkbwojjkj"
    
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    text = msg.as_string()
    server.sendmail(smtp_username,email, text)
    server.quit()
    
    return otp_code


