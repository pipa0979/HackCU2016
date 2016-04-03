import aiml
import os
import requests,json
import smtplib
from twilio.rest import TwilioRestClient
import wikipedia
import Tweets_cassandra
from PyDictionary import PyDictionary
import gmail

def check_inbox(user, pwd) : 
    g = gmail.login(user, pwd)
    emails  = g.inbox().mail()
    mails = []
    for email in emails : 
        email.fetch()
        mails.append(email)
    return mails
    


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
dictionary=PyDictionary()


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

    elif message.strip().split()[0].lower() == 'weather'  : 
        url = 'http://api.openweathermap.org/data/2.5/weather?q=' + message.strip().split()[1].lower()  + ',USA&appid=83364ebafb88eff14f89615a7067812f' 
        bot_response = (requests.get(url).json())        
        ans ="The forcast for today's weather is "
        weather_desc = bot_response['weather'][0]['description']

        temp = ((float(bot_response['main']['temp']) - 273.15) * 9.0/5.0 )  + 32.0
        bot_response = ans+ weather_desc +" with a temperature of "+str(temp)+" farenheit."
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

    elif message.lower() == 'inbox' : 
        kernel.setBotPredicate("email",'pipa09799@gmail.com')
        kernel.setBotPredicate("pwd",'hackcu123')
        bot_response = check_inbox(kernel.getBotPredicate("email"),kernel.getBotPredicate("pwd"))
        #print bot_response     




    #News       
    elif message.lower() == 'news' :
        url = 'http://content.guardianapis.com/search?api-key=test'
        bot_response = (requests.get(url).json())
        print type(bot_response),bot_response['response']['results']
        
        try:
            ans =" "
            bot_response = bot_response['response']["results"]
            for each in bot_response:
                ans += each["webTitle"]+"\n"+each["webUrl"]+"\n\n"
            bot_response = ans
        except:
            print  "Cannot fetch news"
        print bot_response
        






    elif message.strip().lower().split()[0] == "wiki":
        bot_response = wikipedia.summary("Wikipedia",sentences=2)
        print bot_response
    elif message.strip().split()[0] == "tweet":
        flag = None
        tw = Tweets_cassandra.TweetAPI()
        try:
            flag = 0
            tw.postTweet(" ".join(message.strip().split()[1:]))
        except:
            flag = 1
        if (flag == 0 ):
            print "Tweet successful"
        else:
            print "Tweet Failed"

    elif " ".join(message.strip().lower().split()[:2]) == "synonym of":
        bot_response =  dictionary.synonym(" ".join(message.strip().lower().split()[2:]))
        if(len(bot_response) >= 1 ):
            bot_response = ", ".join(bot_response)
        else:
            bot_response = "Sorry i couldn't find the synonym for "," ".join(bot_response)
        print bot_response

    elif " ".join(message.strip().lower().split()[:2]) == "antonym of":        
        bot_response =  (dictionary.antonym(" ".join(message.strip().lower().split()[2:])))
        if(len(bot_response) >= 1 ):
            bot_response = ", ".join(bot_response)
        else:
            bot_response = "Sorry i couldn't find the antonym for "," ".join(bot_response)
        print bot_response


    elif " ".join(message.strip().lower().split()[:2]) == "meaning of":
        bot_response =  dictionary.meaning(" ".join(message.strip().lower().split()[2:]))
        if len (bot_response.keys()) == 0  :
            bot_response = "Sorry, Couldn't find the meaning "
        else:
            if 'Noun' in bot_response.keys():
                print bot_response['Noun'][0]
            else:
                print "Not found"
            




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