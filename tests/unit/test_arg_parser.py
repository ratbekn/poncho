import os
import pytest
import sys

sys.path.append(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.utils import arg_parser


def test_no_args():
    with pytest.raises(SystemExit):
        arg_parser.parse_arguments([])


def test_parse_input_file():
    argv = ['input']

    args = arg_parser.parse_arguments(argv)

    assert args.input_file == 'input'


def test_if_output_file_not_specified_it_has_same_name_as_input_file():
    argv = ['host']

    args = arg_parser.parse_arguments(argv)

    assert args.output_file == 'host.html'


def test_if_output_file_specified_parse_it():
    argv = ['bash.1', '-o', 'groff_html']

    args = arg_parser.parse_arguments(argv)

    assert args.output_file == 'groff_html'
