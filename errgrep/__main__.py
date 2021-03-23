import argparse

from .log_line import LogLine

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='errgrep helps grep for multi-line statements in log files.')
    parser.add_argument('-i', '--ignore-case', action='store_true', help='If given, ignore case in search.')
    parser.add_argument('regex', help='The regex used to search to search for statements.')
    parser.add_argument('files', nargs='*', help='Files to search. A "-" corresponds with reading from stdin.')

    args = parser.parse_args()

    log_lines_and_files = sorted([(LogLine(log_file=l), l) for l in args.files], key=lambda x: x == '-')

    for log_line, file_path in log_lines_and_files:
        print (f"Searching: {file_path}...")
        for match in log_line.iter_log_lines_with_regex(args.regex, ignore_case=args.ignore_case):
            print('  ' + match.log_message.replace('\n', '\n  ').rstrip(' '))
