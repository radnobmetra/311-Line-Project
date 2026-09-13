# 311-Line-Project / Team Rollback Netcode CSC-190/191 Senior Project

# Overview
What is contained in this repository?

This repository is Team Rollback Netcode's Repository for our Senior Project. It is a 311 Text Line for the City of Sacramento designed to help users with longer responses times due to needing to call back with the information requested.


# Project Breakdown
Our project focuses on shortening response time for users when they ask the City of Sacramento's 311 Department questions. Often when callers have a question, they have to deal with long wait times for reasons like staff shortages and the information not being immediately available. By utilizing Gemini with Twilio residents can text the SMS line and get information about a ticket as well as general questions and answers. 

## AI Agents
Currently there are multiple agents that each handle their own responsibities and link together as follows.


### Overseer / Receptionist Agent
This agent acts as the main orchestrator and coordinates whether or not a request is valid. It also handles greeting the user by using the greeting agent tool. It runs multiple security functions to avoid spam issues such as spamming numbers or other characters.

### Ticket Lookup Agent
This agent finds the reference ticket number in the user's message. If there are multiple valid tickets inside the message then it will ask which one you want. It then uses a lookup tool to get information from the City's ArcGIS Database that is publicly available information.

### Q&A Agent 
This agent answers questions and can handle most requests. It will link into a RAG pipeline based on ElasticSearch. This allows it to have accurate and valid information. Currently it links into the __Information Lookup Agent__. Once we have integrated the City's ElasticSearch tool it will link to that to provide fast, accurate and up to date results for residents. This agent also utilizes feedback loops so if it's unsure of its answer it will either fix the answer or provide a tag asking if it helps answer the question. 
 
### Information Lookup Agent
This agent handles lookup from a .txt document. This agent acts as our temporary endpoint tester. This will be replaced by ElasticSearch once that is developed and linked into the system. By using this it allows us to simulate getting information from an external source.



## External APIs:

### Sacramento 311 ArcGIS
The City of Sacramento holds a public ArcGIS endpoint that allows people to see noted requests. This is linked into our system so you can see the status of a ticket via a simple text.

### Elastic Search
By using the City's internal ElasticSearch we are able to grab the relevant information to a residents query and respond accurately minimizing halluciations.


**Prototypes & Mockups**
Here is our mockup / prototype documents from Figma.

<img width="1094" height="581" alt="image" src="https://github.com/user-attachments/assets/7e2d2c67-c6c4-42e2-802a-3af084672ca3" />
<img width="1309" height="614" alt="image" src="https://github.com/user-attachments/assets/6951642b-6ddc-422b-94c0-3cf1f609404c" />
<img width="1062" height="643" alt="image" src="https://github.com/user-attachments/assets/c7a33455-5ff7-4d26-bdbc-ddead3a7eb30" />


**ERD Diagram**

Here is our ERD for storing users sessions. We will be storing the session, time start, time end, outcome of the session (i.e are the agent helping people out or getting stuck or having some sort of error). 

<img width="1280" height="720" alt="image" src="https://github.com/user-attachments/assets/a90bcaf5-ed06-413c-8237-55d5f770abcf" />


## Planned Features / Key Milestones
   ### - Admin Dashboard  
    
This will be a built in reporting site that allows for generating of graphs based on preset information. By having this it allows for easier access to configure specific settings as well as what types of requests are occuring, usage rates and session outcomes. This will be developed using AngularJS and link into our session database.


   ### - SalesForce Integrated Agents 

This will be a series of agents that integrate into city services to allow for reporting on specific common issues that residents might have. Currently planned ones are the Pothole Reporting Agent and the Parking Meter Agent. Each of these will take images as inputs as well as additional information and create a ticket for the 311 to handle. 

 ### Elastic Search Integration
 This will be integrated into our Q&A Agent replacing our Lookup agent allowing for more reliable and up to date information. 



## Testing

To Be Completed

## Deployment|

To Be Completed

## Developer Instructions /

To Be Completed

    Installation Guide:
https://docs.cloud.google.com/agent-builder/agent-engine/quickstart-adk
Before running this command: 'gcloud auth application-default login', you will most likely have to install Google Cloud CLI. Follow this guide to install it:
https://docs.cloud.google.com/sdk/docs/install-sdk#windows
After installing all the necessary dependencies, you're good to go. 
