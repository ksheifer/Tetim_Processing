import os
import time
import subprocess
from tenacity import retry, stop_after_attempt, wait_fixed

# Set the stream URL
STREAM_URL = "http://icecast-saha.cdnvideo.ru/saha"

# Set the directory where you want to save the recordings
OUTPUT_DIR = os.path.expanduser("~/Documents/Languages/Turkic/NorthSiberian/YKT/radio")

# Recording duration (in HH:MM:SS format)
RECORDING_DURATION = "01:00:00"

# Function to record audio
@retry(stop=stop_after_attempt(10), wait=wait_fixed(10))
def record_stream():
    # Generate a timestamp for the filename
    TIMESTAMP = time.strftime("%Y%m%d_%H%M%S")

    # Set the output file name
    OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"radio_{TIMESTAMP}.wav")

    # Record for the specified duration
    command = [
        "ffmpeg",
        "-i", STREAM_URL,
        "-t", RECORDING_DURATION,
        "-ar", "16000",   # Set the sample rate to 16 kHz
        "-ac", "1",       # Set to mono audio
        OUTPUT_FILE       # Output file with .wav extension
    ]

    # Execute the ffmpeg command
    result = subprocess.run(command, check=True)
    print(f"Recorded: {OUTPUT_FILE}")
    return result

# Start recording in a loop
while True:
    try:
        record_stream()
    except subprocess.CalledProcessError as e:
        print(f"Error while recording: {e}")