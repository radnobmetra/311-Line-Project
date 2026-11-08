
This folder contains the backend for the admin dashboard's agent chat page.

dependencies
==============
Before running the flask app, you will need to install flask and flask-cors:   
    pip install flask
    pip install flask-cors

Also, make sure that your env file is updated and has the REASONING_ENGINE_APP_NAME field.

how to run
============
To run the flask app, run this command in 311-line-project/frontend/backend:
    flask --app flask_backend.flask_app run --debug

After starting the flask app, you should be able to talk to the agent using the
agent chat page on the admin dashboard.

how to test
=============
Run this command in 311-line-project/frontend/backend:
    'py -m flask_backend.remote_chat_test'

Or, run this command in 311-line-project/frontend/backend:
    'py -m backend_test' 

Or, run pytest from 311-line-project/frontend/backend:
    'python -m pytest'

folders
========
temp/
    Used to temporarily store user-submitted images, which are automatically deleted from
    the folder after the user's message is sent to the agent.

files
=======
__init__.py

flask_app.py
    The code for the flask app. The endpoint "/sendMessage" gets the user's message
    from the POST request and returns a JSON with the agent's response or an error message.
    The angular app expects a JSON file in the following format:
    {author: "(Error, agent, etc)", contents: "(contents of message)"}

remote_chat_dashboard.py
    Modified copy of 311-Line-Project/remote_chat.py.
    The flask app uses the send_message_get_response function to send a message to
    the agent and return a response.

session_handling, evaluation_handling, user_feedback_handling
    Dependencies of remote_chat_dashboard.

remote_chat_test.py
    Tests if remote_chat_dashboard functions successfully return an agent response 
    to a message. If a session has already been started, it will be reused.

pothole.JPG
    used by test module to test image handling.
