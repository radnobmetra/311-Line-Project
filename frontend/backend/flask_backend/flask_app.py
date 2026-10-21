
#import os
from flask import Flask, request, make_response
#from markupsafe import escape
from flask_cors import CORS
#import json
import asyncio
import os
from werkzeug.utils import secure_filename  
from pathlib import Path

from .remote_chat_dashboard import (
    gui_make_session,
    send_message_get_response,
    send_image_get_response
)

def create_app():   
    app = Flask(__name__)
    CORS(app)

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    FLASK_FOLDER = Path(__file__).resolve().parent
    UPLOAD_FOLDER = FLASK_FOLDER / "temp"
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    error_msg = {"author": "error", "contents": "An error occurred. Please try again later."}

    def allowed_file(filename):
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def valid_user_number(user_number: str):
        #checks if user number is valid. For now, just checks that the user number 
        # contains at least 2 characters
        return len(user_number) >= 2



    @app.route("/hello")
    def hello():
        return "hello world"

    

    @app.route("/sendMessage", methods=["POST"])
    def sendMessage():
        userNumber = str(request.json.get("userNumber"))
        userMessage = str(request.json.get("message"))
        if not (userNumber and userMessage):
            return(error_msg)
        responseJson = asyncio.run(send_message_get_response(userNumber, userMessage))
        return responseJson



    @app.route("/sendImage", methods=["POST"])
    def sendImage():
        #return error message for requests without a user id
        if 'userNumber' not in request.form:
            return(error_msg)

        #get user number
        user_number = request.form['userNumber']
        if valid_user_number(user_number) is False:
            return(error_msg)

        #get file
        if 'userUpload' not in request.files:
            return (error_msg)
        file = request.files['userUpload']
        if file.filename == '':
            return(error_msg)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            #send image to agent
            responseJson = asyncio.run(send_image_get_response(filepath, user_number))
            return(responseJson)

        return(error_msg)

    return app