import os
import argparse

from text_to_speech import generate_mp3_files, merge_mp3_files


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='input file path')
    parser.add_argument('-o', '--output_path', type=str, help='output file path')
    args = parser.parse_args()

    out_path = os.path.dirname(args.output_path)
    os.system('nougat {} -o {}'.format(args.input_file, out_path))

    mp3_list = generate_mp3_files(args.input_file.replace('.pdf', '.mmd'))
    merge_mp3_files(out_path, mp3_list)
