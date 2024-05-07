# TODO Check why this happens: "No language specified, language will be first be detected for each audio file (increases inference time)."
import os
import sys
import argparse
import yaml
import ffmpeg
import whisperx

# Global constants
CONFIG_FILE_NAME = "config.yml" # filename for configuration
PLACEHOLDER_HF_TOKEN = "PutYourHuggingFaceUserAccessTokenHere"
WHISPER_MODEL_SIZES = ["tiny", "base", "small", "medium", "large"]

# Whisper configuration TODO move to config.yml?
MODEL_DIRECTORY = "whisper-model/" # directory to download/save whisper model
DEVICE = "cpu" # change to "cuda" if high on GPU
BATCH_SIZE = 8 # set to 16 if high on GPU mem
COMPUTE_TYPE = "int8" # change to "float16" if high on GPU mem (also increases accuracy)

def load_config():
    """
    Load configuarion from config.yml

    Args:
        configuration_file_path: file path without file name

    Returns:
        config: Dict with keys
        or
        False: if config.yml does not exist
    """
    configuration_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_FILE_NAME)

    if os.path.exists(configuration_file_path):
        with open(CONFIG_FILE_NAME, "rt") as config_file:
            config = yaml.load(config_file, Loader=yaml.Loader)
        return(config)
    else:
        return False

def is_wav_file(file_path):
    """
    Check if file_path has the extension .wav

    Args:
        file_path: a valid file path

    Returns:
        Boolean
    """
    # get the file extension
    _, extension = os.path.splitext(file_path)
    # check if the extension is '.wav'
    return extension.lower() == '.wav'

def convert_to_wav(input_file, output_file):
    """
    Converts input_file to .wav using ffmpeg, prints an error if conversion not possible
    """
    print(f"Converting {input_file} to {output_file}")
    try:
        # Stream audio to wav format, suppress output of ffmpeg
        ffmpeg.input(input_file).output(output_file, format='wav').run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        print(f"Converted {input_file} to {output_file}.")
        return True
    except ffmpeg.Error as e:
        print("Error:", e.stderr.decode())
        # TODO actual error handling?, e.g. sys.exit(1)
        return False

def convert_to_string(value, default="{None}"):
    """
    Converts value to a string, using a default if None is encountered.
    """
    return str(value) if value is not None else default

def save_result(result, file_name):
    """
    Output a diarized whisper result to a human-readable .txt file

    Args:
        result: dict - result from Whisper X
        file: filename - a filename where to save the results
    """
    # delete, if file exists already
    if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Existing file {file_name} was deleted")

    # initiate variables
    currentspeaker = ""
    currenttext = ""
    # write results to file, seperating speaker and spoken words
    with open(file_name, 'a') as file:
        # iterate through all segments within result
        for i in result.get("segments"):
            speaker = i.get("speaker")
            if currentspeaker == speaker:
                # append text to previous text
                currenttext = currenttext + " " + i.get("text")
            else:
                # output previous speaker and text, make sure we're using strings
                file.write(convert_to_string(currentspeaker) + "\n" + convert_to_string(currenttext) + "\n\n")
                # set to new speaker and text
                currentspeaker = i.get("speaker")
                currenttext = i.get("text")
        file.flush() # make sure, all changes are written to the file
    print(f"Result written to {file_name}")

def transcribe_and_diarize(audio_file, spoken_language, min_speakers, max_speakers, auth_token, model_size):
    """
    Runs a Whisper pipeline to transcribe audio and identidy speakers (diarization)

    Args:
        audio_file: str - an audio file in .wav format
        spoken_language: str - language code, e.g. "de" or "en"
        min_speakers: int - minimum number of speakers
        max_speakers: int - maximum number of speakers
        auth_token: str - a valid Hugging Face User Access token
        model_size: str - model size for Whisper, e.g. "small", "base" or "medium"

    Returns:
        result: dict - whisper results with speaker identification
    """
    # Transcribe with original whisper (batched) and save model to local path
    print(f"Transcribing {audio_file} ...")
    whisperx_model = whisperx.load_model(model_size, DEVICE, compute_type=COMPUTE_TYPE, download_root=MODEL_DIRECTORY)
    audio = whisperx.load_audio(audio_file)
    result = whisperx_model.transcribe(audio, batch_size=BATCH_SIZE, language=spoken_language, print_progress=False)
    # DEBUG result = model.transcribe(audio, batch_size=BATCH_SIZE, language="German", print_progress=False)

    # Align whisper output
    print(f"Aligning output for {audio_file} ...")
    whisperx_model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=DEVICE)
    result = whisperx.align(result["segments"], whisperx_model_a, metadata, audio, DEVICE, return_char_alignments=False)

    # Assign speaker labels
    print(f"Assigning speaker labels in {audio_file} ...")
    diarize_model = whisperx.DiarizationPipeline(use_auth_token=auth_token, device=DEVICE)
    diarize_segments = diarize_model(audio, min_speakers=min_speakers, max_speakers=max_speakers)
    result = whisperx.assign_word_speakers(diarize_segments, result)
    print(f"Finished transcribing {audio_file}")

    return result

def process_file(file_path, language, min_speaker, max_speaker, auth_token, model_size):
    """
    Transcribes an audio/video file using an LLM and assigns speaker labels

    Args:
        file_path: str - an audio or video file
        language: str - default "de", others languages possible
        min_speaker: int - number of minumum speakers expected in the file
        max_speaker: int - number of maximum speakers expected in the file
        auth_token: str - a HF-token, used to download the LLM
    """
    # convert to .wav if necessary
    successfulconversion = True
    if not is_wav_file(file_path):
        converted_file_path = file_path + ".wav"
        successfulconversion = convert_to_wav(file_path, converted_file_path)
        file_path = converted_file_path # cheeky: re-use previous file_path with converted filename
    if successfulconversion:
        # process file
        print(f"Processing {file_path} ...")
        # DEBUG print(f"DEBUG Language: {language}, Min Speakers: {min_speaker}, Max Speakers: {max_speaker}, Model Size: {model_size}")
        result = transcribe_and_diarize(file_path, language, min_speaker, max_speaker, auth_token, model_size)
        # append .txt to existing filename
        result_file_path = file_path + ".txt"
        # save result in human-readable format
        save_result(result, result_file_path)
    else:
        print(f"Skipping {file_path} - conversion to .wav not possible with ffmpeg")


def parse_args():
    """
    Parses commandline arguments

    Returns:
        args.language: str - Language spoken in all files
        args.min_speaker: int - Minimum number of speakers
        args.max_speaker: int - Maximum number of speakers
    """
    parser = argparse.ArgumentParser(description="Convert audio or video to a human-readable transcript using a local LLM (Whisper).")
    parser.add_argument("path", help="Path to audio/video file or directory to transcribe")
    parser.add_argument("--language", help="Language spoken in all files", default="de")
    parser.add_argument("--min_speaker", help="Minimum number of speakers", type=int, default=1)
    parser.add_argument("--max_speaker", help="Maximum number of speakers", type=int, default=2)
    return parser.parse_args()

def main():
    """
    Transcribes audio/video files passed via command-line to .txt with speaker identification.
    """
    args = parse_args()

    # load config from .yml
    config = load_config()
    if not config:
        sys.exit(f"Error: Configuration file {CONFIG_FILE_NAME} missing or unreadable.")
    hf_token = config.get("hf_token")
    model_size = config.get("model_size")

    # check if Hugging Face token is not the placeholder
    if (not hf_token) or (hf_token == PLACEHOLDER_HF_TOKEN):
        print(f"Error: No valid hf_token in {CONFIG_FILE_NAME} -- please add a valid Hugging Face User Access Token.")
        sys.exit(1)

    # check for valid model size
    if not model_size in WHISPER_MODEL_SIZES:
        print(f"Error: No valid model_size in {CONFIG_FILE_NAME} -- please use one of {WHISPER_MODEL_SIZES}.")
        sys.exit(1)

    # process single file
    if os.path.isfile(args.path):
        process_file(args.path, args.language, args.min_speaker, args.max_speaker, hf_token, model_size)
    # process all files within given directory
    elif os.path.isdir(args.path):
        for filename in os.listdir(args.path):
            full_path = os.path.join(args.path, filename)
            if os.path.isfile(full_path):
                process_file(full_path, args.language, args.min_speaker, args.max_speaker, hf_token, model_size)
    else:
        print(f"Error: The provided file/path does not exist: {args.path}")
        sys.exit(1)

if __name__ == "__main__":
    main()
