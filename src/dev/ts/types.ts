export interface ServerResponse {
    success: boolean;
    message: string;
    data: Record<string, any>[];
}

export interface LoginStartResult {
    password: string;
    state: string;
    serverResponse: ServerResponse;
}

export interface RegistrationStartResult {
    username: string;
    password: string;
    state: string;
    serverResponse: ServerResponse;
}