import { client } from "@serenity-kit/opaque";

interface ServerStartLoginResponse {
    loginResponse: string;
    requestId: string;
}

interface StartLoginResult {
    password: string;
    clientLoginState: string;
    serverLoginResponse: string;
    serverRequestId: string;
}

export async function startLogin(
        username: string,
        password: string,
): Promise<StartLoginResult> {
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

    if (!response.ok) {
        throw new Error("Failed to start login");
    }

    const serverResponse =
        await response.json() as ServerStartLoginResponse;

    return {
        password,
        clientLoginState,
        serverLoginResponse: serverResponse.loginResponse,
        serverRequestId: serverResponse.requestId
    }
}

export async function finishLogin(
        startLoginResult: StartLoginResult,
): null {
    const loginResponse = startLoginResult.serverLoginResponse.replace(/=+$/, "");
    const { finishLoginRequest } = client.finishLogin({
        password: startLoginResult.password,
        clientLoginState: startLoginResult.clientLoginState,
        loginResponse,
    })

    const response = await fetch("/api/login/finish", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            requestId: startLoginResult.serverRequestId,
            finishLoginRequest,
        })
    });

    if (!response.ok) {
        throw new Error("Failed to finish login");
    }
}