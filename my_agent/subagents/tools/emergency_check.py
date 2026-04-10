import json

def emergency_check(user_msg:str) -> str:

    with open('emergency_cases.json','r') as f:
            txt = json.load(f)
            keywords = txt.get('emergency_key',[])
        
    msg_lower=user_msg.lower()

    for word in keywords:
          if word.lower() in msg_lower:
                return "Emergency Alert"
          else:
                return "Valid"