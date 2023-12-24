import os
import argparse
import subprocess

from text_to_speech import merge_mp3_files, MP3Generator

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='input file path')
    parser.add_argument('-o', '--output_path', type=str, help='output file path', default=None)
    args = parser.parse_args()
    if not os.path.isfile(args.input_file):
        print(f'Input file {args.input_file} does not exist.')
        exit(1)

    out_path = args.output_path or os.path.dirname(args.input_file)
    command = f'nougat "{args.input_file}" -o "{out_path}" -m 0.1.0-base'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if process.returncode != 0:
        print(error.decode())
        exit(1)

    mp3_gen = MP3Generator(os.path.join(out_path, os.path.basename(args.input_file).replace('.pdf', '.mmd')))
    mp3_files = mp3_gen.generate_mp3_files()
    merge_mp3_files(out_path, mp3_files)
