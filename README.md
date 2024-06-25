# localwhisperx.py

## About

Performs local speech to text transcription and speaker identification of audio and video files.

Especially useful for transcription of user interviews where confidentially might be an issue or where data privacy is needed. No data leaves your computer, everything runs locally.

Transcription will take pretty long compared to what you might be used to, since this script does not use any GPU optimization.

On a 2023 Mac M3 Pro this script runs roughly in real-time, meaning one minute of audio will take about one minute. Identifying speakers takes most of this time.

For many or large files it might be best to run this tool over night.

## Getting Started

This script has been tested on Mac OS 14.4.1 (23E224). Your milage on Windows or another OS might vary.

### Prerequisites

These instructions are for usage on Mac OS:

- Download and install Python from https://www.python.org/downloads/
- Open a Terminal and install Homebrew, see https://brew.sh/
- In the open Terminal install [FFmpeg](https://ffmpeg.org/) with the following command:
  ```sh
  brew install ffmpeg
  ```
- If you haven't already, create an account on [Hugging Face](https://huggingface.co/join)
  - Note! This is only used to download a model from Hugging Face, no training or other data will leave your computer.
- Log in to Hugging Face and accept the following user conditions:
  - https://huggingface.co/pyannote/segmentation-3.0
  - https://huggingface.co/pyannote/speaker-diarization-3.1

### Installation

- Download this repository and extract it to a folder of you choice. You should see these files:
  - `config.yml`
  - `localwhisperx.py`
- Install these necessary Python modules:
  ```sh
  pip3 install pyyaml
  pip3 install ffmpeg-python
  pip3 install git+https://github.com/m-bain/whisperx.git
  ```
- Open `config.yml` with your favourite Editor, e.g. TextEdit and add your [Huggin Face User Access Token](https://huggingface.co/settings/tokens) in the appropriate line

## Usage

- Put your audio and/or video files into a directory and open a Terminal.
- In the open Terminal change to the directory, where you extracted this repository:
  ```sh
  cd path/to/unzipped/localwhisperx
  ```
- Transcribe your files with the following command
  ```sh
  python3 localwhisperx.py your/audio/or/video/file/or/folder
  ```
  This will run the script and create a .txt file for the provided file or all files within the given directory.

On the first run the program will download a local copy of a large language model (LLM) which requires a couple of free gigabytes.

### Command line arguments

The script can take a couple of command line arguments to refine your transcription:

- `--language` Language spoken in all files, e.g. `en`; default is `de`
- `--minspeaker` Minimum number of speakers; default is `1`
- `--maxspeaker` Minimum number of speakers; default is `2`

Here's a example, converting an english language audio file with exactly 4 speakers:

```sh
python3 localwhisperx.py test.mp3 --language en --minspeaker 4 --maxspeaker 4
```

### Selecting a model size

The file `config.yml` contains a line to change the LLM-model size. A larger model will generally result in a more accurate transcription. Likewise processing time will increase.

You can select one of the follwing options:

- `tiny`
- `base`
- `small`
- `medium` (default, recommended compromise of accuracy and processing time, takes about 1.5 GB of space on your harddisk)
- `large`

## Trouble Shooting

The tool might show a couple of warnings -- it is safe to ignore these:

```sh
UserWarning: torchaudio.\_backend.set_audio_backend has been deprecated. With dispatcher enabled, this function is no-op. You can remove the function call.
torchaudio.set_audio_backend("soundfile")
torchvision is not available - cannot save figures
Model was trained with pyannote.audio 0.0.1, yours is 3.1.1. Bad things might happen unless you revert pyannote.audio to 0.x.
Model was trained with torch 1.10.0+cu102, yours is 2.3.0. Bad things might happen unless you revert torch to 1.x.
```

## Next steps

If you're transcribing interviews put the resulting transcriptions into [ChatGPT](https://chatgpt.com/auth/login). Maybe try using the [Interview Analyst GPT](https://chatgpt.com/g/g-bTO2IaM1V-interview-analyst) and see what a quick analysis will result in.

## Acknowledgments

- [WhisperX](https://github.com/m-bain/whisperX)
- [FFmpeg](https://ffmpeg.org/)
