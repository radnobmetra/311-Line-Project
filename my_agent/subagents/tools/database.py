import os
import random

db = "sessions.log"

def data_file():
    if not os.path.exists(db):
        with open(db, "w") as file:
            file.write("--- Session Transcript ---\n")
        
def conversation_record(chat_transcript: str):
    """
    Logs the entire conversation history to the database once the session is done.
    
    Args:
        chat_transcript: The full text of the interaction between the user and the agents.
    """
    data_file()    
    with open(db, "a") as file:
       # file.write(f"\n[Session ID: {conv_id}]\n")
       # ill prob implement this later brah idk session.db is mad confusing rn
        file.write(f"Transcript:\n{chat_transcript}\n")
        file.write("-" * 100 + "\n")


# --------------- ALSO SAVING THIS FOR LATER !! INGORE !! ---------------
# import os
# db = "sessions.log"

# def data_file():
#     if not os.path.exists(db):
#         with open(db, "w") as file:
#             file.write("")
        
# def conversation_record(conv_id: str, phone: str, start_time: str, end_time: str, text: str, result: str):
#     """
#     Logs the end of a conversation to the database.
    
#     Args:
#         conv_id: The unique ID of the chat (generate a random 4-digit number if unknown).
#         phone: The user's phone number (use 'Unknown' if not provided).
#         start_time: When the chat started (e.g., '10:00 AM').
#         end_time: When the chat ended (e.g., '10:05 AM').
#         text: A short summary of the conversation.
#         result: The final outcome (e.g., 'Resolved' or 'Ticket Created').
#     """
#     data_file()
#     with open(db, "a") as file:
#         file.write(f"ID:{conv_id}\n")
#         file.write(f"Phone:{phone}\n")
#         file.write(f"Start Time:{start_time}\n")
#         file.write(f"End Time:{end_time}\n")
#         file.write(f"Text:{text}\n")
#         file.write(f"Result:{result}\n")