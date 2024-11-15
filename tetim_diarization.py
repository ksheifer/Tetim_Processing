import torch
import time
from pyannote.audio.pipelines import SpeakerDiarization
from pyannote.core import Annotation
from pydub import AudioSegment
import os
import sys
import argparse

def diarize_and_segment(audio_file, min_segment_length=3000, min_pause_duration=100):
    """
    Perform speaker diarization on the provided audio file and split it into segments.
    """
    # Start measuring the total execution time
    total_start_time = time.time()

    # Check if GPU is available
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Using device: {device}")

    # Load the speaker diarization model
    pipeline = SpeakerDiarization.from_pretrained("pyannote/speaker-diarization")
    pipeline.to(device)

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

    # Merge segments based on min_pause_duration
    merged_segments = []
    for i, (start_time, end_time, speaker) in enumerate(segments):
        start_ms = parse_time_to_ms(start_time)
        end_ms = parse_time_to_ms(end_time)

        if i == 0:
            merged_segments.append((start_ms, end_ms, speaker))
            continue

        prev_start, prev_end, prev_speaker = merged_segments[-1]
        # Merge segments if the pause between them is shorter than the specified minimum pause duration
        if start_ms - prev_end < min_pause_duration:
            merged_segments[-1] = (prev_start, end_ms, prev_speaker)
        else:
            merged_segments.append((start_ms, end_ms, speaker))

    # Create a directory to save the segments
    output_dir = os.path.join(os.path.dirname(audio_file), filename)
    os.makedirs(output_dir, exist_ok=True)

    # Load the original audio
    audio = AudioSegment.from_wav(audio_file)

    # Split the audio into segments based on the timecodes
    for start_ms, end_ms, speaker in merged_segments:
        segment_duration = end_ms - start_ms

        # Skip segments shorter than the specified minimum segment length
        if segment_duration < min_segment_length:
            print(f"Segment {speaker} {start_ms} --> {end_ms} skipped (too short).")
            continue

        segment = audio[start_ms:end_ms]
        speaker_number = speaker.split()[-1]

        # Format time for the filename
        start_time_formatted = f"{start_ms // 3600000:02}:{(start_ms // 60000) % 60:02}:{(start_ms // 1000) % 60:02}_{start_ms % 1000:03}"
        end_time_formatted = f"{end_ms // 3600000:02}:{(end_ms // 60000) % 60:02}:{(end_ms // 1000) % 60:02}_{end_ms % 1000:03}"

        # Create the output filename
        output_filename = f"{speaker_number}_{start_time_formatted}_{end_time_formatted}.wav".replace(" ", "")
        output_file = os.path.join(output_dir, output_filename)

        # Save the segmented audio to a file
        segment.export(output_file, format="wav")
        print(f"Segment saved: {output_file}")

    print("Audio segmentation completed.")

    # End measuring the total execution time and print the result
    total_end_time = time.time()
    elapsed_time = total_end_time - total_start_time
    minutes, seconds = divmod(int(elapsed_time), 60)
    print(f"Total processing time: {minutes} minutes {seconds} seconds")


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Diarize and segment an audio file.")
    parser.add_argument("audio_path", type=str, help="Path to the audio file for processing")
    parser.add_argument("--min_segment_length", type=int, default=3000, help="Minimum segment length in milliseconds")
    parser.add_argument("--min_pause_duration", type=int, default=100, help="Minimum pause duration in milliseconds")

    args = parser.parse_args()

    # Run the diarization and segmentation function with the provided audio file
    diarize_and_segment(args.audio_path, args.min_segment_length, args.min_pause_duration)
