import re, os
from typing import Tuple
from markdown import Markdown
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

md = Markdown(extensions=['mdx_math'], extension_configs={'mdx_math': { 'enable_dollar_delimiter': True }})

#############################################
# Export HTML
class CodeBlock:
    head_content     = \
        "<style>{}</style>".format(HtmlFormatter().get_style_defs('.highlight')).replace(".highlight { background: #f8f8f8; }", "") # Remove white background
    head_content += \
        r"""
        <style>
        div.section:hover div.code {
            background: #f8fafb;
        }
        div.section div.code {
            background: #ebedef;
              padding: 14px 8px 16px 15px;
              vertical-align: top;
        }
        @media (min-width: 768px) {
            div.section div.code {
                margin-left: 40%;
            }
        }
        </style>
        """
    code_key_phrase = r"<codeblock_code_content>"
    html_template   = \
        r"""
        <div class="code">
            <codeblock_code_content>
        </div>
        """
    def __init__(self) -> None:
        self.code_str = r""

    def add(self, code_block: str):
        self.code_str += code_block

    def render(self):
        c = highlight(self.code_str, PythonLexer(), HtmlFormatter()) if self.code_str != r"" else r""
        block = self.html_template.replace(
            self.code_key_phrase,
            c
        )
        return block

    @property
    def is_empty(self):
        return self.code_str == r""

    
class CommentBlock:
    head_content = \
        r"""
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex/dist/katex.min.css" crossorigin="anonymous">
        <script src="https://cdn.jsdelivr.net/npm/katex/dist/katex.min.js" crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/katex/dist/contrib/mathtex-script-type.min.js" defer></script>
        <style>
            div.section div.doc {
                box-sizing: border-box;
                padding: 10px 8px 1px 8px;
                vertical-align: top;
                text-align: left;
                word-break: break-all;
            }
        @media (min-width: 768px) {
            div.section div.doc {
                float: left;
                width: 40%;
                min-height: 5px;
            }
        }
        @media (min-width: 1024px) {
            div.section div.doc {
                padding: 10px 25px 1px 50px;
            }
        }
        div.section div.doc img {
            max-width: 100%;
            transition:transform 0.25s ease;
        }
        img:hover {
            -webkit-transform:scale(1.75);
            transform:scale(1.75);
        }        
        </style>
        """
    comment_key_phrase = r"<codeblock_comment_content>"
    html_template   = \
        r"""
        <div class="doc">
            <codeblock_comment_content>
        </div>
        """

    def __init__(self) -> None:
        self.comment_str = r""

    def clean_inside_comment(self, str_block: str):
        """ Remove leading comment symbols. """
        str_block_list = [re.sub(r"[^\n\w]*#[ \t]*", '', x) for x in str_block.splitlines()]
        return ' '.join(str_block_list).replace(r"\n", "\n\n")

    def clean_outside_comment(self, str_block: str):
        """ Remove leading and trailing comment symbols. """
        str_block = re.sub(r"\s*[^\W]*r?\"\"\"", '', str_block)
        no = min([(len(x) - len(x.lstrip())) for x in str_block.splitlines() if not (x.isspace() or x == '')])
        str_block_list = []
        for x in str_block.splitlines():
            if not (x.isspace() or x == ''):
                str_block_list.append(x[no:])
            else:
                str_block_list.append(x)
        return '\n'.join(str_block_list)

    def add(self, comment_str: str, is_inside: bool):
        if is_inside:
            self.comment_str += self.clean_inside_comment(comment_str)
        else:
            self.comment_str += self.clean_outside_comment(comment_str)

    def add_plain(self, comment_str: str):
        self.comment_str += comment_str

    def render(self):
        block = self.html_template.replace(
            self.comment_key_phrase, md.convert(self.comment_str) 
        )
        return block


class Section:
    head_content = \
    r"""
    <style>
        div.section:hover {
            background: #f8fafb;
        }
        div.section {
            position: relative;
        }
        div.section:after {
            clear: both;
            content: "";
            display: block;
        }
        div.section {
            border-top: 1px solid #e2e2eb;
        }
        div.footer {
            margin-top: 25px;
            position: relative;
            padding: 10px 0;
            text-align: center;
        }
        div.footer a {
            display: inline-block;
            margin: 8px;
            font-size: 1.3rem;
        }
        div.footer {
            background: #d5dbe0;
        }
    </style>
    """ + CodeBlock.head_content \
        + CommentBlock.head_content
    
    section_id_key_phrase = r"<section_id_key_phrase>"
    comment_key_phrase    = r"<section_comment_key_phrase>"
    code_key_phrase       = r"<section_code_key_phrase>"
    html_template = \
    r"""
    <div class="section" id="<section_id_key_phrase>">
        <section_comment_key_phrase>
        <section_code_key_phrase>
    </div>
    """
    def __init__(self) -> None:
        self.comment = CommentBlock()
        self.code    = CodeBlock()

    def addCommentBlock(self, comment: str, is_inside: bool=False, is_plain: bool=False):
        if is_plain:
            self.comment.add_plain(comment)
        else:
            self.comment.add(comment, is_inside)

    def addCodeBlock(self, code: str):
        self.code.add(code)

    def render(self, section_id: int):
        _html = self.html_template.replace(self.section_id_key_phrase
        , str(section_id))
        _html = _html.replace(self.comment_key_phrase, self.comment.render())
        _html = _html.replace(self.code_key_phrase, self.code.render())
        return _html

    @property
    def is_valid(self):
        return not self.code.is_empty
        
class Header(Section):
    html_template = \
    r"""
    <div class="section" id="<section_id_key_phrase>">
        <section_comment_key_phrase>
    </div>
    """
    def __init__(self) -> None:
        super().__init__()

    def add_parents(self, parent_list: list) -> None:
        tmp = r""
        for parent in parent_list:
            tmp += r"""<a class="parent" href="{}">{}</a>""".format(parent[1], parent[0])
        self.addCommentBlock(tmp, is_plain=True)

class Footer(Section):
    html_template = \
    r"""
    <div class="footer">
        <a href="mailto:thomas.buechler@cariad.technology">Contact</a>
    </div>
    """
    def __init__(self) -> None:
        super().__init__()

    def render(self):
        return self.html_template

class Page:
    head_content            = \
    r"""
    <style>
        html {
            font-size: 62.5%;
        }
        body {
            font-size: 1.5em;
            line-height: 1.6;
            font-weight: 400;
            font-family: "SF Pro Text", "SF Pro Icons", "Helvetica Neue", "Helvetica", "Arial", sans-serif;
            margin: 0;
            padding: 0;
            color: #777;
            background: #ecf0f3;
        }
        #section_container {
            position: relative;
            background: #ecf0f3;
        }
        #background {
            background: #ebedef;
            border-left: 1px solid #e2e2eb;
            position: absolute;
            top: 0;
            left: 40%;
            right: 0;
            bottom: 0;
            z-index: 0;
            display: none;
        }
        @media (min-width: 768px) {
            #background {
                display: block;
            }
        }
        a {
            color: #666;
        }
        a:visited {
            color: #777;
        }
        a.parent {
            text-transform: uppercase;
            font-weight: bold;
            font-size: 12px;
            margin-right: 10px;
            text-decoration: none;
        }
        a.parent:after {
            content: ">";
            font-size: 14px;
            margin-left: 4px;
        }
    </style>
    """
    head_content_key_phrase = r"<head_content_key_phrase>"
    sections_key_phrase     = r"<sections_key_phrase>"
    html_template = \
    r"""<!DOCTYPE html><html><head><head_content_key_phrase></head><body><div id="section_container"><div id="background"></div><sections_key_phrase><sections_key_phrase></div></body></html>
    """
    def __init__(self) -> None:
        self.head_content += Section.head_content
        self.header   = None 
        self.sections = []
        self.footer   = Footer()
        
    def add_header(self, section: Section):
        self.sections.append(section)

    def add_section(self, section: Section):
        if not isinstance(section, Section):
            print("Only sections can be added to the page right now.")
        self.sections.append(section)

    def clean_markdown_for_katex(self, _html: str):
        _html = _html.replace("<em>", "")
        _html = _html.replace("</em>", "")
        return _html

    def render(self):
        _html = self.html_template.replace(
            self.head_content_key_phrase,
            self.head_content
        )
        for i, section in enumerate(self.sections):
            _html = _html.replace(
                self.sections_key_phrase, 
                section.render(section_id=i),
                1 # Replace only first occurrence
            )
            _html = _html.replace(
                self.sections_key_phrase,
                self.sections_key_phrase * 2
            )

        _html = _html.replace(self.sections_key_phrase, self.footer.render(), 1)
        _html = _html.replace(self.sections_key_phrase, "")
        _html = self.clean_markdown_for_katex(_html)
        return _html

    def dump(self, file_path):
        assert file_path.endswith(".html"), "Only HTML export is supported."
        f = open(file_path, "w", encoding="utf8")
        f.write(self.render())
        f.close()

################################################################################
################################################################################

import re

# Strikes if beginning of def is in line
re_def_in_line = r"^[^\w]*def "
# Strikes if beginning of class is in line
re_class_in_line = r"^[^\w]*class "
# Strikes if a possible end of a def or class header is found (a : followed by only whitespaces and newline)
re_def_class_end_in_line = r":[\r\f]*\n"
#
re_inline_comment_in_line = r"[^\n\w\W]*#[ ]*[^\w]"
# Strikes if outline comment is done in one line
re_outline_comment_in_one_line = r"r?\"\"\".*\"\"\""
# Strikes if outline comment ends
re_outline_comment_end = r".*\"\"\""

def is_empty(str: str) -> bool:
    """ Checks if a str is empty or only contains whitspaces. """
    return (str.isspace() or str==r"")

def is_def_class_end(line_no, lines) -> bool:
    return bool(re.search(re_def_class_end_in_line, lines[line_no]))

def is_def(line_no: int, lines: list[str]) -> bool:
    return bool(re.search(re_def_in_line, lines[line_no]))

def is_class(line_no: int, lines: list[str]) -> bool:
    return bool(re.search(re_class_in_line, lines[line_no]))

def is_inline_comment(line_no: int, lines: list[str]) -> bool:
    return lines[line_no].lstrip().startswith('#')

def is_outside_comment(line_no: int, lines: list[str]) -> bool:
    return lines[line_no].lstrip().startswith("r\"\"\"") or lines[line_no].lstrip().startswith("\"\"\"") 

def is_code_line(line_no: int, lines: list[str]) -> bool:
    return not(
        is_def(line_no, lines) or
        is_class(line_no, lines) or
        is_inline_comment(line_no, lines) or
        is_outside_comment(line_no, lines) or
        is_empty(lines[line_no])
    )

def is_outside_comment_end(line_no: int, lines: list[str]) -> bool:
    return bool(re.search(re_outline_comment_end, lines[line_no]))

def is_outside_comment_in_one_line(line_no: int, lines: list[str]) -> bool:
    return bool(re.search(re_outline_comment_in_one_line, lines[line_no]))

#############################################################################
## Used to extract the beginning of a .py file
def find_header_end(lines) -> int:
    for idx, _ in enumerate(lines):
        if is_def(idx, lines):
            return idx-1
        if is_class(idx, lines):
            return idx-1
    return idx

def extract_header(lines):
    """ Returns sections object and first line of non-header part. """
    line_header_end = find_header_end(lines)
    section = Section()
    num_comment = 0
    was_inline = False
    line_idx = 0
    for _, _ in enumerate(lines):
        if is_empty(lines[line_idx]):
            # Empty line
            section.addCommentBlock("<br>", True)
            section.addCodeBlock("\n")
        elif is_inline_comment(line_idx, lines):
            # Comment line
            if was_inline:
                section.addCommentBlock(lines[line_idx] + " ", True)
            else:
                num_comment += 1
                num_pointer = "({}) ".format(num_comment)

                # Find place where num_pointer must be placed
                to_place = lines[line_idx].index(''.join(re.findall(re_inline_comment_in_line, lines[line_idx]))) + len(''.join(re.findall(re_inline_comment_in_line, lines[line_idx])))

                _line = lines[line_idx][:to_place] + num_pointer + lines[line_idx][to_place:]
                section.addCommentBlock(_line + " ", True)
                section.addCodeBlock(num_pointer + "\n")
                was_inline = True
        elif is_outside_comment(line_idx, lines):
            _, _l = get_def_class_comment(line_idx, lines)
            section.addCommentBlock(''.join(lines[_l[0]:_l[1]+1]), False)
            line_idx = _l[1]
        else:
            # Code line
            section.addCodeBlock(lines[line_idx])
            was_inline = False
        
        if line_idx == line_header_end:
            break
        line_idx += 1
    return section, line_idx + 1

#############################################################################
#############################################################################
## Used to extract a def or class header including outside comment

def find_def_class_end(line_defClass_starts: int, lines: list[str]):
    """ Searches for the ending of class or def definition and retturns the index of corresponding line. """
    for line_idx in range(line_defClass_starts, len(lines)):
        if is_def_class_end(line_idx, lines):
            return line_idx
    print("End of Def/Class header cannot be found.")
    exit(-1)

def get_def_class_comment(line_after_def_class_ends: int, lines: list[str]):
    """ Checks for outline comments of def and class instances. If available it returns the start and end index of corresponding comment section as well. """
    for line_idx in range(line_after_def_class_ends, len(lines)):
        if is_outside_comment(line_idx, lines):
            if is_outside_comment_in_one_line(line_idx, lines):
                return True, (line_idx, line_idx)
            for comment_line_idx in range(line_idx + 1, len(lines)):
                if is_outside_comment_end(comment_line_idx, lines):
                    return True, (line_idx, comment_line_idx)
            print("End of outline comment not found.")
            exit(-1)
        else:
            if not is_empty(lines[line_idx]):
                return False, (-1, -1)
    print("This is only reachable for invalid files.")
    exit(-1)

def extract_def_class_header(line_defClass_starts, lines):
    ## Code in [line_defClass_starts:line_defClass_header_ends]
    line_defClass_header_ends = find_def_class_end(line_defClass_starts, lines)
    has_comment, comment_lines = get_def_class_comment(line_defClass_header_ends + 1, lines)

    section = Section()
    section.addCodeBlock(''.join(lines[line_defClass_starts:line_defClass_header_ends+1]))
    if has_comment:
        section.addCommentBlock(''.join(lines[comment_lines[0]:comment_lines[1]+1]), False)
    else:
        comment_lines = (0, line_defClass_header_ends)
    return section, comment_lines[1] + 1

#############################################################################
#############################################################################
## Used to extract an inline comment along with the code section
def get_inline_comment_end(line_inline_comment_starts: int, lines: list[str]):
    for line_idx in range(line_inline_comment_starts, len(lines)):
        if is_empty(lines[line_idx]):
            continue
        elif is_inline_comment(line_idx, lines):
            continue
        else:
            # Occurance of non-comment -> return decremented index
            return line_idx - 1
    return line_idx

def get_code_section_end(line_code_section_starts: int, lines: list[str]):
    for line_idx in range(line_code_section_starts, len(lines)):
        if is_code_line(line_idx, lines):
            continue
        else:
            return line_idx - 1
    return line_idx

def extract_inline_code_section(line_inline_comment_starts, lines):
    line_inline_comment_ends = get_inline_comment_end(line_inline_comment_starts, lines)

    section = Section()
    section.addCommentBlock(''.join(lines[line_inline_comment_starts:line_inline_comment_ends+1]), True)

    if line_inline_comment_ends + 1 != len(lines):
        line_code_sections_end = get_code_section_end(line_inline_comment_ends + 1, lines)
        section.addCodeBlock(''.join(lines[line_inline_comment_ends + 1:line_code_sections_end+1]))
    else:
        line_code_sections_end = len(lines)
    return section, line_code_sections_end + 1



#############################################################################
#############################################################################
## Starting point of single file processing
def pydoc(py_path: str, html_path: str=None, parent_link: list=[]):
    try:
        with open(py_path, 'r', encoding="utf8") as py_file:
            page = Page()
            py_lines = py_file.readlines()

            ## Add header to page
            header_section = Header()
            header_section.add_parents(parent_link)
            page.add_header(header_section)

            ## Import Code Header manually
            header_code_section, search_start = extract_header(py_lines)
            page.add_section(header_code_section)

            focus_on = search_start
            # To avoid infinite loops
            for _ in range(search_start, len(py_lines)): 
                if focus_on >= len(py_lines):
                    break

                ## Continue if empty
                if is_empty(py_lines[focus_on]):
                    focus_on += 1
                    continue

                ## If Def or Class instance starts
                if is_class(focus_on, py_lines) or is_def(focus_on, py_lines):
                    s, i = extract_def_class_header(focus_on, py_lines)
                    page.add_section(s)
                    focus_on = i
                    continue
                elif is_inline_comment(focus_on, py_lines):
                ## if inline comment starts
                    s, i = extract_inline_code_section(focus_on, py_lines)
                    page.add_section(s)
                    focus_on = i
                    continue
                
                focus_on += 1

            if (html_path is not None):
                page.dump(html_path)
            return page.render()

    except FileNotFoundError:
        print("Python file {} cannot be found.".format(
            py_path
        ))
        exit(-1)


#############################################################################
#############################################################################
## Starting point of multi directory processing
def get_dirs(root_path: str):
    """ Returns list of directories in the current path alphabetically sorted. """
    _dirs = []
    for _dir in os.listdir(root_path):
        if os.path.isdir(os.path.join(root_path, _dir)):
            if '__pycache__' in _dir:
                continue
            _dirs.append(_dir)
    return sorted(_dirs)

def get_pyFiles(root_path: str):
    """ Return list of files in the current path alphbat"""
    _files = []
    for _file in os.listdir(root_path):
        if os.path.isfile(os.path.join(root_path, _file)):
            if not _file.endswith('.py'):
                continue
            if '__init__' in _file:
                continue
            _files.append(_file)
    return sorted(_files)

def create_index_html_file(root_src: str, root_doc: str, parent_link: list=[("Home", "index.html")]):
    page = Page()

    ## Add header to page
    header_section = Header()
    header_section.add_parents(parent_link)
    page.add_header(header_section)

    ###
    files = get_pyFiles(root_src)
    dirs  = get_dirs(root_src)

    table = r""
    if parent_link == [("Home", "index.html")]:
        table += (r"#  Home &#127969 " + "\n\n")
    else:
        table += ("# " + os.path.basename(root_src) + "\n\n")

    for _file in files:
        table += (r"""- <a href="{}.html">{}</a>""".format(_file.replace('.py', ''), _file.replace('.py', '')) + "\n")

    for _dir in dirs:
        table += (r"""* <a href="{}/index.html">{}</a> <b>></b>""".format(_dir, _dir) + "\n")

    section = Section()
    section.addCommentBlock(table)
    page.add_section(section)

    page.dump(os.path.join(root_doc,"index.html"))
    return parent_link


def pydoc_runner_process_dir(root_src: str, root_doc: str, parent_link: list[Tuple[str, str]]):
    if not os.path.isdir(root_doc):
        os.mkdir(root_doc)
    
    _dirs = get_dirs(root_src)
    for c_dir in _dirs:
        ##
        if not os.path.isdir(os.path.join(root_doc, c_dir)):
            os.mkdir(os.path.join(root_doc, c_dir))
        next_parent_link = [(x[0], "../" + x[1]) for x in parent_link]
        next_parent_link.append((c_dir, "index.html"))
        ##
        pydoc_runner_process_dir(
            os.path.join(root_src, c_dir),
            os.path.join(root_doc, c_dir),
            next_parent_link
        )

    create_index_html_file(root_src, root_doc, parent_link)

    _py_files = get_pyFiles(root_src)
    for py_file in _py_files:
        print(f"Processing {py_file}...", end=" ")
        pydoc(
            os.path.join(root_src, py_file), 
            os.path.join(root_doc, py_file.replace('.py', '.html')),
            parent_link=parent_link
        )
        print("Done!")

def pydoc_runner(root_src: str, root_doc: str):
    """
    Args:

    * root_src: Root path of source directory.
    * root_doc: Root path of doc directory.
    """
    parent_links = [("Home", "index.html")]
    pydoc_runner_process_dir(root_src, root_doc, parent_links)

