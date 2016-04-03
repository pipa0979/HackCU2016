from flask import Flask
import bot
app = Flask(__name__)

'''
@app.route("/hello")
def hello():	
    return "Hello World!!"
'''
@app.route("/hello")
def hello():
	a= bot.web_input("heyyy")
	return a



if __name__ == "__main__":
    app.run()


