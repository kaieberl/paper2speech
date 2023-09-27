import os
import argparse

from text_to_speech import merge_mp3_files, MP3Generator

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='input file path')
    parser.add_argument('-o', '--output_path', type=str, help='output file path', default=None)
    args = parser.parse_args()

    out_path = args.output_path or os.path.dirname(args.input_file)
    os.system('nougat "{}" -o "{}" -m 0.1.0-base'.format(args.input_file, out_path))

    mp3_gen = MP3Generator(os.path.join(out_path, os.path.basename(args.input_file).replace('.pdf', '.mmd')))
    mp3_files = mp3_gen.generate_mp3_files()
    merge_mp3_files(out_path, mp3_files)
