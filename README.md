> [!NOTE]
> This project was written entirely by AI. Our teacher told us to create some basic app using copilot, to get a higher grade, so I did.

# MoodMusic

A tiny Python project that recommends songs based on a user-provided mood description.

- Embeddings: `sentence-transformers/all-MiniLM-L6-v2`
- HTTP API: FastAPI
- Agent/tool API: MCP server (stdio)
- Package manager: `uv`

## Setup

```powershell
git clone <your-repo-url>
cd MoodMusic
uv sync
```

This will create a virtualenv and install dependencies.

## Run the HTTP API

```powershell
uv run moodmusic-api
```

Open the web UI:

- http://127.0.0.1:8000/

Then call it:

```powershell
$body = @{ mood_text = "I feel calm, reflective, and a bit nostalgic. I want something mellow."; k = 5 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/recommend -ContentType application/json -Body $body
```

## Run the MCP server

```powershell
uv run moodmusic-mcp
```

This starts an MCP stdio server exposing a tool named `recommend_songs`.

## Use the CLI

```powershell
uv run moodmusic-recommend "I feel calm, reflective, and a bit nostalgic. I want something mellow." -k 5
```

JSON output:

```powershell
uv run moodmusic-recommend "I feel anxious and restless; I want something grounding" -k 3 --json
```

## Notes

- The first run will download the embedding model from Hugging Face.
- The project ships with a small built-in song catalog in `src/moodmusic/data/songs.json`.
  Replace it with your own dataset later (Spotify export, etc.).

## Configuration

Set the embedding model via environment variable:

```powershell
$env:MOODMUSIC_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```
