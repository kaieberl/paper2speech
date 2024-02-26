import re

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

from replacements import text_replacements, math_replacements


class MarkdownModel:
    def __init__(self) -> None:
        self.ssml = ''

    def markdown_to_html(self, content: str):
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
            self.ssml = self.ssml.replace(pattern, replacement)

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
