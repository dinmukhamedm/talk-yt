# Talk to YouTube extension

Talk to any YouTube video

## Installation

### Backend

1. Create a json file `tokens.json` that will have your model provider tokens in the following format
```json
{
  "openai": "<YOUR_OPENAI_TOKEN>",
  "anthropic": "<YOUR_ANTHROPIC_TOKEN>",
  "...": "..."
}
```
2. Install the requirements: `pip install -r requirements.txt`
3. Run the server from the `talk-yt` directory: `python websocket.py`

### Frontend

1. Open any Chromium-based browser (e.g. Google Chrome, Opera, Brave)
1. Go to the extension page at `chrome://extensions`, or by following sandwich button > More Tools > Extensions
1. Make sure "Developer mode" is enabled, usually in the top-right corner
1. Click "Load unpacked" and select the `chromium` directory from the `frontend` directory.

