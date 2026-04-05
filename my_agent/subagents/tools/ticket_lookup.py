import json

def get_ticket_status(ticketNum:str) -> str:
    
    ticketStatus = 'no ticket found'

    #load ticket objects 
    with open('tickets.json') as f:
        tickets = json.load(f)

    #try to find ticket with given ticket number. If ticket is found, return its status.
    #if ticket with correct ticket number isn't found, return 'no ticket found'

    for ticket in tickets['tickets']:
        if ticket['Ticket number'] == ticketNum:
            ticketStatus = ticket['Status']
            break

    f.close() 

    return(ticketStatus)