# localtranscribe.py

## About

Performs local speech to text transcription and speaker identification of audio and video files.

## Getting Started

This script has been tested on Mac OS 14.4.1 (23E224). Your milage on Windows or another OS might vary.

### Prerequisites

These instructions are for usage on Mac OS:

- Download and install Python from https://www.python.org/downloads/
- Install Homebrew, see https://brew.sh/
- Open a Termin and install ffmpeg with the following command:
  ```sh
  brew install ffmpeg
  ```

### Installation

- Download this repository and extract it to a folder of you choice. You should see these files:
  - `config.yml`
  - `localtranscribe.py`
- In the terminal change to the directory, create a Python environment and activate it:
  ```sh
  cd local/path/to/this/repository
  python3 -m venv pvenv
  source pvenv/bin/activate
  ```
- Install a couple of necessary Python modules within the environment:
  ```sh
  pip install pyyaml
  pip install ffmpeg-python
  pip install git+https://github.com/m-bain/whisperx.git
  ```
- TODO! HF-Token

## Usage

Put your audio and or video files into a directory and run the following command within the activated Python environment:

```sh
python localtranscribe.py your/audio/or/video/file/or/folder
```

This will run the script and create a .txt file for the provided file file or run for the complete directory.

TODO! On the first run it will download a LLM, requires a couple of free gigabytes

- TODO! typical output and progress should look like this
  ```sh
  (pvenv) user@mbp locatranscribe % python localtranscribe short.wav
  Processing short.wav ...
  Transcribing short.wav ...
  Aligning output for short.wav ...
  Assigning speaker labels in short.wav ...
  Finished transcribing short.wav
  Result written to short.wav.txt
  (pvenv) user@mbp locatranscribe %
  ```

### Command line arguments

The script takes the following command line arguments:

- `--language` TODO
- `--max_speaker` TODO
- `--min_speaker` TODO

## Trouble Shooting

TODO! Ignore warnings, e.g.

- "UserWarning: torchaudio.\_backend.set_audio_backend has been deprecated. With dispatcher enabled, this function is no-op. You can remove the function call.
  torchaudio.set_audio_backend("soundfile")
  torchvision is not available - cannot save figures"
- Model was trained with pyannote.audio 0.0.1, yours is 3.1.1. Bad things might happen unless you revert pyannote.audio to 0.x.
- Model was trained with torch 1.10.0+cu102, yours is 2.3.0. Bad things might happen unless you revert torch to 1.x.

## Acknowledgments

- [WhisperX](https://github.com/m-bain/whisperX)
