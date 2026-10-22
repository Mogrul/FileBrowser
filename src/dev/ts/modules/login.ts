import { client } from "@serenity-kit/opaque";
import type {
    ServerResponse,
    LoginStartResult
} from "../types";

export async function logout(): Promise<void> {
    const response = await fetch("/api/login/logout", { method: "POST" });
    const serverResponse = await response.json() as ServerResponse;

    console.log(serverResponse);
}

export async function startLogin(
        username: string,
        password: string,
): Promise<LoginStartResult | string> {
    const { clientLoginState, startLoginRequest } =
        client.startLogin({ password });

    const response = await fetch("/api/login/start", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            username,
            startLoginRequest,
        }),
    });

    const serverResponse = await response.json() as ServerResponse;

    if (!serverResponse.success) {
        return serverResponse.message;
    }

    return {
        password,
        state: clientLoginState,
        serverResponse,
    }
}

export async function finishLogin(
        loginResult: LoginStartResult,
): Promise<ServerResponse | string> {
    const loginResponse = loginResult.serverResponse.data.loginResponse.replace(/=+$/, "");
    const result = client.finishLogin({
        password: loginResult.password,
        clientLoginState: loginResult.state,
        loginResponse,
    });

    if (!result) {
        return "Invalid request";
    }

    const { finishLoginRequest } = result;

    const response = await fetch("/api/login/finish", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            requestId: loginResult.serverResponse.data.requestId,
            finishLoginRequest,
        })
    });

    return await response.json();
}