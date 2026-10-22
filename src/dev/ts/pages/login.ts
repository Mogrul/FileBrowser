import {startLogin, finishLogin} from "../modules/login";
import {startRegistration, finishRegistration} from "../modules/registration";

const form = document.getElementById("form") as HTMLFormElement | null;
const alert = document.getElementById("message") as HTMLParagraphElement | null;
const loginButton = document.getElementById("login-button") as HTMLButtonElement | null;
const registerButton = document.getElementById("register-button") as HTMLButtonElement | null;

if (form) {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const formaData = new FormData(form);
        const username = formaData.get("username")?.toString().trim()
        const password = formaData.get("password")?.toString();

        if (!username || !password) {
            return;
        }

        const submitter = event.submitter as HTMLButtonElement | null;
        const action = submitter?.value;

        try {
            disableButtons();
            let alertMessage: string;

            if (action === "login") {
                const startResult = await startLogin(username, password);

                if (typeof startResult === "string") {
                    alertMessage = startResult;
                } else {
                    const finishResult = await finishLogin(startResult);

                    if (typeof finishResult === "string") {
                        alertMessage = finishResult;
                    } else {
                        window.location.href = "/";
                        return;
                    }
                }
            } else if (action === "register") {
                const startResult = await startRegistration(username, password);

                if (typeof startResult === "string") {
                    alertMessage = startResult;
                } else {
                    const finishResult = await finishRegistration(startResult);

                    if (typeof finishResult === "string") {
                        alertMessage = finishResult;
                    } else {
                        alertMessage = finishResult.message;
                    }
                }
            } else {
                return;
            }

            if (alert) {
                alert.textContent = alertMessage;
            }

        } finally {
            enableButtons();
        }
    });
}

function disableButtons() {
    if (loginButton && registerButton) {
        loginButton.disabled = true;
        registerButton.disabled = true;
    }
}

function enableButtons() {
    if (loginButton && registerButton) {
        loginButton.disabled = false;
        registerButton.disabled = false;
    }
}