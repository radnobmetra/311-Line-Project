

#runs remote_chat_test.testRemoteChat(), which can't be run from the flask_backend folder
#because of the project structure

from flask_backend.remote_chat_test import testRemoteChat

if __name__ == "__main__":
    testRemoteChat()