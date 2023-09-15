import os
import sys

from text_to_speech import generate_mp3_files, merge_mp3_files

if __name__ == '__main__':
    input_pdf = sys.argv[1] if len(sys.argv) > 1 else '<YOUR_DEFAULT_PATH>'
    out_path = os.path.dirname(input_pdf)
    os.system('nougat {} -o {}'.format(input_pdf, out_path))

    mp3_list = generate_mp3_files(input_pdf.replace('.pdf', '.mmd'))
    merge_mp3_files(out_path, mp3_list)
