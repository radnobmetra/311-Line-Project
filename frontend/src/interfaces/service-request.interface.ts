export interface ServiceRequest {
    id: string;
    conversationId: string;
    categoryId: string;
    title: string;
    description: string;
    status: string;
    priority: string;
    address: string;
    latitude: number;
    longitude: number;
    createdAt: string;
    updatedAt: string;
    resolvedAt: string;
    closedAt: string;
}
