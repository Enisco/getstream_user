
import time
from flask import Flask, render_template, request, jsonify
import stream
from flask_cors import CORS
# from app import app

from getstream import Stream
from getstream.models import CallRequest, CallSettingsRequest
from getstream.models import RecordSettingsRequest
from getstream.models import UserRequest

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Hello, from GospelTube!"

@app.route("/get_token/<string:userId>", methods=['GET'])
def get_user_token(userId):
    try:
        client = stream.connect('mgeuu28wmz7g', 'wdt5u4pbdbpjnywfphzmvshzbpz5g3qdmsxz5bh22pehzztvymyrn64pgtgzgp44')
        user_token = client.create_user_token(userId)
        print ("User Token generated for " +  userId + ": " + user_token) 

        response = {
            'id': userId,
            'token': user_token
        }
        return jsonify(response)
    except Exception as error:
        errorResponse = {
            'status': False,
            'error': str(error)
        }
        return jsonify(errorResponse)


# -----------------------Create Call and Go Live--------------------------

@app.route("/create_livestream/<string:userId>/<string:callId>", methods=['GET'])
def create_livestream(userId, callId):
    try:
        client = Stream(api_key="mgeuu28wmz7g", api_secret="wdt5u4pbdbpjnywfphzmvshzbpz5g3qdmsxz5bh22pehzztvymyrn64pgtgzgp44")

        externalStorageList = client.list_external_storage()
        print("\nexternalStorageList: ", externalStorageList.data)

        updateCallTypeResponse = client.video.update_call_type(
            name="default",
            external_storage="gtubelive_s3bucket",
        )
        print("\nUpdateCallTypeResponse: ", updateCallTypeResponse.data) 

        call = client.video.call(
            call_type = "default",
            id=callId
        )
        
    except Exception as error:
        errorResponse = {
            'status': False,
            'error': str(error)
        }
        print("\n\nError initiating call: ", str(error))
        return jsonify(errorResponse)

    try:
        createCallResponse = call.get_or_create(
                data= CallRequest(
                    created_by=UserRequest(
                        id=userId,
                        name="GtubeUser" + userId,
                        role="gtubeadmin",
                    ),
                    settings_override=CallSettingsRequest(
                        recording= RecordSettingsRequest(
                            mode="available",
                            quality="1080p",
                            audio_only=False,
                        ),
                    ),
                ),
            )
        print("\n\n createCallResponse: ", createCallResponse.data) 
    
    except Exception as error:
        errorResponse = {
            'status': False,
            'error': str(error)
        }
        print("\nError creating call: ", str(error))
        return jsonify(errorResponse)

    try:
        goLiveRes = client.video.go_live(
            id=callId,
            type="default",
            recording_storage_name="gtubelive_s3bucket",
        )
        print("\nGo Live Result: ", goLiveRes.data)

        response = {
            'status': True,
            'call_id': createCallResponse.data.call.id,
            "rtmp": createCallResponse.data.call.ingress.rtmp.address
        }
        return jsonify(response)
    
    except Exception as error:
        errorResponse = {
            'status': False,
            'error': str(error)
        }
        print("\n\nError going live call: ", error)
        return jsonify(errorResponse)


# -------------------------Start Recording-------------------------------------------

@app.route("/start_recording/<string:callId>", methods=['GET'])
def start_recording(callId):
    try:
        clientRec = Stream(api_key="mgeuu28wmz7g", api_secret="wdt5u4pbdbpjnywfphzmvshzbpz5g3qdmsxz5bh22pehzztvymyrn64pgtgzgp44")
        # time.sleep(5)
        startRecording = clientRec.video.start_recording(
            id=callId,
            type="default",
            recording_external_storage="gtubelive_s3bucket",
        )
        print("\nStart Recording Result: ", startRecording.data)

        response = {
            'status': True
        }
        return jsonify(response)

    except Exception as error:
        errorResponse = {
            'status': False,
            'error': str(error)
        }
        return jsonify(errorResponse)

# -------------------------Stop Livestream and Get Recording-------------------------------------------

@app.route("/get_recording/<string:callId>", methods=['GET'])
def get_recording(callId):
    try:
        client = Stream(api_key="mgeuu28wmz7g", api_secret="wdt5u4pbdbpjnywfphzmvshzbpz5g3qdmsxz5bh22pehzztvymyrn64pgtgzgp44")
        call = client.video.call(
            call_type = "default",
            id=callId
        )
        
        end = call.end()
        print("End Call Data: ", end.data)
        # time.sleep(30)

        list_recordings = call.list_recordings()
        print("\n\nlist_recordings Data after CallEnd: ", list_recordings.data)
        recording_url = "https://gospeltube533267336299.s3.us-east-2.amazonaws.com/gtube_liverecordings_s3bucket/default_" + callId + "/" + list_recordings.data.recordings[0].filename
        print("\n\n ------ Recordings URL: ", recording_url)

        response = {
            'status': True,
            'recording_url': recording_url
        }
        return jsonify(response)

    except Exception as error:
        errorResponse = {
            'status': False,
            'error': str(error)
        }
        return jsonify(errorResponse)


# ---------------------------Error Handlers------------------------------------

@app.errorhandler(404)
def not_found_error(error):
    response = {
        'status': False,
        'error': 'Not Found'
    }
    return jsonify(response), 404

@app.errorhandler(Exception)
def handle_exception(error):
    # Handle all exceptions
    response = {
        'status': False,
        'error': str(error)
    }
    return jsonify(response), 500


if __name__ == '__main__':
    app.run(debug=True)
