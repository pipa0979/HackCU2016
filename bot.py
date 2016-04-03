import aiml
import os
import requests,json
import smtplib
from twilio.rest import TwilioRestClient

def send_email(user, pwd, recipient, subject, body):
    print user, pwd, recipient, subject, body
    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body
    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
    except:
        return 0
    return 1

def call(number,ACCOUNT_SID,AUTH_TOKEN) :
     try :
        client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
        call = client.calls.create(
         to=number,
         from_="+xxxxxxxxxxxxx",
         url="http://demo.twilio.com/welcome/voice/",
         method="GET",         
         fallback_method="GET",
         status_callback_method="GET",
         record="false"
        )
        return 1
     except :
        return 0

def text(number,msg,ACCOUNT_SID,AUTH_TOKEN) :
     try :
        client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
        client.messages.create(
         to=number,
         from_="+xxxxxxxxxxxxx",
         body = msg,
        )
        return 1
     except :
        return 0

kernel = aiml.Kernel()

if os.path.isfile("bot_brain.brn"):
    kernel.bootstrap(brainFile = "bot_brain.brn")
else:
    kernel.bootstrap(learnFiles = "std-startup.xml", commands = "load aiml b")
    kernel.saveBrain("bot_brain.brn")

# kernel now ready for use


while True:
    message = raw_input("Enter your message to the bot: ")
    if message == "quit":
        exit()
    elif message == "save":
        kernel.saveBrain("bot_brain.brn")

    #Weather
    elif message.lower() == 'weather'  :
        if kernel.getBotPredicate("location") == '' :
                location = raw_input('I need your location ... : ')
                kernel.setBotPredicate("location",location)
        url = 'http://api.openweathermap.org/data/2.5/weather?q=' + kernel.getBotPredicate("location")  + ',USA&appid=xxxxxxxxxxxxxxxx'
        bot_response = str(requests.get(url).json())
        if bot_response == '' :
                kernel.setBotPredicate("location",'')
        print bot_response


    #Email
    elif message.strip().split()[0].lower() == 'email' :
        kernel.setBotPredicate("email",'xxxxxxxxxx@gmail.com')
        kernel.setBotPredicate("pwd",'xxxxxxxxxx')
        receiver = message.strip().split()[1].lower()
        subject = raw_input('SUBJECT\n')
        body = raw_input('BODY\n' )
        bot_response = send_email(kernel.getBotPredicate("email"),kernel.getBotPredicate("pwd"), receiver, subject , body)
        #print bot_response

    #News       
    elif message.lower() == 'news' :
        url = 'http://content.guardianapis.com/search?api-key=test'
        bot_response = str(requests.get(url).json())
        print bot_response
        
    #tasks
    elif message.strip().split()[0].lower() == 'tasks' :
        bot_response = ''
        if len(message.strip().split()) == 1 :
                bot_response = kernel.getBotPredicate("tasks").split('#')
        elif message.strip().split()[1].lower() == 'add' :
                kernel.setBotPredicate("tasks",kernel.getBotPredicate("tasks") + '#' + raw_input('Task\n'))
                bot_response = kernel.getBotPredicate("tasks").split('#')
        elif message.strip().split()[1].lower() == 'clean' :
                kernel.setBotPredicate('tasks' , '')
                bot_response = kernel.getBotPredicate("tasks").split('#')
        #print bot_response

    elif message.strip().split()[0].lower() == 'call':
        bot_response = ''
        if len(message.strip().split()) == 1 :
                number = raw_input('Number : ')
        bot_response = call(number,"xxxxxxxxxxxxxxxxxxxxxxxx","xxxxxxxxxxxxxxxxxxxxxxxx")
        #print bot_response

    elif message.strip().split()[0].lower() == 'text':
        bot_response = ''
        if len(message.strip().split()) == 1 :
                number = raw_input('Number : ')
        body = raw_input('Body : ')
        bot_response = text(number, body, "xxxxxxxxxxxxxxxxxxxxx","xxxxxxxxxxxxxxxxxxxxxx")
        print bot_response

    #AIML       
    else:
        bot_response = kernel.respond(message)
        print bot_response
        # Do something with bot_response

