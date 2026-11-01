from .remote_chat_dashboard import (
    send_message_get_response,
    send_image_get_response,
)

import asyncio
from pathlib import Path
import json
import os
from shutil import copyfile

user_number = "remote-chat-test"
filename = "pothole.JPG"
message = "I would like to report a pothole on State University Drive in Sacramento. The nearest address is 6000 Jed Smith Dr, Sacramento, CA 95819."

FLASK_FOLDER = Path(__file__).resolve().parent
UPLOAD_FOLDER = FLASK_FOLDER / "temp"


def testRemoteChat():

    print("\n=====================\nTesting remote chat\n=====================\n")

    filepath = os.path.join(FLASK_FOLDER, filename)
    tempFilePath = os.path.join(UPLOAD_FOLDER, filename)

    print ("Test image will be temporarily copied to this filepath: " + tempFilePath)
    
    #send a text message
    responseJson = asyncio.run(send_message_get_response(user_number, message))
    assert responseJson["author"] == "Agent", "send_message_get_response didn't return an agent response."

    #send an image message
    #because send_image_get_response automatically deletes user-submitted images once they are
    #sent to the agent, a temporary copy of the test file must be made.
    try:
        tempFilePath = copyfile(filepath, tempFilePath)
    except:
        print("Error: test file couldn't be copied to temp directory.")
        return

    responseJson = asyncio.run(send_image_get_response(tempFilePath, user_number))
    assert responseJson["author"] == "Agent", "send_image_get_response didn't return an agent response."

    print()
    print("Tests passed.")

# for running script with details, run 'py -m flask_backend.remote_chat_test'
#from frontend/backend
if __name__ == "__main__":
    testRemoteChat()