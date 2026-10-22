import {startLogin, finishLogin} from "../modules/login";
import {startRegistration, finishRegistration} from "../modules/registration";

const loginButton = document.getElementById("login-button");
const registerButton = document.getElementById("register-button");

loginButton.addEventListener("click", async () => {
    const startResult = await startLogin("username", "password");
    const finishResult = await finishLogin(startResult);
});

registerButton.addEventListener("click", async () => {
    const startResult = await startRegistration("username", "password");
    const finishResult = await finishRegistration(startResult);
});