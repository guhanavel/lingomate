import os
from google.cloud import speech

credential_path = "eduflare-9f4c5-c0cd9ba0c6aa.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
speech_client = speech.SpeechClient()

## Example 1: Transcribe Local Media File

def gtts(file):
    media_file_name_wav = file

    with open(media_file_name_wav, 'rb') as f1:
        byte_data_wav = f1.read()
    audio_wav = speech.RecognitionAudio(content=byte_data_wav)

    ## Configuring Media Output
    config_wav = speech.RecognitionConfig(
        encoding = 'ENCODING_UNSPECIFIED',
        sample_rate_hertz = 48000,
        language_code = 'de-DE',
        audio_channel_count = 1,
        enable_automatic_punctuation=True
    )

    response_standard_wav = speech_client.recognize(
        config=config_wav,
        audio=audio_wav
    )
    return response_standard_wav.results[0].alternatives[0].transcript
