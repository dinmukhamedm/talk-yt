async function getCurrentTab() {
  let queryOptions = { active: true, lastFocusedWindow: true };
  // `tab` will either be a `tabs.Tab` instance or `undefined`.
  let [tab] = await chrome.tabs.query(queryOptions);
  return tab;
}

const sendButton = document.getElementById('send-button');
const userInput = document.getElementById('user-input');

if(sendButton){
  sendButton.addEventListener('click', () => {

    const message = userInput.value;
    if (message.trim() !== '') {
      // chrome.runtime.sendMessage(chrome.runtime.id, {kind: 'raw_user_message', text: message });
      window.parent.postMessage({kind: 'raw_user_message', text: message }, 'https://www.youtube.com');
      addOutgoingMessage(message);
      userInput.value = ''; // Clear the input field
    }
  });
}

window.addEventListener('message', (message) => {
  console.log(message);
  if (message.data.kind === "agent_response")
    addIncomingMessage(message.data.text, message.data.timestamp);
})

function addIncomingMessage(message, timestamp = null) {
  const chatHistory = document.querySelector('.chat-history');
  const messageElement = createMessageElement(message, 'incoming', timestamp);
  chatHistory.appendChild(messageElement);
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

function addOutgoingMessage(message) {
  const chatHistory = document.querySelector('.chat-history');
  const messageElement = createMessageElement(message, 'outgoing');
  chatHistory.appendChild(messageElement);
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

function createMessageElement(message, className, timestamp = null) {
  const messageDiv = document.createElement('div');
  messageDiv.classList.add('message', className);

  const avatarDiv = document.createElement('div');
  avatarDiv.classList.add('avatar');
  const avatarImg = document.createElement('img');
  if (className === 'outgoing'){
    avatarImg.src = 'static/user.png';
  } else {
    avatarImg.src = 'static/avatar.jpg';
  }
  avatarDiv.appendChild(avatarImg);

  const messageContentDiv = document.createElement('div');
  messageContentDiv.classList.add('message-content');

  const messageTextDiv = document.createElement('div');
  messageTextDiv.classList.add('message-text');
  messageTextDiv.textContent = message;

  const messageTimeDiv = document.createElement('div');
  messageTimeDiv.classList.add('message-time');
  const spanMessageTime = document.createElement('span');
  const messageTime = timestamp ? new Date(timestamp) : new Date();
  const formattedTimestamp = messageTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  spanMessageTime.textContent = formattedTimestamp;
  messageTimeDiv.appendChild(spanMessageTime);

  messageContentDiv.appendChild(messageTextDiv);
  messageContentDiv.appendChild(messageTimeDiv);

  messageDiv.appendChild(avatarDiv);
  messageDiv.appendChild(messageContentDiv);

  return messageDiv;
}
