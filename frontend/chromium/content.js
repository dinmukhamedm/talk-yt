function insertCustomHTML() {
  const customHTML = `
<iframe
  id="yt-ext-iframe"
  src="${chrome.runtime.getURL("index.html")}"
  data-origin=${window.origin}
  style="
    width:23vw;
    height:60vh;
    min-width:298px;
    min-height:320px;">
</iframe>
`
  let secondaryInnerDiv = null;
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  sleep(2000).then(() => {
    secondaryInnerDiv = document.getElementsByTagName('ytd-app')[0].querySelector("#secondary-inner");
    if (secondaryInnerDiv) {
      const panelsDiv = secondaryInnerDiv.querySelector("#panels");

      if (panelsDiv) {
        panelsDiv.insertAdjacentHTML("afterend", customHTML);
      }
    }
  });

  
}

function getCurrentTimestamp() {
  const videoElement = document.querySelector("video");
  if (videoElement) {
    return videoElement.currentTime;
  } else {
    return null;
  }
}

const socket = new WebSocket('ws://localhost:23369');

socket.addEventListener('open', (event) => {
  console.log('WebSocket connection established');
});

socket.addEventListener('error', (error) => {
  console.error('WebSocket error:', error);
});

socket.addEventListener('close', (event) => {
  console.log('WebSocket connection closed');
});

// Event listener for receiving messages from the server
socket.addEventListener('message', (event) => {
  console.log(event.data)
  const message = JSON.parse(event.data); // Parse the JSON message
  // Handle the received message, e.g., update chat history
  const iframe = document.querySelector('#yt-ext-iframe')
  if (!iframe) return;
  const contentWindow = iframe.contentWindow;
  if (!contentWindow) return;
  contentWindow.postMessage({kind: "agent_response", ...message}, '*');
});

window.addEventListener('message', (message) => {
  if (message.data.kind === 'raw_user_message') {
    const playback_timestamp = getCurrentTimestamp();
    socket.send(
        JSON.stringify({
          text: message.data.text,
          url: document.URL,
          playback_timestamp
        })
      );
  }
});

window.onload = insertCustomHTML;