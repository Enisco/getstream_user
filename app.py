from flask import Flask, render_template, request, jsonify
import datetime
import stream

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, Flask!"

@app.route("/get_token/<string:userId>", methods=['GET'])
def get_user_token(userId):
    client = stream.connect('mgeuu28wmz7g', 'wdt5u4pbdbpjnywfphzmvshzbpz5g3qdmsxz5bh22pehzztvymyrn64pgtgzgp44')
    user_token = client.create_user_token("enisco2")
    print ("User Token generated for " +  userId + ": " + user_token) 

    response = {
        'id': userId,
        'token': user_token
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run()
