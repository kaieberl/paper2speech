import os
import argparse

from text_to_speech import generate_mp3_files, merge_mp3_files


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='input file path')
    parser.add_argument('-o', '--output_path', type=str, help='output file path', default=None)
    args = parser.parse_args()

    out_path = args.output_path or os.path.dirname(args.input_file)
    os.system('nougat {} -o {}'.format(args.input_file, out_path))

    mp3_list = generate_mp3_files(os.path.join(out_path, os.path.basename(args.input_file).replace('.pdf', '.mmd')))
    merge_mp3_files(out_path, mp3_list)
