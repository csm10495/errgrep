import argparse
import re
import time
from colorama import init, Fore

from .log_line import LogLine

def get_text_with_color_for_regex_match(regex: str, text: str, ignore_case: bool, color: str) -> str:
    '''
    Take this text, find regex matches and apply the given color to that match
    '''
    matches = re.findall(regex, text, re.IGNORECASE if ignore_case else 0)
    for m in matches:
        text = text.replace(m, color + m + Fore.RESET)
    return text

def indent(text):
    '''
    Indents the given string by 2 spaces per line
    '''
    return '  ' + text.replace('\n', '\n  ').rstrip(' ')

def get_context(log_line: LogLine, context: int) -> tuple:
    '''
    Follows log_lines to get a given amount of contextual log_lines
    '''
    before_context_lines = []
    after_context_lines = []
    this_line = log_line
    before_line = log_line
    after_line = log_line

    for idx in range(context):
        if before_line:
            if before_line.previous_line:
                before_line = before_line.previous_line
            else:
                before_line = None

            if before_line:
                before_context_lines.append(before_line)

        if after_line:
            possible_after_line = after_line.get_next_log_line()
            if possible_after_line:
                after_line = possible_after_line
            else:
                after_line = None

            if after_line:
                after_context_lines.append(after_line)

    return before_context_lines, after_context_lines

def errgrep(file_path: str, log_line: LogLine, regex: str, ignore_case: bool, context: int) -> None:
    '''
    Prints out the errgrep results starting with the given LogLine
    '''
    print (f"Searching: {file_path if file_path != '-' else '<stdin>'}...")
    for match in log_line.iter_log_lines_with_regex(regex, ignore_case=ignore_case):
        before_context_lines, after_context_lines = get_context(match, context)

        for line in before_context_lines:
            print(Fore.CYAN + indent(line.log_message) + Fore.RESET)
        print(get_text_with_color_for_regex_match(regex, indent(match.log_message), ignore_case, Fore.RED))
        for line in after_context_lines:
            print(Fore.CYAN + indent(line.log_message) + Fore.RESET)

def modify_update_args(args: argparse.Namespace, unknown_args: argparse.Namespace) -> argparse.Namespace:
    '''
    Find the -NUM arg if its there. Adds it to arg as args.context
    '''
    if args.context == 0:
        num_arg_regex = r'-(\d*)'

        # look in regex param
        match = re.findall(num_arg_regex, args.regex)
        if match and match[0]:
            args.context = int(match[0])
            if not args.files:
                raise argparse.ArgumentError("Missing regex parameter")
            args.regex = args.files[0]
            args.files = args.files[1:]
        else:
            # look in each file param :/
            # if the -NUM is after (or in the files) it could be in unknown_args
            args.files = args.files + unknown_args
            for idx, itm in enumerate(args.files):
                match = re.findall(num_arg_regex, itm)
                if match and match[0]:
                    args.context = int(match[0])
                    del args.files[idx]
                    break

    return args

def main():
    ''' main entry point '''
    # Colorama init
    init()

    parser = argparse.ArgumentParser(description='errgrep helps grep for multi-line statements in log files.')
    parser.add_argument('-i', '--ignore-case', action='store_true', help='If given, ignore case in search.')
    parser.add_argument('-a', '--allow-timestamp-format-changes', action='store_true', help='If given, assume the timestamp format can change within a given file.')
    parser.add_argument('-C', '--context', help='If given, the number of lines of context to print around matching lines. Can also be given as -NUM.', type=int, default=0)
    parser.add_argument('regex', help='The regex used to search to search for statements.')
    parser.add_argument('files', nargs='*', help='Files to search. A "-" corresponds with reading from stdin. If no files are given, will search stdin.')

    args = modify_update_args(*parser.parse_known_args())

    start_time = time.time()

    log_lines_and_files = [(LogLine(log_file=l, allow_timestamp_format_changes=args.allow_timestamp_format_changes), l) for l in args.files]

    tail_stdin = (len(log_lines_and_files) == 0)

    for log_line, file_path in log_lines_and_files:
        if file_path == '-':
            tail_stdin = True
            continue

        errgrep(file_path, log_line, args.regex, args.ignore_case, args.context)

    if tail_stdin:
        try:
            errgrep('-', LogLine(log_file='-'), args.regex, args.ignore_case, args.context)
        except KeyboardInterrupt:
            pass

    end_time = time.time()

    print(f"Finished in {end_time - start_time:.4f} seconds.")

if __name__ == '__main__':
    main()
