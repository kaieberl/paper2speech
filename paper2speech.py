import os
import argparse
import subprocess

from src.text_to_speech import merge_mp3_files, MP3Generator, refine_mmd
from src.convert import mmd_to_tex, tex_to_html, process_html


def get_args():
    """Parse arguments and check validity."""
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='input file path. Can be a pdf, mmd or tex file.')
    parser.add_argument('-o', '--output_file', type=str, help='output file path. Either an mp3 or html file.')
    args = parser.parse_args()
    assert os.path.isfile(args.input_file), f'Input file {args.input_file} does not exist.'
    return args


def main():
    args = get_args()

    filename, file_extension = os.path.splitext(args.input_file)
    assert file_extension.lower() in ['.pdf', '.mmd', '.tex'], f'Input file type {file_extension} not supported.'
    filename = os.path.basename(filename)
    _, file_type = os.path.splitext(args.output_file)
    assert file_type.lower() in ['.mp3', '.html'], f'Output file type {file_type} not supported.'
    in_path = os.path.dirname(args.input_file)
    out_path = os.path.dirname(args.output_file)
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    if file_extension.lower() == '.pdf':
        command = f'nougat "{args.input_file}" -o "{in_path}" -m 0.1.0-base --no-skipping'
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if process.returncode != 0:
            print(error.decode())
            exit(1)

    if file_type == '.mp3':
        # TODO: implement conversion from tex to mp3
        mp3_gen = MP3Generator(os.path.join(out_path, filename + '.mmd'))
        mp3_files = mp3_gen.generate_mp3_files()
        merge_mp3_files(out_path, mp3_files)
    else:
        if file_extension.lower() != '.tex':
            refine_mmd(os.path.join(in_path, filename + '.mmd'))
            mmd_to_tex(os.path.join(in_path, filename + '.mmd'))
            tex_to_html(os.path.join(in_path, filename, filename + '.tex'), out_path)
        else:
            tex_to_html(args.input_file, out_path)
        process_html(args.output_file)
        os.system(f'open "{args.output_file}"')


if __name__ == "__main__":
    main()
