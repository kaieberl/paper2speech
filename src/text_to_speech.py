import os
import re
import tempfile

from google.cloud import texttospeech

from src import MarkdownModel
from src.replacements import text_replacements

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(PROJECT_DIR, "texttospeech.json")

speech_client = texttospeech.TextToSpeechClient()


def apply_text_rules(text: str) -> str:
    """make replacements defined in replacements.py"""
    for pattern, replacement in text_replacements:
        text = re.sub(pattern, replacement, text)
    return text


class MP3Generator:
    def __init__(self, md_filename):
        self.md_filename = md_filename
        self.mp3_file_list = []
        self.temp_path = tempfile.gettempdir()
        self.title_flag = True
        self.table_flag = False

    def generate_mp3_files(self):
        with open(self.md_filename, "r") as md_file:
            mm = MarkdownModel()
            mm.markdown_to_html(md_file.read())

            for id, chunk in enumerate(mm.get_chunk()):
                filename = f'{os.path.basename(self.md_filename)[:-4]}-{id}.mp3'
                mp3_file = generate_mp3_for_ssml(self.temp_path, filename, chunk)
                self.mp3_file_list.append(mp3_file)

        return self.mp3_file_list


def generate_mp3_for_ssml(out_path, filename, ssml):
    print("Started generating speech for {}".format(filename))
    # set text and configs
    ssml = "<speak>\n" + ssml + "</speak>\n"
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml)
    voice = texttospeech.VoiceSelectionParams(
        language_code='en-GB',
        name='en-GB-Neural2-B',
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0,
    )

    # generate speech
    try:
        response = speech_client.synthesize_speech(
            request={"input": synthesis_input, "voice": voice, "audio_config": audio_config}
        )
    except Exception as e:
        print("Retrying speech generation with WaveNet...")
        voice = texttospeech.VoiceSelectionParams(
            language_code='en-GB',
            name='en-GB-Wavenet-B',
        )
        response = speech_client.synthesize_speech(
            request={"input": synthesis_input, "voice": voice, "audio_config": audio_config}
        )

    # save a MP3 file and delete the text file
    with open(os.path.join(out_path, filename), "wb") as out:
        out.write(response.audio_content)
    print("MP3 file saved: {}".format(filename))
    return os.path.join(out_path, filename)


def merge_mp3_files(out_path, mp3_file_list):

    # merge saved mp3 files
    print("Started merging mp3 files...")

    # save the merged mp3 file
    merged_mp3_file_name = (
        re.sub("-[0-9]+.mp3", ".mp3", os.path.basename(mp3_file_list[0]))
    )  # 'foo-101' -> 'foo.mp3'
    with open(os.path.join(out_path, merged_mp3_file_name), "wb") as out:
        for mp3_file in mp3_file_list:
            with open(mp3_file, "rb") as mp3:
                out.write(mp3.read())

    # delete mp3 files
    for mp3_file in mp3_file_list:
        os.remove(mp3_file)
    print("Ended merging mp3 files: {}".format(merged_mp3_file_name))


def refine_mmd(mmd_file):
    """
    Replace \mathds and \mathbbm by \mathbb for conversion to html with mathpix-markdown-it
    Args:
        mmd_file: full path to the markdown file

    Returns:
        None
    """
    with open(mmd_file, "r") as file:
        mmd = file.read()

    # remove comments
    mmd = re.sub(r"\\mathds\{", r"\\mathbb{", mmd)
    mmd = re.sub(r"\\mathbbm\{", r"\\mathbb{", mmd)

    with open(mmd_file, "w") as file:
        file.write(mmd)
