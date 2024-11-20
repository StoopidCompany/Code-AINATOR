import argparse
from .controllers.scanner import scan_project, delete_project
from .controllers.quick_summary import quick_summary

def main():
    parser = argparse.ArgumentParser(
        prog='codeainator',
        description='Codeainator CLI Tool - Process code directories.'
    )
    parser.add_argument(
        '-d', '--dir', '--directory',
        help='Path to the directory to process'
    )
    parser.add_argument(
        '-a', '--analyze',
        action='store_true',
        help='Analyze files using AI (requires API access)'
    )
    parser.add_argument(
        '-r', '--remove',
        action='store_true',
        help='Remove database entries related to the directory'
    )
    parser.add_argument(
        '-q', '--quick',
        action='store_true',
        help='Perform a quick summary of the directory'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file to save the result'
    )
    args = parser.parse_args()

    if args.dir:
        if args.remove:
            delete_project(args.dir)
        elif args.analyze:
            output = scan_project(args.dir)
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
            else:
                print(output)
        elif args.quick:
            output = quick_summary(args.dir)
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
            else:
                print(output)
        else:
            parser.print_help()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()