import re
import subprocess
from typing import List

from bs4 import BeautifulSoup
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.deflist import deflist_plugin
from mdit_py_plugins.tasklists import tasklists_plugin
from mdit_py_plugins.field_list import fieldlist_plugin
from mdit_py_plugins.anchors import anchors_plugin
# from mdit_py_plugins.container import container_plugin
from mdit_py_plugins.attrs import attrs_plugin
from mdit_py_plugins.texmath import texmath_plugin

from src.replacements import text_replacements, math_replacements

GEMMA_CPP_PATH = '/Users/k/Documents/Code/gemma.cpp/build/gemma'


class MarkdownModel:
    def __init__(self) -> None:
        self.ssml = ''

    def markdown_to_html(self, content: str):
        def is_authors(text: str) -> List[bool]:
            result = subprocess.run(
                [GEMMA_CPP_PATH, '--', '--tokenizer', '/Users/k/Documents/Code/gemma.cpp/build/tokenizer.spm', '--compressed_weights', '/Users/k/Documents/Code/gemma.cpp/build/2b-it-sfp.sbs', '--model', '2b-it', '--verbosity', '0'],
                input='You are provided with lines extracted from various scientific papers. Your task is to determine whether each line represents the list of authors. Here is how to decide. Author List (True): Typically includes names (e.g., Sarah Wilson), Michael Johnson). Not an Author List (False): Could be any other part of the paper, such as the title, sentences from the abstract or body, figure captions, etc. ' + text,
                capture_output=True,
                text=True
            )
            result = subprocess.run(
                [GEMMA_CPP_PATH, '--', '--tokenizer', '/Users/k/Documents/Code/gemma.cpp/build/tokenizer.spm', '--compressed_weights', '/Users/k/Documents/Code/gemma.cpp/build/2b-it-sfp.sbs', '--model', '2b-pt', '--verbosity', '0'],
                input='<start_of_turn>user Your task is to determine whether each line represents the list of authors (True / False).<end_of_turn>' + '<start_of_turn>model ' + ' '.join(result.stdout.split("\n")) + '<start_of_turn>user Convert your answer to booleans for each line.<end_of_turn><start_of_turn>model',
                capture_output=True,
                text=True
            )
            # convert result containing some "True" and "False" to list of booleans
            boolean_list = [word.lower() == 'true' for word in result.stdout.split() if word.lower() in ['true', 'false']]
            return boolean_list

        needs_author_check = '# abstract' in content.lower() or '# introduction' in content.lower()

        md = (MarkdownIt(
            'commonmark',
            {}
        )
              .use(front_matter_plugin)
              .use(footnote_plugin)
              .use(deflist_plugin)
              .use(tasklists_plugin)
              .use(fieldlist_plugin)
              .use(anchors_plugin, max_level=6)
              # .use(container_plugin)
              .use(attrs_plugin)
              .use(texmath_plugin, delimiters='brackets'))
        rendered = md.render(content)

        # prepare html for text-to-speech
        soup = BeautifulSoup(rendered, 'html.parser')
        # replace latex commands inside <eq> tag with their text representation
        for eq in soup.find_all(['eq']):
            for pattern, replacement in math_replacements:
                eq.string = re.sub(pattern, ' ' + replacement + ' ', eq.get_text())
            eq.string = re.sub(r' +', ' ', eq.get_text()).strip()

        # remove attributes from tags
        for tag in soup.find_all(True):
            tag.attrs = {}

        for elem in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            elem.name = 'p'
            elem.insert_after(soup.new_tag('break', time='0.5s'))
            elem.insert_before(soup.new_tag('break', time='0.5s'))

        for elem in soup.find_all('li'):
            elem.name = 'p'

        # remove ol, ul tags
        for elem in soup.find_all(['ol', 'ul', 'eq', 'section']):
            elem.unwrap()

        for elem in soup.find_all(['em', 'strong']):
            elem.name = 'emphasis'

        for elem in soup.find_all(['a']):
            elem.unwrap()

        for elem in soup.find_all(['img', 'table', 'eqn']):
            elem.decompose()

        self.ssml = str(soup)

        for pattern, replacement in text_replacements:
            self.ssml = re.sub(pattern, replacement, self.ssml)

        if needs_author_check:
            soup = BeautifulSoup(self.ssml, 'html.parser')
            tags = [tag for tag in soup.children if tag.get_text() and tag.get_text() != "\n"][:6]
            elements = [tag.get_text() for tag in tags]
            # if longest element is >300 characters, remove all subsequent elements
            while elements and len(max(elements, key=len)) > 300:
                elements = elements[:-1]
            prompt = ""
            for i, elem in enumerate(elements):
                elem = re.sub(r'\d+', '', elem)
                prompt += f'{i + 1}: "' + elem + '", '
            try:
                remove = is_authors(prompt[:-2])
                assert len(remove) == len(elements)
                for i, elem in enumerate(tags):
                    if remove[i]:
                        # replace only the first occurrence
                        self.ssml = self.ssml.replace(str(elem), '', 1)
            except Exception as e:
                print(f"Removing authors using Gemma.cpp failed: {e}")

    def get_chunk(self) -> str:
        # break after </p> if current chunk length exceeds 4500 characters
        chunk = ''
        soup = BeautifulSoup(self.ssml, 'html.parser')
        for tag in soup.children:
            tag_str = str(tag)
            if len(chunk) + len(tag_str) > 4500:
                yield chunk
                chunk = tag_str
            else:
                chunk += tag_str
        yield chunk
