import os
import sys

import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))
from exceptions import arg_parser_exceptions
from utils import arg_parser


def test_if_no_arguments_throw_exception():
    argv = []

    with pytest.raises(arg_parser_exceptions.NoArgumentsError):
        arg_parser.parse_arguments(argv)


def test_pars_input_file():
    argv = ['input']

    args = arg_parser.parse_arguments(argv)

    assert args.input_file == 'input'


def test_if_output_file_not_specified_it_has_same_name_as_input_file():
    argv = ['host']

    args = arg_parser.parse_arguments(argv)

    assert args.output_file == 'host'


def test_if_output_file_specified_parse_it():
    argv = ['groff', '-o', 'groff_html']

    args = arg_parser.parse_arguments(argv)

    assert args.output_file == 'groff_html'
