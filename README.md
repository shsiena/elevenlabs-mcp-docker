# Eleven Labs MCP Server

[![smithery badge](https://smithery.ai/badge/@jacekduszenko/11labs-mcp)](https://smithery.ai/server/@jacekduszenko/11labs-mcp)

A Model Context Protocol (MCP) server that enables interaction with Eleven Labs' powerful text-to-speech and audio processing APIs. This server allows Claude and other AI assistants to generate speech, clone voices, transcribe audio, and more.

<a href="https://glama.ai/mcp/servers/11labs-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/11labs-mcp/badge" alt="Eleven Labs MCP server" />
</a>

## Quick Start

1. Get your API key from [Eleven Labs](https://elevenlabs.io/). You'll need an account to access the API.

2. Add this configuration to your Claude Desktop config file:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ElevenLabs": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "elevenlabs",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "11labs_mcp/server.py"
      ],
      "env": {
        "ELEVENLABS_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

3. Restart Claude Desktop

That's it! Claude can now interact with Eleven Labs through these tools:

- `text_to_speech`: Convert text to speech using a specified voice
- `list_voices`: Get a list of all available voices
- `voice_clone`: Clone a voice using provided audio files
- `speech_to_text`: Transcribe speech from an audio file
- `text_to_sound_effects`: Generate sound effects from text descriptions
- `isolate_audio`: Isolate audio from a file
- `check_subscription`: Check your Eleven Labs subscription status

## Example Usage

Try asking Claude:
- "Can you convert this text to speech using a British accent?"
- "What voices are available for text-to-speech?"
- "Can you transcribe this audio file for me?"
- "Generate some rain sound effects"

## Development

If you want to contribute or run from source:

1. Clone the repository:
```bash
git clone https://github.com/jacekduszenko/11labs-mcp.git
cd 11labs-mcp
```

2. Create a virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

3. Copy `.env.example` to `.env` and add your Eleven Labs API key:
```bash
cp .env.example .env
# Edit .env and add your API key
```

4. Run the server:
```bash
python -m 11labs_mcp.server
```

## Requirements

- Python 3.11 or higher
- Dependencies:
  - mcp>=0.1.0
  - fastapi==0.109.2
  - uvicorn==0.27.1
  - python-dotenv==1.0.1
  - pydantic>=2.6.1
  - httpx==0.28.1
  - elevenlabs>=1.54.0

## Troubleshooting

Logs can be found at:
- **Windows**: `%APPDATA%\Claude\logs\mcp-server-elevenlabs.log`
- **macOS**: `~/Library/Logs/Claude/mcp-server-elevenlabs.log`

## License

MIT 