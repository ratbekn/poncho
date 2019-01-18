import sys  # pragma: no cover
from src.utils import arg_parser  # pragma: no cover
from src.converters import to_html  # pragma: no cover


def main():  # pragma: no cover
    args = arg_parser.parse_arguments(sys.argv[1:])

    with open(args.input_file) as in_file:
        with open(args.output_file, 'w') as out_file:
            for section in to_html.convert(in_file, args.style):
                out_file.write(section)


if __name__ == '__main__':  # pragma: no cover
    main()
