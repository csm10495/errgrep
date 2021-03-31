![Run tests](https://github.com/csm10495/errgrep/workflows/Run%20tests/badge.svg) [![PyPI version](https://badge.fury.io/py/errgrep.svg)](https://badge.fury.io/py/errgrep)

# errgrep

A cli for grep'ing through log files to find log statements matching a regex. Internally line timestamps, delimit 'log lines'. A line without a timestamp is considered to be part of the prior line. This allows for errgrep to find more complete exceptions (or other events) than just a single line from a file.

# Installation
```
pip install errgrep
```

# Usage

[CLI_OUTPUT_MARKER]::

```
usage: errgrep [-h] [-i] [-a] regex [files [files ...]]

errgrep helps grep for multi-line statements in log files.

positional arguments:
  regex                 The regex used to search to search for statements.
  files                 Files to search. A "-" corresponds with reading from
                        stdin. If no files are given, will search stdin.

optional arguments:
  -h, --help            show this help message and exit
  -i, --ignore-case     If given, ignore case in search.
  -a, --allow-timestamp-format-changes
                        If given, assume the timestamp format can change
                        within a given file.

```

[CLI_OUTPUT_MARKER]::

# Example
```
errgrep --ignore-case error file.txt
```

See [https://csm10495.github.io/errgrep/](https://csm10495.github.io/errgrep/) for full API documentation.

## License
MIT License