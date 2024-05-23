"""Converts Mathpix Markdown (mmd) files to html with added explanation buttons."""
import os.path
import subprocess
import zipfile

from bs4 import BeautifulSoup


def mmd_to_tex(file_path):
    """Convert mmd to tex file using Mathpix CLI."""
    base_path, file_extension = os.path.splitext(file_path)
    if not file_extension.lower() == '.mmd':
        raise ValueError(f'{file_path} is not an mmd file')
    command = f'/opt/homebrew/bin/mpx convert "{os.path.basename(file_path)}" "{os.path.basename(base_path) + ".tex"}"'
    process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.path.dirname(file_path))
    if process.returncode != 0:
        raise RuntimeError(f"Mathpix CLI conversion failed: {process.stderr.decode('utf-8')}")

    zip_file = base_path + '.tex.zip'
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(os.path.dirname(file_path))
    os.remove(zip_file)


def tex_to_html(file_path, out_path):
    """Convert tex to html using LaTeXML."""
    base_path, file_extension = os.path.splitext(file_path)
    if not file_extension.lower() == '.tex':
        raise ValueError(f'{file_path} is not a tex file')
    command = f'latexmlc "{base_path + ".tex"}" --dest="{os.path.join(out_path, os.path.basename(base_path) + ".html")}"'
    process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.returncode != 0:
        raise RuntimeError(f"LaTeXML conversion failed: {process.stderr.decode('utf-8')}")


def append_stylesheet(doc, href):
    """Adds a stylesheet link to the HTML document."""
    style_tag = doc.new_tag('link', rel='stylesheet', href=href)
    doc.head.append(style_tag)


def append_script(doc, src, onload=None):
    """Adds a script tag to the HTML document with optional onload handler."""
    script_tag = doc.new_tag('script', src=src)
    if onload:
        script_tag.string = f'window.onload = function() {{ {onload} }}'
    doc.head.append(script_tag)


def is_theorem(element):
    return element.get_text().lstrip().startswith(('Theorem', 'Lemma', 'Corollary', 'Proposition', 'Definition', 'Remark'))


def wrap_theorems(doc):
    headings = doc.select('h2, h3, h4, h6')

    for heading in headings:
        add_button(doc, heading)

    # find .ltx_para elements whose text content starts with "Theorem", "Lemma", "Corollary", "Proposition", "Definition", "Example", "Remark"
    paras = doc.select('.ltx_para')
    for para in paras:
        if is_theorem(para):
            # put this and all subsequent elements into a section element, until there is another element with the same class
            section = doc.new_tag('section')
            section['class'] = 'ltx_theorem'
            para.insert_before(section)
            section.append(para)
            next_element = section.find_next_sibling()
            while next_element and not is_theorem(next_element):
                section.append(next_element)
                next_element = section.find_next_sibling()

            add_button(doc, para)

    return doc


def add_button(doc, element):
    new_button = doc.new_tag('button')
    new_button['onclick'] = 'handleExplainButton(this)'
    new_button['class'] = 'explain-section-button'
    explain_span = doc.new_tag('span')
    explain_span['class'] = 'material-icons-round'
    explain_span.string = 'auto_awesome'

    new_button.append(explain_span)
    element.insert_before(new_button)


def process_html(file_path):
    """Remove Mathpix styling and add reference to custom css."""
    with open(file_path, 'r') as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    
    soup.html['data-theme'] = 'dark'

    # Add stylesheets
    append_stylesheet(soup, 'https://ar5iv.labs.arxiv.org/assets/ar5iv-fonts.0.7.9.min.css')
    append_stylesheet(soup, 'https://ar5iv.labs.arxiv.org/assets/ar5iv.0.7.9.min.css')
    append_stylesheet(soup, 'https://ar5iv.labs.arxiv.org/assets/ar5iv-site.0.2.2.css')
    append_stylesheet(soup, 'https://fonts.googleapis.com/icon?family=Material+Icons+Round')
    append_stylesheet(soup, './styles_latexml.css')

    # Add script
    append_script(soup, 'https://cdn.jsdelivr.net/npm/mathpix-markdown-it@1.0.40/es5/bundle.js',
                  onload='window.loadMathJax()')
    append_script(soup, './script_latexml.js')

    soup = wrap_theorems(soup)
    with open(file_path, 'w') as f:
        f.write(soup.prettify())
