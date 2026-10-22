import {client, StartLoginResult} from "@serenity-kit/opaque";

interface ServerStartRegistrationResponse {
    registrationResponse: string;
    requestId: string;
}

interface StartRegistrationResult {
    username: string;
    password: string;
    clientRegistrationState: string;
    serverRegistrationResponse: string;
    serverRequestId: string
}

export async function startRegistration(
        username: string,
        password: string,
): Promise<StartLoginResult> {
    const { clientRegistrationState, registrationRequest } =
        client.startRegistration({ password });

    const response = await fetch("/api/registration/start", {
        method: "POST",
        headers: {"Content-Type": "application/json" },
        body: JSON.stringify({
            username,
            registrationRequest,
        })
    });

    if (!response.ok) {
        throw new Error("Failed to start registration");
    }

    const serverResponse =
        await response.json() as ServerStartRegistrationResponse;

    return {
        username,
        password,
        clientRegistrationState,
        serverRegistrationResponse: serverResponse.registrationResponse,
        serverRequestId: serverResponse.requestId
    }
}

export async function finishRegistration(
    startRegistrationResult: StartRegistrationResult,
): null {
    const registrationResponse = startRegistrationResult.serverRegistrationResponse.replace(/=+$/, "");
    const { registrationRecord } = client.finishRegistration({
        password: startRegistrationResult.password,
        clientRegistrationState: startRegistrationResult.clientRegistrationState,
        registrationResponse
    });

    const response = await fetch("/api/registration/finish", {
        method: "POST",
        headers: {"Content-Type": "application/json" },
        body: JSON.stringify({
            requestId: startRegistrationResult.serverRequestId,
            registrationRecord,
        })
    });

    if (!response.ok) {
        throw new Error("Failed to finish registration");
    }
}