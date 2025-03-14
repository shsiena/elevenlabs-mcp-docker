import os
import base64
from pathlib import Path
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, EmbeddedResource, BlobResourceContents, Tool
from elevenlabs.client import ElevenLabs
from elevenlabs import Voice

load_dotenv()
api_key = os.getenv("ELEVENLABS_API_KEY")
if not api_key:
    raise ValueError("ELEVENLABS_API_KEY environment variable is required")

client = ElevenLabs(api_key=api_key)
mcp = FastMCP("ElevenLabs")

@mcp.tool(description="Convert text to speech using specified voice ID")
def text_to_speech(text: str, voice_id: str, file_path: str):
    """Convert text to speech using specified voice ID.

    Args:
        text: The text to convert to speech
        voice_id: The ID of the voice to use, if not provided uses first available voice
        file_path: Optional path to save the audio file, defaults to audio.mp3

    Returns:
        List containing text content and audio data as embedded resource
    """
    if voice_id is None:
        voices = client.voices.get_all()
        voice_id = voices.voices[0].voice_id if voices.voices else None
        if voice_id is None:
            raise ValueError("No voices available")

    audio_data = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    audio_bytes = b"".join(audio_data)

    if file_path:
        if os.path.isabs(file_path):
            output_path = file_path
        else:
            downloads_dir = os.path.expanduser("~/Downloads")
            output_path = os.path.join(downloads_dir, file_path)
    else:
        downloads_dir = os.path.expanduser("~/Downloads")
        output_path = os.path.join(downloads_dir, "audio.mp3")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(audio_bytes)

    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
    filename = Path(output_path).name
    resource_uri = f"audio://{filename}"

    return [
        TextContent(
            type="text",
            text=f"Audio generation successful. File saved as: {output_path}",
        ),
        EmbeddedResource(
            type="resource",
            resource=BlobResourceContents(
                uri=resource_uri,
                name=filename,
                blob=audio_base64,
                mimeType="audio/mpeg",
            ),
        ),
    ]


@mcp.tool(description="List all available voices")
def list_voices() -> TextContent:
    """List all available voices.

    Returns:
        A formatted list of available voices with their IDs and names
    """
    response = client.voices.get_all()
    voice_list = "\n".join(
        f"- {voice.name} (ID: {voice.voice_id}, Category: {voice.category})"
        for voice in response.voices
    )
    return TextContent(type="text", text=f"Available voices:\n{voice_list}")


@mcp.resource("voices://list")
def get_voices() -> list[Voice]:
    """Get a list of all available voices."""
    response = client.voices.get_all()
    return response.voices


@mcp.resource("voice://{voice_id}")
def get_voice(voice_id: str) -> Voice:
    """Get details of a specific voice."""
    response = client.voices.get_all()
    for voice in response.voices:
        if voice.voice_id == voice_id:
            return voice
    raise ValueError(f"Voice with ID {voice_id} not found")


@mcp.tool(description="Clone a voice using provided audio files")
def voice_clone(name: str, files: list[str], description: str | None = None) -> TextContent:
    voice = client.clone(name=name, description=description, files=files)

    return TextContent(
        type="text",
        text=f"""Voice cloned successfully:
        Name: {voice.name}
        ID: {voice.voice_id}
        Category: {voice.category}
        Description: {voice.description or "N/A"}
        Labels: {", ".join(voice.labels) if voice.labels else "None"}
        Preview URL: {voice.preview_url or "N/A"}
        Available for Cloning: {voice.fine_tuning.available_for_cloning}
            Fine Tuning Status: {voice.fine_tuning.status}""",
    )


@mcp.tool(description="Transcribe speech from an audio file")
def speech_to_text(file_path: str, language_code: str = "eng", diarize=False) -> TextContent:
    """Transcribe speech from an audio file using ElevenLabs API.

    Args:
        file_path: Path to the audio file to transcribe
        language_code: Language code for transcription (default: "eng" for English)

    Returns:
        TextContent containing the transcription
    """
    with open(file_path, "rb") as f:
        audio_bytes = f.read()
    transcription = client.speech_to_text.convert(
        model_id="scribe_v1",
        file=audio_bytes,
        language_code=language_code,
        enable_logging=True,
        diarize=diarize,
        tag_audio_events=True,
    )

    return TextContent(type="text", text=f"Transcription:\n{transcription.text}")


@mcp.tool(description="Convert text description to sound effects")
def text_to_sound_effects(text: str, duration_seconds: float, file_path: str) -> list[TextContent | EmbeddedResource]:
    audio_data = client.text_to_sound_effects.convert(
        text=text,
        output_format="mp3_44100_128",
        duration_seconds=duration_seconds,
    )
    audio_bytes = b"".join(audio_data)

    if os.path.isabs(file_path):
        output_path = file_path
    else:
        downloads_dir = os.path.expanduser("~/Downloads")
        output_path = os.path.join(downloads_dir, "sound_effect.mp3")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(audio_bytes)

    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
    filename = Path(output_path).name
    resource_uri = f"audio://{filename}"

    return [
        TextContent(
            type="text",
            text=f"Sound effect generation successful. File saved as: {output_path}",
        ),
        EmbeddedResource(
            type="resource",
            resource=BlobResourceContents(
                uri=resource_uri,
                name=filename,
                blob=audio_base64,
                mimeType="audio/mpeg",
            ),
        ),
    ]


@mcp.tool(description="Isolate audio from a file")
def isolate_audio(input_file_path: str, output_file_path: str) -> list[TextContent | EmbeddedResource]:
    if not os.path.exists(input_file_path):
        raise ValueError(f"Input file not found: {input_file_path}")

    with open(input_file_path, "rb") as f:
        audio_bytes = f.read()

    isolated_audio = b"".join(client.audio_isolation.audio_isolation(audio=audio_bytes))

    if output_file_path is None:
        downloads_dir = os.path.expanduser("~/Downloads")
        output_file_path = os.path.join(downloads_dir, "isolated_audio.mp3")
    elif not os.path.isabs(output_file_path):
        downloads_dir = os.path.expanduser("~/Downloads")
        output_file_path = os.path.join(downloads_dir, output_file_path)

    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    with open(output_file_path, "wb") as f:
        f.write(isolated_audio)

    audio_base64 = base64.b64encode(isolated_audio).decode("utf-8")
    filename = Path(output_file_path).name
    resource_uri = f"audio://{filename}"

    return [
        TextContent(
            type="text",
            text=f"Audio isolation successful. File saved as: {output_file_path}",
        ),
        EmbeddedResource(
            type="resource",
            resource=BlobResourceContents(
                uri=resource_uri,
                name=filename,
                blob=audio_base64,
                mimeType="audio/mpeg",
            ),
        ),
    ]


@mcp.tool(description="Check the current subscription status. Could be used to measure the usage of the API.")
def check_subscription() -> TextContent:
    subscription = client.user.get_subscription()
    return TextContent(
        type="text",
        text=f"{subscription.model_dump_json(indent=2)}"
    )


if __name__ == "__main__":
    mcp.run()
