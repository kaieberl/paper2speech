# Paper2Speech

> [!TIP]
> ArXiv now features html versions for new papers, see [here](https://info.arxiv.org/about/accessible_HTML.html). I am currently working on a browser add-on that adds buttons directly to the website. You can also convert the TeX sources to html yourself using [latexml](https://github.com/brucemiller/LaTeXML). The `latexml` folder provided in this repository is a copy from [engrafo](https://github.com/arxiv-vanity/engrafo).
> ```bash
> latexmlc --dest out.html main.tex --nographicimages --format html5 --nodefaultresources --mathtex --svg --verbose --timestamp 0 --path latexml/packages/ --preload latexml/engrafo.ltxml --preload /opt/local/lib/perl5/vendor_perl/5.34/LaTeXML/Package/hyperref.sty.ltxml --xsltparameter SIMPLIFY_HTML:true
> ```

## Motivation
As a student in applied mathematics / machine learning, I often get to read scientific books, lecture notes and papers.
Usually I prefer listening to a lecture from the professor and following his visual explanations on the blackboard, because then I get much information through the ear and don't have to do the "heavy lifting" through reading only.
So far, this has not been available for books and papers.  
So I thought: Why not let a software read out the text for you?
What if you just had to click a button in the Finder, and the book or paper is converted to speech automatically?  
This script uses the Meta [Nougat](https://facebookresearch.github.io/nougat/) package to extract formatted text from pdf and then converts it to audio using the [Google Cloud Text to Speech API](https://cloud.google.com/text-to-speech?hl=de).

Sample output for the paper [Large Language Models for Compiler Optimization](https://arxiv.org/abs/2309.07062):  
[output audio](https://github.com/kaieberl/paper2speech/blob/main/Large%20Language%20Models%20for%20Compiler%20Optimization.mp4)  
<img src="https://github.com/kaieberl/paper2speech/blob/main/Large%20Language%20Models%20for%20Compiler%20Optimization.jpg" width="500">

## Features
- pause before and after headings
- skip references like \[1\], \(1, 2)], \[Feynman et al., 1965\], \[AAKA23, SKNM23\]
- spell out abbreviations like e.g., i.e., w.r.t., Fig., Eq.
- read out inline math (work in progress)
- do not read out block math, instead pause
- do not read out table contents
- read out figure, table captions

## Usage
Replace the `GEMMA_CPP_PATH` variable in `src/markdown_to_html.py` with the build path of your gemma executable. The tokenizer and model weights should be in the same directory.
```bash
git clone git://github.com/kaieberl/paper2speech
pip install .
```
```bash
paper2speech <input_file.pdf> -o <output_path>
```
Alternatively, you can pass in an MMD (Mathpix Markdown) file directly:
```bash
paper2speech <input_file.mmd> -o <output_path>
```

The Google cloud authentication json file should be in the `src` directory. It can be downloaded from the Google Cloud Console, as described [here](https://cloud.google.com/api-keys/docs/create-manage-api-keys).  
TLDR: On [https://cloud.google.com](https://cloud.google.com), create a new project. In your project, in the upper right corner, click on the 3 dots > project settings > service accounts > choose one or create service account > create key > json > create.
The resulting json file should be downloaded automatically.
Google TTS Neural2 and Wavenet voices are free for the first 1 million characters per month, after that $16 per 1M characters for the Neural2 voices and $4 per 1M characters for the Wavenet voices.

You can customize the voice in the definition of the `voice` variable.
```python3
voice = texttospeech.VoiceSelectionParams(
    language_code='en-GB',
    name='en-GB-Neural2-B',
)
```
Go to [https://cloud.google.com/text-to-speech](https://cloud.google.com/text-to-speech) to try out different voices and languages. Below the text box, there is a button to show the json request.
E.g. to use an American english voice, replace `'en': ('en-GB', 'en-GB-Neural2-B'),` by `'en': ('en-US', 'en-US-Neural2-J'),`.
Also change the fallback Wavenet voice to the same voice a few lines further down:
```python3
voice = texttospeech.VoiceSelectionParams(
    language_code='en-GB',
    name='en-GB-Wavenet-B',
)
```
This voice is used if the Neural voice returns an error, e.g. because a sentence is too long.

On macOS, you can create a shortcut in the Finder with the following steps:
1. in Automator, create a new Quick Action. 
2. At the top, choose input as "PDF files" in "Finder". 
3. add a "Run Shell Script" action. Set shell to /bin/zsh and pass input as arguments. 
4. add the following code:
```bash
source ~/opt/miniconda3/etc/profile.d/conda.sh
conda activate paper2audio
paper2speech $1
```
5. save the action and give it a name, e.g. "Paper2Speech"

## Limitations (for PDFs)
- captions of tables, figures are always read at the end of the page (because of the way Nougat has been trained)
- only works for English

## Roadmap
- use gpt-3.5-turbo / Gemma 2B to detect names with special pronunciation, e.g. IEEE
- add chapters to audio file
