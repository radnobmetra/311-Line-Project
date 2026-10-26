import { Component, inject, signal } from '@angular/core';
import { ChatMessage } from '../../interfaces/chat-message.interface';
import { AgentChatService } from '../../services/agent-chat.service';
import { FormsModule } from '@angular/forms';
import { form, FormField } from '@angular/forms/signals';

interface userInputInterface {
  input: string;
}

@Component({
  imports: [FormsModule, FormField],
  selector: 'agent-chat',
  styleUrl: './agent-chat.css',
  templateUrl: './agent-chat.html',
})

export class agentChat {
  //The latest response from the server
  latestMessage = signal<ChatMessage>({ author: "", contents: "" });
  agentChatService = inject(AgentChatService);
  //array of all messages except latestMessage
  messages: ChatMessage[];
  //input type is normal if user is messaging the agent, 
  // thumbsUp or thumbsDown if they are leaving feedback
  inputType: string;

  constructor() {
    this.messages = [];
    this.inputType = "normal";
    this.imageFileName = "";

  }

  //needed to get text box input
  userInputModel = signal<userInputInterface>({
    input: ""
  });
  userInputForm = form(this.userInputModel);

  imageFileName: string;
  imageFile: any;

  //============================================================
  //          manage message type
  //============================================================

  //constant variables for class of buttons 
  thumbsDownBtnClass_Default = "thumbsDownBtn";
  thumbsUpBtnClass_Default = "thumbsUpBtn";
  thumbsDownBtnClass_Selected = "thumbsDownBtn_selected";
  thumbsUpBtnClass_Selected = "thumbsUpBtn_selected";

  //variables to change class of buttons
  thumbsDownBtnClass = this.thumbsDownBtnClass_Default;
  thumbsUpBtnClass = this.thumbsUpBtnClass_Default;

  //attached to thumbsUp button; changes button styles and value of inputType 
  thumbsUp() {
    if (this.inputType == "up") {
      this.inputType = "normal";
      this.thumbsUpBtnClass = this.thumbsUpBtnClass_Default;
      this.thumbsDownBtnClass = this.thumbsDownBtnClass_Default;
    } else {
      this.inputType = "up";
      this.thumbsUpBtnClass = this.thumbsUpBtnClass_Selected;
      this.thumbsDownBtnClass = this.thumbsDownBtnClass_Default;
    }
  }

  //attached to thumbsDown button; changes button styles and value of inputType 
  thumbsDown() {
    if (this.inputType == "down") {
      this.inputType = "normal";
      this.thumbsUpBtnClass = this.thumbsUpBtnClass_Default;
      this.thumbsDownBtnClass = this.thumbsDownBtnClass_Default;
    } else {
      this.inputType = "down";
      this.thumbsUpBtnClass = this.thumbsUpBtnClass_Default;
      this.thumbsDownBtnClass = this.thumbsDownBtnClass_Selected;
    }
  }

  uploadImage(event: any) {
    if ((event) && (event.target) && (event.target.files[0])) {
      this.imageFile = event.target.files[0];
      if (this.imageFile) {
        this.imageFileName = this.imageFile.name;
        console.log(this.imageFileName);
        this.inputType = "image";
      }
    }
  }

  //============================================================
  //                    clear user input
  //============================================================

  clear() {
    //reset variables pertaining to user input
    this.userInputForm().reset({ input: "" });
    this.inputType = "normal";
    this.thumbsDownBtnClass = this.thumbsDownBtnClass_Default;
    this.thumbsUpBtnClass = this.thumbsUpBtnClass_Default;
    this.imageFileName = ""
    this.imageFile = null;
  }

  //============================================================
  //                    send message
  //============================================================

  sendMessage() {
    //for now, only send timages with no text component
    if (this.inputType == "image") {
      this.sendImage();
      this.clear();
      return;
    }

    //get and format user's message
    let message = this.userInputForm.input().value();
    let formattedMessage = this.formatInput(message, this.inputType);

    //send message if user entered valid input
    if (formattedMessage != "invalid") {
      //store the agent's last message 
      if (this.latestMessage().author != "" && this.latestMessage().contents != "") {
        this.messages.push({
          author: this.latestMessage().author,
          contents: this.latestMessage().contents
        });
      }

      //store regular user message in message array
      if (this.inputType == "up") {
        if (message.length >= 2)
          this.messages.push({ author: "user", contents: "Sent thumbs up with comment: " + message })
        else
          this.messages.push({ author: "user", contents: "Sent thumbs up." })
      }

      //store user feedback message in message array
      else if (this.inputType == "down") {
        if (message.length >= 2)
          this.messages.push({ author: "user", contents: "Sent thumbs down with comment: " + message })
        else
          this.messages.push({ author: "user", contents: "Sent thumbs down." })
      }
      else {
        this.messages.push({ author: "user", contents: message })
      }

      //reset latest message signal
      this.latestMessage.set({ author: " ", contents: "Waiting for response..." });

      //send message using flask backend and store response in latestMessage
      this.agentChatService.sendMessage(formattedMessage).subscribe({
        next: (msg) => this.latestMessage.set(msg),
        error: (err) => this.latestMessage.set({ author: "Error", contents: "A connection error occurred." })
      });

      this.clear();
    }

    //user entered invalid input:
    else {
      //store latest agent message
      if (this.latestMessage().author != "" && this.latestMessage().contents != "") {
        this.messages.push({
          author: this.latestMessage().author,
          contents: this.latestMessage().contents
        });
      }

      //reset latestMessage
      this.latestMessage.set({ author: "", contents: "" });

      //add error message to list of messages
      this.messages.push({
        author: "Error",
        contents: "Messages must be between 2 and 300 characters."
      });
    }
  }

  formatInput(message: string, messageType: string): string {
    let messageStr = "";

    if (messageType == "up") {
      messageStr = "/up " + message;
    }
    else if (messageType == "down") {
      messageStr = "/down " + message;
    }

    //format regular message 
    else if (messageType == "normal") {
      if (message.length >= 2) {
        messageStr = message;
      }
      else {
        //don't accept messages under 2 chars 
        messageStr = "invalid";
      }
    }

    //don't accept messages over 160 chars
    if (messageStr.length > 300) {
      messageStr = "invalid";
    }

    return messageStr;
  }

  //============================================================
  //                    send image
  //============================================================

  sendImage() {
    this.messages.push({ author: "user", contents: "Sent an image: " + this.imageFileName });

    //reset latest message signal
    this.latestMessage.set({ author: " ", contents: "Waiting for response..." });

    //send message using flask backend and store response in latestMessage
    this.agentChatService.sendImage(this.imageFile).subscribe({
      next: (msg) => this.latestMessage.set(msg),
      error: (err) => this.latestMessage.set({ author: "Error", contents: "A connection error occurred." })
    });
  }
}