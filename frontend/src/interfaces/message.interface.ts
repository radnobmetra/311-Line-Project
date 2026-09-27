export interface Message {
    id: string;
    conversationId: string;
    requestId: string;
    twilioMessageSid: string;
    direction: string;
    fromNumber: string;
    body: string;
    sentAt: string;
}
