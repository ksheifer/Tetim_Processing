import torch
import time
from pyannote.audio.pipelines import SpeakerDiarization
from pyannote.core import Annotation
from pydub import AudioSegment
import os
import sys
import argparse

def diarize_and_segment(audio_file):
    """
    Perform speaker diarization on the provided audio file and split it into segments.
    """
    # Check if GPU is available
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Using device: {device}")

    # Load the speaker diarization model
    pipeline = SpeakerDiarization.from_pretrained("pyannote/speaker-diarization")
    pipeline.to(device)

    # Start measuring time
    print("Starting diarization...")
    start_time = time.time()

    # Extract the filename without extension and create a path to save the results
    filename = os.path.splitext(os.path.basename(audio_file))[0]
    output_txt_path = f'{os.path.dirname(audio_file)}/{filename}.txt'

    # Perform diarization
    try:
        diarization = pipeline(audio_file)
        if isinstance(diarization, Annotation):
            with open(output_txt_path, mode='w') as txt_file:
                txt_file.write(str(diarization))
            print(f"Diarization results saved to '{output_txt_path}'.")
        else:
            raise ValueError("Diarization result is not an Annotation object.")
    except Exception as e:
        print(f"Error during diarization: {e}")
        return

    print("Diarization completed. Starting segmentation...")

    # Function to convert time format to milliseconds
    def parse_time_to_ms(time_str):
        hours, minutes, seconds = time_str.split(':')
        seconds, milliseconds = seconds.split('.')
        return int(int(hours) * 3600000 + int(minutes) * 60000 + int(seconds) * 1000 + int(milliseconds))

    # Read timecodes from the generated file
    segments = []
    with open(output_txt_path, 'r') as f:
        for line in f:
            if '-->' in line:
                timecodes, speaker = line.split(']')
                timecodes = timecodes.strip()[1:]
                start_time, end_time = timecodes.split(' --> ')
                speaker = speaker.strip()
                segments.append((start_time, end_time, speaker))

    # Create directory to save the segments
    output_dir = os.path.join(os.path.dirname(audio_file), filename)
    os.makedirs(output_dir, exist_ok=True)

    # Load the original audio
    audio = AudioSegment.from_wav(audio_file)

    # Split the audio into segments based on timecodes
    for start_time, end_time, speaker in segments:
        start_ms = parse_time_to_ms(start_time)
        end_ms = parse_time_to_ms(end_time)
        segment_duration = end_ms - start_ms

        # Skip segments shorter than 2 seconds
        if segment_duration < 2000:
            print(f"Segment {speaker} {start_time} --> {end_time} skipped (too short).")
            continue

        segment = audio[start_ms:end_ms]
        speaker_number = speaker.split()[-1]

        # Format time for the filename
        start_time_formatted = start_time.replace(':', '').replace('.', '_')
        end_time_formatted = end_time.replace(':', '').replace('.', '_')

        # Create the output filename
        output_filename = f"{speaker_number}_{start_time_formatted}_{end_time_formatted}.wav".replace(" ", "")
        output_file = os.path.join(output_dir, output_filename)

        segment.export(output_file, format="wav")
        print(f"Segment saved: {output_file}")

    print("Audio segmentation completed.")


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Diarize and segment an audio file.")
    parser.add_argument("audio_path", type=str, help="Path to the audio file for processing")

    args = parser.parse_args()

    # Run the diarization and segmentation function with the provided audio file
    diarize_and_segment(args.audio_path)
