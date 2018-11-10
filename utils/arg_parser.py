import argparse
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                             os.pardir))
from exceptions import arg_parser_exceptions


def parse_arguments(argv):
    """
    Парсит аргументы комадной строки

    :param list of str argv: список аргументов командной строки sys.argv
    :raise arg_parser_exceptions.NoArgumentsError: если argv пустой
    :returns: распарсенные аргументы командной строки
    :return: argparse.Namespace
    """
    if not argv:
        raise arg_parser_exceptions.NoArgumentsError

    parser = create_parser()

    args = parser.parse_args(argv)

    if not args.output_file:
        args.output_file = args.input_file

    return args


def create_parser():
    """
    Создаёт и инициализирует парсер

    :return: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'input_file', type=str,
        help='исходный файл, который нужно сконвертировать')

    parser.add_argument(
        '-o', '--output_file', type=str, default=None,
        help='название для сконвертированного файла. по умолчанию как у исходного с соответсвующим расширением')

    return parser
