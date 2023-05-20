

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete" && tab.active && tab.url.startsWith("https://youtube.com/watch")) {
    chrome.scripting.executeScript({
      target: {tabId, allFrames: true},
      files: ["content.js"] 
    });
  }
});
