
#import os
from flask import Flask, request, make_response
#from markupsafe import escape
from flask_cors import CORS
#import json
import asyncio

from .remote_chat_dashboard import (
    gui_make_session,
    send_message_get_response,
)

def create_app():   
    app = Flask(__name__)
    CORS(app)

    
    @app.route("/hello")
    def hello():
        return "hello world"
    
    """
    @app.route("/makeSession", methods=['GET'])
    def makeSession():
        #create or reuse a session, then return the session ID to the user.
        #use the function gui_make_session() to get a session ID.
        #return gui_make_session()
        return "1234"
    """

    @app.route("/sendMessage", methods=["POST"])
    def sendMessage():
        userMessage = str(request.json.get("message"))
        responseJson = asyncio.run(send_message_get_response(userMessage))
        return responseJson


    return app