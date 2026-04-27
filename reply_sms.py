from dotenv import load_dotenv
import os

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from google.adk.apps.app import App

from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse

load_dotenv() # Probably not needed, I'm tired

app_name = "my_agent"
session_service = InMemorySessionService()

app = Flask(__name__)

from my_agent import root_agent
# ADK app points to the root_agent to process the user's input.
adk_app = App(name=app_name, root_agent=root_agent)

@app.route("/reply_sms", methods=['POST'])
async def reply_sms():
    # Takes the user's input text.
    incoming_msg = request.values.get('Body', '')
    # Gets the user's phone number as the user_id and removes the '+' character at the start of the number.
    user_id = request.values.get('From', 'default_user').replace('+', '')
    # A runner is required to process the conversation with the ADK app.
    runner = Runner(
        app=adk_app,
        session_service=session_service
    )
    # New reply_text variable.
    reply_text = ""
    try:
        # If a session does not already exist, create one.
        session = await session_service.get_session(
            app_name=app_name, 
            user_id=user_id, 
            session_id=user_id
        )
        if session is None:
            await session_service.create_session(
                app_name=app_name, 
                user_id=user_id, 
                session_id=user_id
            )
        # Packages the incoming message as a Content object for the AI to understand, with a user role.
        new_msg = Content(parts=[Part(text=incoming_msg)], role="user")
        # Runs the entire AI process, including agent function calls.
        async for event in runner.run_async(
            user_id=user_id,
            session_id=user_id,
            new_message=new_msg
        ):
            print(f"Event received: {event}")
            # Extracts only the final response from the agent to send back to the user.
            if event.is_final_response():
                # The final response is the first part of the content of the final response.
                reply_text = event.content.parts[0].text 
    # If any errors occur, the reply text will be the error message.      
    except Exception as e:
        reply_text = f"Runner Error: {str(e)}"

    # Create a new Twilio MessagingResponse.
    resp = MessagingResponse()
    resp.message(reply_text)
    # Return the TwiML (as XML) response.
    return Response(str(resp), mimetype='text/xml')

if __name__ == "__main__":
    app.run(port=3000)