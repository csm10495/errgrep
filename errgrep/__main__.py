import argparse
import time

from .log_line import LogLine

def errgrep(file_path, log_line, regex, ignore_case):
    print (f"Searching: {file_path if file_path != '-' else '<stdin>'}...")
    for match in log_line.iter_log_lines_with_regex(regex, ignore_case=ignore_case):
        print('  ' + match.log_message.replace('\n', '\n  ').rstrip(' '))

def main():
    parser = argparse.ArgumentParser(description='errgrep helps grep for multi-line statements in log files.')
    parser.add_argument('-i', '--ignore-case', action='store_true', help='If given, ignore case in search.')
    parser.add_argument('-a', '--allow-timestamp-format-changes', action='store_true', help='If given, assume the timestamp format can change within a given file.')
    parser.add_argument('regex', help='The regex used to search to search for statements.')
    parser.add_argument('files', nargs='*', help='Files to search. A "-" corresponds with reading from stdin. If no files are given, will search stdin.')

    args = parser.parse_args()

    start_time = time.time()

    log_lines_and_files = [(LogLine(log_file=l, allow_timestamp_format_changes=args.allow_timestamp_format_changes), l) for l in args.files]

    tail_stdin = (len(log_lines_and_files) == 0)

    for log_line, file_path in log_lines_and_files:
        if file_path == '-':
            tail_stdin = True
            continue

        errgrep(file_path, log_line, args.regex, args.ignore_case)

    if tail_stdin:
        try:
            errgrep('-', LogLine(log_file='-'), args.regex, args.ignore_case)
        except KeyboardInterrupt:
            pass

    end_time = time.time()

    print(f"Finished in {end_time - start_time:.4f} seconds.")

if __name__ == '__main__':
    main()
