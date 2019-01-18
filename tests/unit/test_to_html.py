import os
import pytest
import sys
from io import StringIO
from itertools import chain

sys.path.append(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.converters import to_html
from src.converters.to_html import (
    Section, Subsection, SimpleParagraph,
    HangingParagraph, IndentedParagraph, TaggedParagraph,
    default_paragraph_indent)


class TestSections:
    """
    Деление, создание, и конвертация разделов
    """
    contentless_section = ['.SH CONTENTLESS']
    headless_section = ['headless section']
    simple_section = ['.SH SIMPLE', 'simple section']
    mans_contents = [
        [],
        [
            r'.\\" MAN PAGE COMMENTS to',
            r'.\\"   Chet Ramey',
            r'.\\"   Case Western Reserve University',
            r'.\\"   chet.ramey@case.edu',
            r'.\\"   Last Change: Sun Feb  2 16:21:40 EST 2014',
            r'.\\" bash_builtins, strip all but Built-Ins section'
        ],
        [
            '.SH NAME',
            '.SH SYNOPSIS',
            '.SH COPYRIGHT'
        ],
        [
            '.SH DESCRIPTION',
            'Bash is an sh-compatible command language interpreter that ',
            'executes commands read from the standard input or from a file'
        ],
        [
            '.SH OPTIONS',
            '.SS Arrays'
        ],
        [
            '.SH SHELL GRAMMAR',
            '.SS Simple Commands',
            '.PP',
            r'A \fIsimple command\fP is a sequence of optional variable ',
            '.HP 4',
            r'assignments followed by \fBblank\fP-separated words and',
            r'\fIname\fP=\fB(\fPvalue\fI1\fP ...',
            r'.IP \(bu 4',
            r'redirections, and terminated by a \fIcontrol operator\fP',
            '.TP 4',
            r'\(bu',
            r'The return value of a \fIsimple command\fP is its exit status'
        ]
    ]

    mans_names = [
        'empty',
        'headless_with_headless_sub_and_headless_paragraph',
        'three contentless',
        'simple_with_headless_sub_and_headless_paragraph',
        'simple_with_contentless_sub',
        'simple_with_simple_sub_and_all_type_paragraphs'
    ]

    divided_mans = [
        [],
        [
            ('', [r'.\\" MAN PAGE COMMENTS to',
                  r'.\\"   Chet Ramey',
                  r'.\\"   Case Western Reserve University',
                  r'.\\"   chet.ramey@case.edu',
                  r'.\\"   Last Change: Sun Feb  2 16:21:40 EST 2014',
                  r'.\\" bash_builtins, strip all but Built-Ins section'])
        ],
        [
            ('NAME', []),
            ('SYNOPSIS', []),
            ('COPYRIGHT', [])
        ],
        [
            ('DESCRIPTION', [
                'Bash is an sh-compatible command language interpreter that ',
                'executes commands read from the standard input or from a file'
            ]),
        ],
        [
            ('OPTIONS', ['.SS Arrays'])
        ],
        [
            ('SHELL GRAMMAR', [
                '.SS Simple Commands',
                '.PP',
                r'A \fIsimple command\fP is a sequence of optional variable ',
                '.HP 4',
                r'assignments followed by \fBblank\fP-separated words and',
                r'\fIname\fP=\fB(\fPvalue\fI1\fP ...',
                r'.IP \(bu 4',
                r'redirections, and terminated by a \fIcontrol operator\fP',
                '.TP 4',
                r'\(bu',
                r'The return value of a \fIsimple command\fP is its exit '
                r'status'
            ])
        ]
    ]

    @pytest.mark.parametrize(
        'man_content, divided_man',
        zip(mans_contents, divided_mans),
        ids=mans_names)
    def test_divide_into_sections(
            self, man_content, divided_man):
        """
        to_html.divide_into_sections правильно разбивает man страницу на
        разделы, определяемые .SH
        """
        man = StringIO('\n'.join(man_content))
        sections = [(h, c) for h, c in to_html.divide_into_sections(man)]

        assert sections == divided_man

    expected_sections_number = [0, 1, 3, 1, 1, 1]

    @pytest.mark.parametrize(
        'man_content, expected_sections_number',
        zip(mans_contents, expected_sections_number),
        ids=mans_names)
    def test_divide_into_sections_number_of_sections(
            self, man_content, expected_sections_number):
        """
        to_html.divide_into_sections делит страницу на правильное кол-во
        разделов, определяемых .SH
        """
        man = StringIO('\n'.join(man_content))
        sections = [(h, c) for h, c in to_html.divide_into_sections(man)]

        assert len(sections) == expected_sections_number

    expected_sections = [
        [],
        [
            Section('', [Subsection('', [
                SimpleParagraph([
                    r'.\\" MAN PAGE COMMENTS to',
                    r'.\\"   Chet Ramey',
                    r'.\\"   Case Western Reserve University',
                    r'.\\"   chet.ramey@case.edu',
                    r'.\\"   Last Change: Sun Feb  2 16:21:40 EST 2014',
                    r'.\\" bash_builtins, strip all but Built-Ins section'
                ])
            ])])
        ],
        [
            Section('NAME', []),
            Section('SYNOPSIS', []),
            Section('COPYRIGHT', [])
        ],
        [
            Section('DESCRIPTION', [Subsection('', [
                SimpleParagraph([
                    'Bash is an sh-compatible command language interpreter '
                    'that ',
                    'executes commands read from the standard input or from '
                    'a file'
                ])
            ])])
        ],
        [
            Section('OPTIONS', [Subsection('Arrays', [])])
        ],
        [
            Section('SHELL GRAMMAR', [Subsection('Simple Commands', [
                SimpleParagraph([
                    r'A \fIsimple command\fP is a sequence of optional '
                    r'variable '
                ]),
                HangingParagraph(
                    4,
                    r'assignments followed by \fBblank\fP-separated words and',
                    [r'\fIname\fP=\fB(\fPvalue\fI1\fP ...']
                ),
                IndentedParagraph(4, r'\(bu', [
                    r'redirections, and terminated by a \fIcontrol operator\fP'
                ]),
                TaggedParagraph(4, r'\(bu', [
                    r'The return value of a \fIsimple command\fP is its exit '
                    r'status'
                ])
            ])])
        ]
    ]

    @pytest.mark.parametrize('man_content, expected_sections',
                             zip(mans_contents, expected_sections),
                             ids=mans_names)
    def test_get_sections(self, man_content, expected_sections):
        """
        to_html.get_sections правильно создаёт секции
        """
        man = StringIO('\n'.join(man_content))
        sections = [s for s in to_html.get_sections(man)]

        assert sections == expected_sections


class TestSubsections:
    """
    Деление, создание и конвертация подразделов
    """
    sections_content = [
        [],
        [
            'bash - GNU Bourne-Again SHell',
            'Bash is an sh-compatible command language interpreter',
            'Bash is intended to be a conformant'
        ],
        [
            '.SS Fight Fire With Fire',
            '.SS Under Your Nose'
        ],
        [
            '.SS Positional Parameters',
            '.HP 4',
            'A positional parameter is a parameter',
            'The shell treats several parameters',
            '.SS Simple Commands',
            '.PP',
            'A simple command is a sequence',
            '.SS Pipelines',
            '.IP \\(bu 4',
            'A pipeline is a sequence',
            '.SS Lists',
            '.TP 4',
            '\\ea',
            'A list is a sequence'
        ]
    ]

    sections_names = [
        'empty',
        'headless_with_simple_paragraph',
        'two_contentless',
        'four_simple_with_all_paragraphs_type'
    ]

    divided_subsections = [
        [],
        [
            ('', ['bash - GNU Bourne-Again SHell',
                  'Bash is an sh-compatible command language interpreter',
                  'Bash is intended to be a conformant'])
        ],
        [
            ('Fight Fire With Fire', []),
            ('Under Your Nose', []),
        ],
        [
            ('Positional Parameters', ['.HP 4',
                                       'A positional parameter is a parameter',
                                       'The shell treats several parameters']),
            ('Simple Commands', ['.PP',
                                 'A simple command is a sequence']),
            ('Pipelines', ['.IP \\(bu 4',
                           'A pipeline is a sequence']),
            ('Lists', ['.TP 4',
                       '\\ea',
                       'A list is a sequence'])
        ]
    ]

    @pytest.mark.parametrize(
        'section_content, expected_subsections',
        zip(sections_content, divided_subsections),
        ids=sections_names)
    def test_divide_into_subsections(
            self, section_content, expected_subsections):
        """
        to_html.divide_into_subsection правильно разбивает содержимое (
        список строк) раздела на подразделы
        """
        subsections = [
            s for s in to_html.divide_into_subsection(section_content)]

        assert subsections == expected_subsections

    expected_subsections_number = [0, 1, 2, 4]

    @pytest.mark.parametrize(
        'section_content, expected_subsections_number',
        zip(sections_content, expected_subsections_number),
        ids=sections_names)
    def test_divide_into_subsections_number_of_subsections(
            self, section_content, expected_subsections_number):
        """
        to_html.divide_into_subsections делит раздел на правильное кол-во
        подразделов
        """
        subsections = [
            sub for sub in to_html.divide_into_subsection(section_content)]

        assert len(subsections) == expected_subsections_number

    expected_subsections = [
        [],
        [
            Subsection('', [
                SimpleParagraph([
                    'bash - GNU Bourne-Again SHell',
                    'Bash is an sh-compatible command language interpreter',
                    'Bash is intended to be a conformant'])])
        ],
        [
            Subsection('Fight Fire With Fire', []),
            Subsection('Under Your Nose', [])
        ],
        [
            Subsection('Positional Parameters', [
                HangingParagraph(4, 'A positional parameter is a parameter',
                                 ['The shell treats several parameters'])
            ]),
            Subsection('Simple Commands', [
                SimpleParagraph(['A simple command is a sequence'])
            ]),
            Subsection('Pipelines', [
                IndentedParagraph(4, '\\(bu', ['A pipeline is a sequence'])
            ]),
            Subsection('Lists', [
                TaggedParagraph(4, '\\ea', ['A list is a sequence'])
            ])
        ]
    ]

    @pytest.mark.parametrize('section_content, expected_subsections',
                             zip(sections_content, expected_subsections),
                             ids=sections_names)
    def test_get_subsections(self, section_content, expected_subsections):
        """
        to_html.get_subsections правильно создаёт подразделы из содержимого
        раздела
        """
        subsections = [s for s in to_html.get_subsections(section_content)]

        assert subsections == expected_subsections


class TestParagraphs:
    """
    Деление, создание и конвертация параграфов
    """
    subsections_content = [
        [
            'bash - GNU Bourne-Again SHell'
        ],
        [

        ],
        [
            'Redirection of input causes the file',
            '.PP',
            'Bash is an sh-compatible command language interpreter',
            'Bash is intended to be a conformant'
        ],
        [
            '.LP',
            'Note that the order of redirections is significant',
            '.PP',
            'directs both standard output',
            'while the command',
            '.P',
            'Do not read and execute the system wide'
        ],
        [
            '.LP',
            '.PP',
            '.P',
            '.HP',
            '.IP',
            '.TP',
        ],
        [
            '.LP',
            'How was the math test?',
            '.PP',
            "She wrote him a long letter, but he didn't read it",
            '.P',
            'The sky is clear; the stars are twinkling',
            '.HP 5',
            'There were white out conditions in the town;',
            'subsequently, the roads were impassable.',
            r'.IP \(bu 4',
            'Christmas is coming',
            '.TP 4',
            r'.B \ea',
            'She folded her handkerchief neatly'
        ]
    ]

    paragraphs_names = ['tagless',
                        'emtpy',
                        'tagless, simple_p',
                        'all simple paragraphs',
                        'contentless',
                        'all paragraphs']

    all_simple_paragraphs = [
        SimpleParagraph([
            'Note that the order of redirections is significant'
        ]),
        SimpleParagraph([
            'Do not read and execute the system wide'
        ]),
        SimpleParagraph([
            'directs both standard output',
            'while the command'
        ])
    ]

    simple_paragraphs_names = ['one_sentence_1',
                               'one_sentence_2',
                               'two_sentences']

    converted_simple_paragraphs = [
        '<p class="simple-paragraph paragraph">'
        'Note that the order of redirections is significant'
        '</p>',
        '<p class="simple-paragraph paragraph">'
        'Do not read and execute the system wide'
        '</p>',
        '<p class="simple-paragraph paragraph">'
        'directs both standard output '
        'while the command'
        '</p>'
    ]

    @pytest.mark.parametrize('paragraph, expected_paragraph',
                             zip(all_simple_paragraphs,
                                 converted_simple_paragraphs),
                             ids=simple_paragraphs_names)
    def test_convert_simple_paragraph(self, paragraph, expected_paragraph):
        """
        to_html.convert_simple_paragraph правильно конвертирует обычный
        параграф
        """
        converted = to_html.convert_simple_paragraph(paragraph)

        assert converted == expected_paragraph

    all_hanging_paragraphs = [
        HangingParagraph(None, '', [
            'Playing For Keeps',
            'Par For the Course'
        ]),
        HangingParagraph(8, '', [
            'Cut To The Chase',
            'Jack of All Trades Master of None'
        ]),
        HangingParagraph(None, 'Tug of war', [
            'Drawing a Blank',
            'Tough It Out'
        ]),
        HangingParagraph(4, 'Break the ice', [
            'When the Rubber Hits the Road',
            "Money Doesn't Grow On Trees"
        ])
    ]

    hanging_paragraphs_names = ['without_indent_and_hang',
                                'without_hang',
                                'without_indent',
                                'with_indent_and_hang']

    converted_hanging_paragraphs = [
        '<span class="hang"></span>'
        f'<p class="hanging-paragraph paragraph" '
        f'style="padding-left: {default_paragraph_indent}em">'
        'Playing For Keeps '
        'Par For the Course'
        '</p>',
        '<span class="hang"></span>'
        f'<p class="hanging-paragraph paragraph" style="padding-left: 8em">'
        'Cut To The Chase '
        'Jack of All Trades Master of None'
        '</p>',
        '<span class="hang">Tug of war</span>'
        f'<p class="hanging-paragraph paragraph" '
        f'style="padding-left: {default_paragraph_indent}em">'
        'Drawing a Blank '
        'Tough It Out'
        '</p>',
        '<span class="hang">Break the ice</span>'
        f'<p class="hanging-paragraph paragraph" style="padding-left: 4em">'
        'When the Rubber Hits the Road '
        "Money Doesn't Grow On Trees"
        '</p>'
    ]

    @pytest.mark.parametrize('paragraph, expected_paragraph',
                             zip(all_hanging_paragraphs,
                                 converted_hanging_paragraphs),
                             ids=hanging_paragraphs_names)
    def test_convert_hanging_paragraph(self, paragraph, expected_paragraph):
        """
        to_html.convert_hanging_paragraph правильно конвертирует висячий
        параграф
        """
        converted = to_html.convert_hanging_paragraph(paragraph)

        assert converted == expected_paragraph

    all_indented_paragraphs = [
        IndentedParagraph(None, None, [
            'In The Red',
            'Lickety Split'
        ]),
        IndentedParagraph(None, "*", [
            'Poke Fun At',
            'Eat My Hat'
        ]),
        IndentedParagraph(4, None, [
            'Mouth-watering',
            'Hit Below The Belt'
        ]),
        IndentedParagraph(4, "*", [
            'A Dime a Dozen',
            'Jaws of Death'
        ])
    ]

    indented_paragraphs_names = ['without_indent_and_hang_tag',
                                 'without_indent',
                                 'without_hang_tag',
                                 'with_indent_and_hang_tag']

    indented_template = ('<div class="indented-paragraph-container">'
                         '<span class="hang-tag">{hang_tag}</span>'
                         '<p class="indented-paragraph paragraph" '
                         'style="padding-left: {pad}em">'
                         '{s1} {s2}'
                         '</p>'
                         '</div>')

    converted_indented_paragraphs = [
        indented_template.format(hang_tag='', pad=default_paragraph_indent,
                                 s1='In The Red', s2='Lickety Split'),
        indented_template.format(hang_tag='*', pad=default_paragraph_indent,
                                 s1='Poke Fun At', s2='Eat My Hat'),
        indented_template.format(hang_tag='', pad=4,
                                 s1='Mouth-watering', s2='Hit Below The Belt'),
        indented_template.format(hang_tag='*', pad=4,
                                 s1='A Dime a Dozen', s2='Jaws of Death'),
    ]

    @pytest.mark.parametrize('paragraph, expected_paragraph',
                             zip(all_indented_paragraphs,
                                 converted_indented_paragraphs),
                             ids=indented_paragraphs_names)
    def test_convert_indented_paragraph(self, paragraph, expected_paragraph):
        """
        to_html.convert_indented_paragraph правильно конвертирует параграф с
        отступом
        """
        converted = to_html.convert_indented_paragraph(paragraph)

        assert converted == expected_paragraph

    all_tagged_paragraphs = [
        TaggedParagraph(None, None, [
            'In The Red',
            'Lickety Split'
        ]),
        TaggedParagraph(None, "*", [
            'Poke Fun At',
            'Eat My Hat'
        ]),
        TaggedParagraph(4, None, [
            'Mouth-watering',
            'Hit Below The Belt'
        ]),
        TaggedParagraph(4, "*", [
            'A Dime a Dozen',
            'Jaws of Death'
        ])
    ]

    tagged_paragraphs_names = ['without_indent_and_hang_tag',
                               'without_indent',
                               'without_hang_tag',
                               'with_indent_and_hang_tag']

    tagged_template = ('<div class="tagged-paragraph-container">'
                       '<span class="hang-tag">{hang_tag}</span>'
                       '<p class="tagged-paragraph paragraph" '
                       'style="padding-left: {pad}em">'
                       '{s1} {s2}'
                       '</p>'
                       '</div>')

    converted_tagged_paragraphs = [
        tagged_template.format(hang_tag='', pad=default_paragraph_indent,
                               s1='In The Red', s2='Lickety Split'),
        tagged_template.format(hang_tag='*', pad=default_paragraph_indent,
                               s1='Poke Fun At', s2='Eat My Hat'),
        tagged_template.format(hang_tag='', pad=4,
                               s1='Mouth-watering', s2='Hit Below The Belt'),
        tagged_template.format(hang_tag='*', pad=4,
                               s1='A Dime a Dozen', s2='Jaws of Death'),
    ]

    @pytest.mark.parametrize('paragraph, expected_paragraph',
                             zip(all_tagged_paragraphs,
                                 converted_tagged_paragraphs),
                             ids=tagged_paragraphs_names)
    def test_convert_tagged_paragraph(self, paragraph, expected_paragraph):
        """
        to_html.convert_tagged правильно конвертирует параграф с биркой
        """
        converted = to_html.convert_tagged_paragraph(paragraph)

        assert converted == expected_paragraph

    all_type_paragraphs_names = chain(
        (f'simple_{t}' for t in simple_paragraphs_names),
        (f'{p}_{t}' for p in ['hanging', 'indented', 'tagged']
         for t in ['without_indent_and_hang', 'without_hang',
                   'without_indent', 'with_indent_and_hang']))

    @pytest.mark.parametrize(
        'paragraph, expected_paragraph',
        zip(chain(all_simple_paragraphs, all_hanging_paragraphs,
                  all_indented_paragraphs, all_tagged_paragraphs),
            chain(converted_simple_paragraphs, converted_hanging_paragraphs,
                  converted_indented_paragraphs, converted_tagged_paragraphs)),
        ids=list(all_type_paragraphs_names))
    def test_convert_paragraph(self, paragraph, expected_paragraph):
        """
        to_html.convert_paragraph правильно конвертирует параграф
        """
        converted = to_html.convert_paragraph(paragraph)

        assert converted == expected_paragraph

    expected_paragraphs = [
        [
            SimpleParagraph(['bash - GNU Bourne-Again SHell'])],
        [],
        [
            SimpleParagraph(['Redirection of input causes the file']),
            SimpleParagraph([
                'Bash is an sh-compatible command language interpreter',
                'Bash is intended to be a conformant'])
        ],
        [
            SimpleParagraph(
                ['Note that the order of redirections is significant']),
            SimpleParagraph([
                'directs both standard output',
                'while the command']),
            SimpleParagraph([
                'Do not read and execute the system wide'
            ])
        ],
        [],
        [
            SimpleParagraph([
                'How was the math test?'
            ]),
            SimpleParagraph([
                "She wrote him a long letter, but he didn't read it"
            ]),
            SimpleParagraph([
                'The sky is clear; the stars are twinkling'
            ]),
            HangingParagraph(5, 'There were white out conditions in the town;',
                             ['subsequently, the roads were impassable.']),
            IndentedParagraph(4, r'\(bu', ['Christmas is coming']),
            TaggedParagraph(4, r'.B \ea',
                            ['She folded her handkerchief neatly'])
        ]
    ]

    @pytest.mark.parametrize(
        'subsection_content, expected_paragraphs',
        zip(subsections_content, expected_paragraphs),
        ids=paragraphs_names)
    def test_get_paragraphs(self, subsection_content, expected_paragraphs):
        """
        to_html.get_paragraphs правильно создаёт параграфы из содержания
        подраздела
        """
        paragraphs = [p for p in to_html.get_paragraphs(subsection_content)]

        assert paragraphs == expected_paragraphs
