function addAgentChat() {
  if (document.getElementById("ai-agent-wrapper")) return;

  let wrapper = document.createElement("div");
  wrapper.id = "ai-agent-wrapper";
  wrapper.style = "position:fixed; bottom:20px; right:20px; z-index:9999; font-family: sans-serif;";

  let chatBox = document.createElement("div");
  chatBox.id = "ai-chat-box";
  chatBox.style = "display:none; width:320px; height:420px; background:white; border-radius:12px; box-shadow: 0 8px 30px rgba(0,0,0,0.3); flex-direction:column; border:1px solid #ddd; margin-bottom:15px; overflow:hidden;";
  chatBox.innerHTML = `
    <div style="background:#1a73e8; color:white; padding:15px; font-weight:bold; display:flex; justify-content:space-between; align-items:center;">
      <span>AI Agent</span>
      <span id="close-chat" style="cursor:pointer; font-size:20px;">×</span>
    </div>
    <div id="chat-history" style="flex:1; padding:15px; overflow-y:auto; font-size:13px; line-height:1.5; color:#333;">
      <p style="color:#888;">System: Agent ready. How can I assist you today?</p>
    </div>
    <div style="padding:10px; border-top:1px solid #eee; display:flex; gap:8px;">
      <input id="agent-input" type="text" placeholder="Type a command..." style="flex:1; padding:10px; border:1px solid #ddd; border-radius:8px; outline:none;">
      <button id="send-btn" style="background:#1a73e8; color:white; border:none; padding:10px 15px; border-radius:8px; cursor:pointer; font-weight:bold;">Send</button>
    </div>
  `;

  let mainBtn = document.createElement("button");
  mainBtn.innerHTML = "🤖";
  mainBtn.style = "width:60px; height:60px; background:#1a73e8; color:white; border:none; border-radius:50%; cursor:pointer; font-size:28px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); float:right;";

  mainBtn.onclick = () => { chatBox.style.display = chatBox.style.display === "none" ? "flex" : "none"; };
  wrapper.appendChild(chatBox);
  wrapper.appendChild(mainBtn);
  document.body.appendChild(wrapper);

  document.getElementById("close-chat").onclick = () => { chatBox.style.display = "none"; };

  document.getElementById("send-btn").onclick = async () => {
    let input = document.getElementById("agent-input");
    let history = document.getElementById("chat-history");
    let command = input.value;
    if (!command) return;

    history.innerHTML += `<div style="margin-top:10px; text-align:right;"><b>You:</b> ${command}</div>`;
    input.value = "";

    let loadingDiv = document.createElement("div");
    loadingDiv.style = "margin-top:10px; color:#1a73e8; font-style:italic;";
    loadingDiv.innerText = "Processing...";
    history.appendChild(loadingDiv);

    try {
      const response = await fetch("http://localhost:5000/webhook", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ command: command })
      });
      const data = await response.json();
      loadingDiv.remove();
      history.innerHTML += `<div style="margin-top:10px; background:#f1f3f4; padding:8px; border-radius:8px;"><b>Agent:</b> ${data.reply}</div>`;
    } catch (e) {
      loadingDiv.innerText = "Error: Connection failed.";
      loadingDiv.style.color = "red";
    }
    history.scrollTop = history.scrollHeight;
  };
}
setInterval(addAgentChat, 2000);
