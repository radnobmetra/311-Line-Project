# 311-Line-Project / Team Rollback Netcode CSC-190/191 Senior Project

## Overview
What is this humble repository?

This repository is Team Rollback Netcode's Repository for our Senior Project. It is a 311 Text Line for the City of Sacramento designed to help users with longer responses times due to needing to call back with the information requested.


## Project Breakdown
Current there are multiple agents that each handle their own responsibities are are as follows.

**Overseer / Receptionist Agent**
    This agent acts as the main orchestrator and coordinates whether or not a request is valid. It also handles greeting the user by using the greeting agent tool.
It runs multiple security functions to avoid spam issues such as spamming numbers or other characters.

**Ticket Lookup Agent**
    This agent finds the reference ticket number in the users message. If there is multiple valid tickets inside the message then it will ask which one you want. It then will use a lookup to get information from the city itself.

**Q&A Agent** 
    This agent answers questions and can handle most requests. It will link into an RAG pipeline based on ElasticSearch. This allows it to have accurate and valid information. Currently it links into the Information Lookup Agent
 
**Information Lookup Agent**
    This agent handles lookup from a .txt document. This is an agent that is a temporrary standin for the RAG which will be developed later.



**External APIs:**

This project integrates in with the City of Sacramento's Elastic Search tool as well as their 

Installation Guide:
https://docs.cloud.google.com/agent-builder/agent-engine/quickstart-adk
Before running this command: 'gcloud auth application-default login', you will most likely have to install Google Cloud CLI. Follow this guide to install it:
https://docs.cloud.google.com/sdk/docs/install-sdk#windows
After installing all the necessary dependencies, you're good to go. 


**Mockups**

Mockups to go here



**ERD Diagram**

Here is our ERD for the project. It's relatively simple as we are mostly storing just individual sessions.

<img src="https://cdn.discordapp.com/attachments/1449536158848651476/1497410368727679046/MAIN_CSC190_Senior_Project_Presentation.png?ex=69ed6b94&is=69ec1a14&hm=cc1b05e9e7aaac345125b3819055b8a297e610cdeaae73b33096d694a798c8eb&" width="560">






## Testing

    To Be Completed

## Deployment|

    To Be Completed

## Developer Instructions

    To Be Completed




## Planned Features / Key Milestones
   ### - Admin Dashboard  
    
        This will be a built in reporting site that allows for generating of graphs based on preset information. By having this it allows for easier management of what types of requests are occuring as well as usage rates and success rates of helping users. This will be using an AngularJS framework.

   ### - SalesForce Agents 

        This will be a series of agents that integrate into city services to allow for reporting on specific common issues. Currently planned ones are the Pothole Reporting Agent and the Parking Meter Agent. Each of these will take images as inputs. 

 ### Elastic Search Integration
        This will be integrated into our Q&A Agent replacing our Lookup agent allowing for more reliable and up to date information. 

