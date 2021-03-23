import argparse

from .log_line import LogLine

def errgrep(file_path, log_line, regex, ignore_case):
    print (f"Searching: {file_path}...")
    for match in log_line.iter_log_lines_with_regex(regex, ignore_case=ignore_case):
        print('  ' + match.log_message.replace('\n', '\n  ').rstrip(' '))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='errgrep helps grep for multi-line statements in log files.')
    parser.add_argument('-i', '--ignore-case', action='store_true', help='If given, ignore case in search.')
    parser.add_argument('regex', help='The regex used to search to search for statements.')
    parser.add_argument('files', nargs='*', help='Files to search. A "-" corresponds with reading from stdin.')

    args = parser.parse_args()

    log_lines_and_files = [(LogLine(log_file=l), l) for l in args.files]

    tail_stdin = False
    for log_line, file_path in log_lines_and_files:
        if file_path == '-':
            tail_stdin = True
            continue

        errgrep(file_path, log_line, args.regex, args.ignore_case)


    if tail_stdin:
        errgrep('-', LogLine(log_file='-'), args.regex, args.ignore_case)