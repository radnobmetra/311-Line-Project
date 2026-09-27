export interface RequestHistory {
    id: string;
    requestId: string;
    userId: string;
    action: string;
    oldValue: string;
    newValue: string;
    createdAt: string;
}