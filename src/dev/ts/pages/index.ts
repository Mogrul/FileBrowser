import { logout } from "../modules/login";
import {ServerResponse} from "../types";

const loginButton = document.getElementById("logout-button") as HTMLButtonElement;
const configButton = document.getElementById("config-button") as HTMLButtonElement;
const failedThumbnailCards: HTMLLinkElement[] = [];

if (loginButton) {
    loginButton.addEventListener("click", async () => {
        await logout();
        window.location.href = "/login";
    });
}

if (configButton) {
    configButton.addEventListener("click", async () => {

    });
}

document.querySelectorAll<HTMLImageElement>(".file-card img").forEach((img) => {
    const card = img.closest<HTMLLinkElement>(".file-card");

    if (!card) return;

    const addFailedCard = () => {
        if (!failedThumbnailCards.includes(card)) {
            failedThumbnailCards.push(card);
        }
    };

    img.addEventListener("error", addFailedCard);

    if (img.complete && img.naturalWidth === 0) {
        addFailedCard();
    }
});

async function processFailedThumbnails() {
    const cards = failedThumbnailCards.splice(0);
    const cardIds: Array<string> = [];

    for (const card of cards) {
        const cardId = card.dataset.id;

        if (!cardId) continue;
        cardIds.push(cardId);
    }

    if (cardIds.length == 0) return;

    const response = await fetch("/api/files/thumbnails", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            "ids": cardIds
        }),
    });

    const serverResponse = await response.json() as ServerResponse;
    const cardById = new Map<string, HTMLLinkElement>(
        cards
            .filter(card => card.dataset.id)
            .map(card => [card.dataset.id!, card])
    );

    console.log(serverResponse.data);

    for (const item of serverResponse.data) {
        const card = cardById.get(item.id);

        if (!card) continue;

        const img = card.querySelector<HTMLImageElement>("img");

        if (img) {
            img.src = item.url;
        }
    }

}

setInterval(async () => {
   if (failedThumbnailCards.length > 0) {
       await processFailedThumbnails();
   }
}, 100);