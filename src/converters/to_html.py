import typing
from collections import namedtuple
from os import path

Section = namedtuple('Section', ['header', 'subsections'])
Subsection = namedtuple('Subsection', ['header', 'paragraphs'])
single_tags = {
    r'\(dq': '"',
    r'\(bv': r'|',
    r'.zZ': r'',
    r'\\$1': r'',
    r'\*(L"': '',
    r'\*(R"': '',
    r'\(co': r'©',
    r'.Os': '',
    r'\|': r'',
    r'\`': '`',
    r'("': r'"',
    r'\-': r'-',
    r'.Sp': r'<br/>',
    r'.sp': r'<br/>',
    r'C`': r'"',
    r"C'": r'"',
    r'\*(': r'',
    r'\|_': r'_',
    r'\fB': r'<span class="strong">',
    r'\fI': r'<span class="emphasis">',
    r'\fR': r'<span class="romanic">',
    r'\fP': r'</span>',
    r'\e': '\\',
    r'\(aq': "'",
    r'\(bu': '\u2022',
}

inline_tags = {
    r'.de': r'',
    r'.ds': r'',
    r'.nr': r'',
    r'.}f': r'',
    r'.ll': r'',
    r'.in': r'',
    r'.ti': r'',
    r'.el': r'',
    r'.ie': r'',
    r'..': r'',
    r'.if': r'',
    r'.nh': r'',
    r'.zY': r'',
    r'.RS': r'',
    r'.RE': r'',
    r'.IB': r'<b><i>{}</i></b>',
    r'.BI': r'<i><b>{}</b></i>',
    r'.FN': '<i>{}</i>',
    r'.SM': r'<span class="small"></span>',
    r'.RB': r'<b>{}</b>',
    r'.\"': r'<!--{}-->',
    r'.B': r'<b>{}</b>',
    r'\.B': r'<b>{}</b>',
    r'.BR': r'<b>{}</b>',
    r'.IR': r'<i>{}</i>',
    r'.I': r'<i>{}</i>',
    r'.br': r'<br/>',
    r'\&': r'',
    r'.TH': r'<span class="title">{}</span>'
}

default_paragraph_indent = 4


def convert(man_page: typing.TextIO, stylesheet: typing.AnyStr) -> \
        typing.AnyStr:
    """
    Лениво конвертирует man страницу в html, секция за секцией
    """
    stylesheet = path.join(r'..', stylesheet)
    yield ('<!DOCTYPE html>'
           '<html>'
           '<head>'
           '<meta charset="utf-8">'
           f'<link rel="stylesheet" href="{stylesheet}">'
           '</head>'
           '<body>')

    for section in get_sections(man_page):
        yield convert_section(section)

    yield ('</body>'
           '</html>')


def convert_section(section: Section) -> typing.AnyStr:
    """
    Конвертирует раздел в html

    :param section: раздел
    :return: html код раздела
    """

    class_name = ((section.header if section.header else 'headless')
                  .lower()
                  .replace(' ', '-'))

    container_open_tag = f'<div class="section-{class_name} section">'

    header_tag = f'<h1 class="section-header">{section.header}</h1>'

    subsections = '\n'.join(convert_subsection(s) for s in section.subsections)

    container_close_tag = '</div>'

    return '\n'.join([container_open_tag, header_tag,
                      subsections, container_close_tag])


def convert_subsection(subsection: Subsection) -> typing.AnyStr:
    """
    Конвертирует подраздел в html

    :param subsection: подраздел
    :return: html код подраздела
    """

    class_name = ((subsection.header if subsection.header else 'headless')
                  .lower()
                  .replace(' ', '-'))

    container_open_tag = f'<div class="subsection-{class_name} subsection">'

    header_tag = (f'<h2 class="subsection-header">'
                  f'{subsection.header}</h2>')

    paragraphs = '\n'.join(convert_paragraph(p) for p in subsection.paragraphs)

    container_close_tag = '</div>'

    return '\n'.join([container_open_tag, header_tag,
                      paragraphs, container_close_tag])


def convert_paragraph(paragraph) -> typing.AnyStr:
    """
    Конвертирует параграф в html

    :param paragraph: параграф
    :return: html код параграфа
    """
    if isinstance(paragraph, SimpleParagraph):
        return convert_simple_paragraph(paragraph)
    elif isinstance(paragraph, HangingParagraph):
        return convert_hanging_paragraph(paragraph)
    elif isinstance(paragraph, IndentedParagraph):
        return convert_indented_paragraph(paragraph)
    elif isinstance(paragraph, TaggedParagraph):
        return convert_tagged_paragraph(paragraph)
    else:
        return ''


def convert_simple_paragraph(simple_paragraph) -> typing.AnyStr:
    """
    Конвертирует обычный параграф в html

    :param simple_paragraph: обычный параграф
    :return: html код параграфа
    """
    open_tag = '<p class="simple-paragraph paragraph">'
    converted = ' '.join(convert_line(l) for l in simple_paragraph.content)
    close_tag = '</p>'

    return ''.join([open_tag, converted, close_tag])


def convert_hanging_paragraph(hanging_paragraph) -> typing.AnyStr:
    """
    Конвертирует висячий параграф в html

    :param hanging_paragraph: висячий параграф
    :return: html код параграфа
    """
    indent = hanging_paragraph.indent
    if not indent:
        indent = default_paragraph_indent

    hanging_line = hanging_paragraph.hang
    if not hanging_line:
        hanging_line = ''
    hanging_line = convert_line(hanging_line)
    hanging_line_tag = f'<span class="hang">{hanging_line}</span>'

    open_tag = (f'<p class="hanging-paragraph paragraph" '
                f'style="padding-left: {indent}em">')
    converted = ' '.join(convert_line(l) for l in hanging_paragraph.content)
    close_tag = '</p>'

    return ''.join([hanging_line_tag, open_tag, converted, close_tag])


def convert_indented_paragraph(indented_paragraph) -> typing.AnyStr:
    """
    Конвертирует параграф с отступом в html

    :param indented_paragraph: параграф с отступом
    :return: html код параграфа
    """
    hang_tag = indented_paragraph.hang_tag
    if not hang_tag:
        hang_tag = ''
    hang_tag = convert_line(hang_tag)

    indent = indented_paragraph.indent
    if not indent:
        indent = default_paragraph_indent

    converted = ' '.join(convert_line(l) for l in indented_paragraph.content)

    container_open_tag = '<div class="indented-paragraph-container">'

    hang_tag_tag = f'<span class="hang-tag">{hang_tag}</span>'

    paragraph = (f'<p class="indented-paragraph paragraph" '
                 f'style="padding-left: {indent}em">'
                 f'{converted}'
                 f'</p>')

    container_close_tag = '</div>'

    return ''.join([container_open_tag,
                    hang_tag_tag, paragraph, container_close_tag])


def convert_tagged_paragraph(tagged_paragraph) -> typing.AnyStr:
    """
    Конвертирует параграф с биркой в html

    :param tagged_paragraph: параграф с биркой
    :return: html код параграфа
    """
    tag = tagged_paragraph.hang_tag
    if not tag:
        tag = ''
    tag = convert_line(tag)

    indent = tagged_paragraph.indent
    if not indent:
        indent = default_paragraph_indent

    converted = ' '.join(convert_line(l) for l in tagged_paragraph.content)

    container_open_tag = '<div class="tagged-paragraph-container">'

    tag_tag = f'<span class="hang-tag">{tag}</span>'

    paragraph = (f'<p class="tagged-paragraph paragraph" '
                 f'style="padding-left: {indent}em">'
                 f'{converted}'
                 f'</p>')

    container_close_tag = '</div>'

    return ''.join([container_open_tag, tag_tag,
                    paragraph, container_close_tag])


def convert_line(line: typing.AnyStr) -> typing.AnyStr:
    """
    Конвертирует одну строку

    :param line: строка для конвертаций
    :return: сконвертированная строка с требуемым отступом
    """
    line = line.replace('<', '&lt;') \
        .replace('>', '&gt;')

    for tag, value in single_tags.items():
        line = line.replace(tag, value)

    for tag, value in inline_tags.items():
        if line.startswith(tag):
            line = value.format(line[len(tag):].strip())

    return line


def get_sections(man_page: typing.TextIO) -> Section:
    """
    Конструирует секций и лениво их возвращает

    :param man_page: man страница
    :return: сконструированная секция
    """
    for header, content in divide_into_sections(man_page):
        header = header.strip(' "')
        subsections = [sub for sub in get_subsections(content)]

        yield Section(header, subsections)


def get_subsections(section_content: typing.List[str]) -> Subsection:
    """
    Создаёт подразделы из содержимого раздела и лениво их возвращает

    :param section_content: содержимое раздела
    :return: подраздел
    """
    for header, content in divide_into_subsection(section_content):
        header = header.strip(' "')
        paragraphs = [p for p in get_paragraphs(content)]

        yield Subsection(header, paragraphs)


simple_paragraph_tags = ('.LP', '.PP', '.P')
paragraph_tags = simple_paragraph_tags + ('.HP', '.TP', '.IP')


def get_paragraphs(subsection_content: typing.List[str]):
    """
    Создаёт параграфы, определяемые .LP, .PP, .P, .HP, .IP, .TP из содержимого
    подраздела и лениво их возвращает

    :param subsection_content: содержимое подраздела
    :return: параграф подраздела
    """
    header = ''
    content = []
    for line in subsection_content:
        if line.startswith(paragraph_tags):
            if content:
                yield get_paragraph(header, content)

            header = line
            content = []
            continue

        content.append(line)

    if content:
        yield get_paragraph(header, content)


SimpleParagraph = namedtuple('SimpleParagraph', ['content'])


def get_paragraph(header: str, content: typing.List[str]):
    """
    Определяет, создаёт и возвращает нужный тип параграфа

    :param header: строка содержащяя тег определяющий параграф
                   (.PP, .TP, .IP и.т.п) и доп. информацию
    :param content: содержание параграфа
    :return: параграф соответствующего типа
    """
    parts = header.split()
    # header.split() будет пуст, когда мы возвращаем все строки
    # до первого объявления какого-либо параграфа
    tag = ''
    if len(parts):
        tag = parts[0]

    if not tag or tag in simple_paragraph_tags:
        return SimpleParagraph(content)
    elif tag == '.HP':
        return get_hanging_paragraph(parts, content)
    elif tag == '.IP':
        return get_indented_paragraph(parts, content)
    elif tag == '.TP':
        return get_tagged_paragraph(parts, content)


HangingParagraph = namedtuple('HangingParagraph',
                              ['indent', 'hang', 'content'])


def get_hanging_paragraph(parts: typing.List, content: typing.List[str]) -> \
        HangingParagraph:
    """
    Создаёт и возвращает HangingParagraph

    :param parts: сам тег .HP, определяющий висячий параграф
                  и отступ, если задан
    :param content: содержимое параграфа
    :return: висячий параграф
    """
    # если отступ не задан, то он None
    indent = None
    # второй элемент - величина отступа, всё остальное
    # в строке игнорируем, поэтому `> 1`, а не `== 2`
    if len(parts) > 1:
        try:
            indent = int(parts[1])
        except ValueError:
            # если отступ - не число, то
            # он остается равным None
            pass
    # первая строка не имеет отступа - свисает
    hanged = content[0]
    content = content[1:]

    return HangingParagraph(indent, hanged, content)


IndentedParagraph = namedtuple('IndentedParagraph',
                               ['indent', 'hang_tag', 'content'])


def get_indented_paragraph(parts: typing.List, content: typing.List[str]) -> \
        IndentedParagraph:
    """
    Создаёт и возвращает IndentedParagraph

    :param parts: сам тег .IP, определяющий параграф с отступом
                  и бирка параграфа с отступом, если заданы
    :param content: содержимое параграфа
    :return: параграф с отступом
    """
    hang_tag = None
    indent = None

    # если второй элемент есть это бирка,
    # иначе он остаётся None
    if len(parts) > 1:
        hang_tag = parts[1]

        # если третий элемент есть это отступ,
        # иначе он остаётся None
        if len(parts) > 2:
            try:
                indent = int(parts[2])
            except ValueError:
                # если это не число, indent остаётся
                # равным None
                pass

    return IndentedParagraph(indent, hang_tag, content)


TaggedParagraph = namedtuple('TaggedParagraph',
                             ['indent', 'hang_tag', 'content'])


def get_tagged_paragraph(parts: typing.List, content: typing.List[str]) -> \
        TaggedParagraph:
    """
    Создаёт и возвращает TaggedParagraph

    :param parts: сам тег .TP определяющий помеченный параграф
                  и отступ, если задан
    :param content: содержимое параграфа
    :return: помеченный параграф
    """
    indent = None

    # если второй элемент есть это отступ,
    # иначе отступ остаётся равным None
    if len(parts) > 1:
        try:
            indent = int(parts[1])
        except ValueError:
            # если отступ задан не числом, то
            # он остаётся равным None
            pass

    # первая строка следующая за строкой определяющей
    # помеченный абзац содержит бирку для абзаца
    hang_tag = content[0]

    return TaggedParagraph(indent, hang_tag, content[1:])


def divide_into_sections(man_page: typing.TextIO) -> \
 typing.Tuple[str, typing.List[str]]:
    """
    Делит страницу на разделы, определяемые .SH

    :param: man страница
    :return: пару заголовок раздела, содержимое (список строк) раздела
    """
    yield from divide_by_tag('.SH', man_page)


def divide_into_subsection(section_content: typing.List[str]) -> \
        typing.Tuple[str, typing.List[str]]:
    """
    Делит содержимое раздела на подразделы, определяемые .SS

    :param section_content: содержимое (список строк) раздела
    :return: пара вида заголовок подраздела, содержимое (список строк)
             подраздела
    """
    yield from divide_by_tag('.SS', section_content)


def divide_by_tag(tag: str, it: typing.Iterable[str]) -> \
        typing.Tuple[str, typing.List[str]]:
    """
    Делит строки коллекций на группы по разделителю.

    Группа - пара: разделитель, список всех строк коллекций до следующего
    разделителя.

    Разделитель - строка коллекций начинающийся с разделительного тега.

    Пример:

    it = ['.ss hello', 'hi', 'yep', '.ss text', 'another text']

    tag = '.ss'

    вернет пары ('hello', ['hi', 'yep']), ('text', ['another text'])

    Если коллекция начинается не с разделителя, то в первой группе первый
    элемент пары будет пустая строка

    Пример:

    it = ['some text', '.ss hello', 'hi', 'yep']

    tag = '.ss'

    вернет пары ('', ['some text']), ('hello', ['hi', 'yep'])

    :param tag: разделительный тег
    :param it: итерируемая коллекция строк
    :return: пара разделитель, список всех элементов итерируемого объекта до
             следующего разделителя
    """
    divider = ''
    content = []
    tag_with_space_length = len(tag) + len(' ')
    for line in it:
        line = line.strip('\r\n')

        if line.startswith(tag):
            if divider or content:
                yield divider, content

            divider = line[tag_with_space_length:]
            content = []
            continue

        content.append(line)

    if divider or content:
        yield divider, content
