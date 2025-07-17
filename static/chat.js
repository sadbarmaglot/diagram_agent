const chatBox = document.getElementById("chat-box");
const input = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

const socket = new WebSocket("ws://localhost:8000/ws/assistant");

let connectionStart = Date.now();

socket.onopen = () => {
    connectionStart = Date.now();
    console.log("📡 WebSocket connected");
    addMessage("Hi! Describe your architecture — I will generate a diagram or ask a follow-up question.", "bot");
};

socket.onmessage = (event) => {
    const msg = JSON.parse(event.data);

    if (msg.type === "question") {
    addMessage("🤖 " + msg.text, "bot");
    }

    if (msg.type === "message") {
    addMessage("🤖 " + msg.text, "bot");
    }

    if (msg.type === "diagram") {
    addImage(msg.path);
    }
};

socket.onclose = (event) => {
    console.warn(`🔌 Connection closed (code ${event.code}). Lifetime: ${lived} seconds`);
    addMessage("❌ Connection closed", "bot");
};

socket.onerror = (err) => {
    console.error("WebSocket error:", err);
    addMessage("⚠️ A connection error occurred", "bot");
};

function sendMessage() {
    const text = input.value.trim();
    if (!text || socket.readyState !== WebSocket.OPEN) return;

    addMessage(text, "user");
    socket.send(text);
    input.value = "";
}

function addMessage(text, sender) {
    const message = document.createElement("div");
    message.className = `message ${sender}`;
    message.innerHTML = text.replace(/\n/g, "<br>");
    chatBox.appendChild(message);
    scrollChatToBottom();
}

function addImage(url) {
    const wrapper = document.createElement("div");
    wrapper.className = "message bot";

    const caption = document.createElement("div");
    caption.textContent = "📊 Diagram:";
    caption.style.marginBottom = "8px";

    const img = document.createElement("img");
    img.src = url;
    img.alt = "Diagram";
    img.className = "diagram";

    wrapper.appendChild(caption);
    wrapper.appendChild(img);
    chatBox.appendChild(wrapper);
    scrollChatToBottom();
}

function scrollChatToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

sendButton.addEventListener("click", sendMessage);
input.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});
