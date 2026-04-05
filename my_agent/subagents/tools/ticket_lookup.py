import json

#kyra and jimson
def get_ticket_status(ticketNum:str) -> str:

    #load ticket objects 
    with open('tickets.json', "r") as f:
        tickets = json.load(f)

    #try to find ticket with given ticket number. If ticket is found, return its chunk/ticket.

    for ticket in tickets['tickets']:
        if ticket['Ticket number'] == ticketNum:
            return ticket

    f.close() 

 #if ticket with correct ticket number isn't found, return 'no ticket found'
    return 'no ticket found'