
from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    answer = None
    if request.method == 'POST':
        if request.form['question'] == 'what is your name':
        	print "Question is - ", request.form['question']

        	# CODE HERE for bot
        	# Set the answer variable 

        	answer = 'Hardcoded answer to the question: '+ request.form['question']           
        else:
        	print "NO FUCKING RESPONSE"
        	return render_template('OfficeBotHome.html', answer=answer)

    return render_template('OfficeBotHome.html', answer=answer)

      
if __name__ == '__main__':
	app.debug = True
	app.run()