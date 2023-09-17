# Paper2Speech

## Motivation
As a student in applied mathematics / machine learning, I often get to read scientific books, lecture notes and papers.
Usually I prefer listening to a lecture from the professor and following his visual explanations on the blackboard, because then I get much information through the ear and don't have to do the "heavy lifting" through reading only.
So far, this has not been available for books and papers.  
So I thought: Why not let a software read out the text for you?
What if you just had to click a button in the Finder, and the book or paper is converted to speech automatically?  
This script uses the Meta [Nougat](https://facebookresearch.github.io/nougat/) package to extract formatted text from pdf and then converts it to audio using the [Google Cloud Text to Speech API](https://cloud.google.com/text-to-speech?hl=de).

## Features
- pause before and after headings
- skip references like \[1\], \[1, 2\], \[1-3\]
- spell out abbreviations like e.g., i.e., w.r.t., Fig., Eq.
- read out inline math
- do not read out block math, instead pause
- do not read out table contents
- read out figure, table captions

## Usage
```bash
pip3 install -r requirements.txt
```
```bash
python3 main.py <input_file> -o <output_path>
```

On macOS, you can create a shortcut in the Finder with the following steps:
- in Automator, create a new Quick Action. At the top, choose input as "PDF files" in "Finder".
- add a "Run Shell Script" action. Set shell to /bin/zsh and pass input as arguments.
- add the following code:
```bash
source ~/opt/miniconda3/etc/profile.d/conda.sh
conda activate paper2audio
python3 ~/path/to/paper2speech/main.py $1
```
- save the action and give it a name, e.g. "Paper2Speech"

## Limitations
- captions of tables, figures are always read at the end
- only works for English

## Future Work
- read out figure caption after referenced in text
