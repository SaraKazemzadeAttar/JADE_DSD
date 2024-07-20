import random
import smtplib

OTP = random.randint(100000,999999)      #generating a randomm 6-digit OTP

#setting up server
server = smtplib.SMTP('smtp.gmail.com',587)
#server = smtplib.SMTP('64.233.184.108',587)           #IP address of smtp.gmail.com to bypass DNS resolution
server.starttls()

name = input("enter your name:")
global receiver_email
receiver_email = input("enter ur email id:")


password = "stqqwjqoocucknsx"
server.login("priyanshu25122002@gmail.com",password)

body = "dear"+name+","+"\n"+"\n"+"your OTP is "+str(OTP)+"."
subject = "OTP verification using python"
message = f'subject:{subject}\n\n{body}'

server.sendmail("priyanshu25122002@gmail.com",receiver_email,message)

def sending_otp(receiver_email):
    new_otp = random.randint(100000,999999)

    body = "dear"+name+","+"\n"+"\n"+"your OTP is "+str(new_otp)+"."
    subject = "OTP verification using python" 
    message = f'subject:{subject}\n\n{body}'
    server.sendmail("priyanshu25122002@gmail.com",receiver_email,message)
    print("OTP has been sent to"+receiver_email)
    received_OTP = int(input("enter OTP:"))

    if received_OTP==new_otp:
        print("OTP verified")
    else:
        print("invalid OTP")
        print("resending OTP.....")
        sending_otp(receiver_email)
    
print("OTP has been sent to "+receiver_email)
received_OTP = int(input("enter OTP:"))

if received_OTP==OTP:
    print("OTP verified")
else:
    print("invalid OTP")
    answer = input("enter yes to resend OTP on same email and no to enter a new email id:")
    YES = ['YES','yes','Yes']
    NO = ['NO','no','No']
    if answer in YES:
        sending_otp(receiver_email)
    elif answer in NO:
        new_receiver_email = input("enter new email id:")
        sending_otp(new_receiver_email)
    else:
        print("invalid input")

server.quit()