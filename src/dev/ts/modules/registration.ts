import { client } from "@serenity-kit/opaque";
import type {
    ServerResponse,
    RegistrationStartResult,
} from "../types";

export async function startRegistration(
        username: string,
        password: string,
): Promise<RegistrationStartResult | string> {
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

    const serverResponse = await response.json() as ServerResponse;

    if (!serverResponse.success) {
        return serverResponse.message;
    }

    return {
        username,
        password,
        state: clientRegistrationState,
        serverResponse,
    }
}

export async function finishRegistration(
    startResult: RegistrationStartResult,
): Promise<ServerResponse | string> {
    const registrationResponse = startResult.serverResponse.data.registrationResponse.replace(/=+$/, "");
    const result = client.finishRegistration({
        password: startResult.password,
        clientRegistrationState: startResult.state,
        registrationResponse
    });

    if (!result) {
        return "Failed to finish registration";
    }

    const { registrationRecord } = result;

    const response = await fetch("/api/registration/finish", {
        method: "POST",
        headers: {"Content-Type": "application/json" },
        body: JSON.stringify({
            requestId: startResult.serverResponse.data.requestId,
            registrationRecord,
        })
    });

    return await response.json();
}