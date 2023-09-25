import os
import re
import tempfile

from google.cloud import texttospeech
from replacements import text_rules, math_rules

# break length
SECTION_BREAK = 2  # sec
CAPTION_BREAK = 1.5  # sec

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(PROJECT_DIR, "texttospeech.json")

speech_client = texttospeech.TextToSpeechClient()


def replace_nested(expr, rules):
    """
    Recursively replace LaTeX using the provided rules.
    """
    changed = True
    while changed:
        changed = False
        for pattern, replacement in rules:
            try:
                new_expr, replacements_made = re.subn(pattern, replacement, expr)
                if replacements_made > 0:
                    changed = True
                    expr = new_expr
            except re.error as e:
                print(f"Invalid pattern: {pattern}. Error: {e}")
    return expr


def process_ssml(ssml, rules):
    # Continue replacing as long as there are matches
    while re.search(r"\\\((.*?)\\\)", ssml):
        ssml = re.sub(r"\\\((.*?)\\\)", lambda match: replace_nested(match.group(1), rules), ssml)
    return ssml


def generate_mp3_files(md_filename: str):

    # generate speech for each <4500 chars
    ssml = ""
    section_break = '<break time="{}s"/>'.format(SECTION_BREAK)
    caption_break = '<break time="{}s"/>'.format(CAPTION_BREAK)
    mp3_file_list = []
    temp_path = tempfile.gettempdir()
    title_flag = True
    table_flag = False
    with open(md_filename, "r") as md_file:
        for id, line in enumerate(md_file.readlines()):
            # remove URLs
            line = re.sub("https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", "", line)

            # remove reference numbers, e.g. [1], (2, 3), [1-3] including preceding spaces
            line = re.sub(r"\s*(\[[0-9,-, ]+\]|\([0-9,-, ]+\))\s*", '', line)
            # remove citations in square brackets, e.g. [Feynman et al., 1965], [Martius and Lampert, 2016], [Zaremba et al., 2014, Kusner et al., 2017, Li et al., 2019, Lample and Charton, 2020]
            line = re.sub(r'\s*\[[^\]]*, \d{4}(?:, [^\]]*, \d{4})*\]', '', line)
            # remove citations in round brackets, e.g. (Welinder et al., 2010), (Kingma and Ba, 2014), (Reed et al., 2016a; Li et al., 2019; Koh et al., 2021),
            # (Zaremba et al., 2014, Kusner et al., 2017, Li et al., 2019, Lample and Charton, 2020), (Zhang et al., 2017; 2018)
            line = re.sub(r'\s*\([^\)]*, \d{4}(?:[;,] [^\)]*, \d{4}[a-zA-Z]*?)*\)', '', line)
            # remove year in embedded citations with et al., e.g. Nguyen et al. (2017), Garc ́ıa et al. [1989]
            line = re.sub(r'\s*(\b\w+\s+et al\.) (\[\d{4}\]|\(\d{4}\))', r'\1', line)
            # remove Markdown syntax
            line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)  # bold
            line = re.sub(r"_(.*?)_", r"\1", line)  # italic
            # remove * bullet points
            line = re.sub(r"^\* ", "", line)

            # make replacements defined in replacements.py
            for pattern, replacement in text_rules:
                line = re.sub(pattern, replacement, line)

            # split as chunks with <4500 bytes each
            if len(ssml.encode("utf-8")) + len(line.encode("utf-8")) > 4500:
                filename = f'{os.path.basename(md_filename)[:4]}-{id}.mp3'
                mp3_file = generate_mp3_for_ssml(temp_path, filename, ssml)
                mp3_file_list.append(mp3_file)
                ssml = ""

            # set flag for text between title and abstract
            if title_flag and not id == 0:
                # disable if line is longer than 200 chars
                if "# Abstract" in line or len(line) > 200:
                    title_flag = False
                else:
                    continue

            # add SSML tags
            inline_footnote = re.match(r"^(.*)Footnote [0-9]+:.*", line)
            inline_header = re.match(r"\*\*(.*?)\*\*\s*([A-Z])", line)
            if re.match(r"^#{1,6} .*", line):
                line = re.sub(r"^#{1,6} ", "", line)
                ssml += section_break + "<p>" + line + "</p>" + section_break + "\n"
            elif inline_header:
                ssml += section_break + "<p>" + inline_header.group(1) + "</p>" + section_break + "\n"
                ssml += "<p>" + inline_header.group(2) + "</p>\n"
            # remove table environment
            elif re.match(r"^\\begin{table}", line):
                table_flag = True
                continue
            elif re.match(r"^\\end{table}", line):
                table_flag = False
                continue
            elif table_flag:
                continue
            # caption
            elif re.match(r"^Figure [0-9]+:", line) or re.match(r"^Table [0-9]+:", line):
                ssml += caption_break + line + caption_break + "\n"
            # footnote in the middle of a paragraph
            elif inline_footnote:
                ssml += inline_footnote.group(1) + "\n"
            # equation block
            elif re.match(r"^\\\[.*\\\]", line):
                ssml += section_break
            # normal paragraph
            else:
                ssml += "<p>" + line + "</p>\n"

            # spell out latex math within \( \) and remove \( \)
            if re.search(r"\\\((.*)\\\)", ssml):
                ssml = process_ssml(ssml, math_rules)

        # generate speech for the remaining
        if ssml:
            filename = f'{os.path.basename(md_filename)}-{id}.mp3'
            mp3_file = generate_mp3_for_ssml(temp_path, filename, ssml)
            mp3_file_list.append(mp3_file)
    return mp3_file_list


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
