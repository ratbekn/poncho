import argparse
import sys
from os import path


def parse_arguments(argv):
    """
    Парсит аргументы комадной строки
    """

    parser = create_parser()

    if not argv:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args(argv)

    if not args.output_file:
        args.output_file = f'{args.input_file}.html'

    return args


def create_parser():
    """
    Создаёт и инициализирует парсер
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'input_file', type=str,
        help='исходный файл, который нужно сконвертировать')

    parser.add_argument(
        '-o', '--output_file', type=str, default=None,
        help='название для сконвертированного файла. '
             'по умолчанию как у исходного с расширением .html')

    parser.add_argument(
        '--style', type=str, default=path.join(r'css\main.css'),
        help='файл css стилизиющий html '
             '(default: %(default)s)'
    )

    return parser
