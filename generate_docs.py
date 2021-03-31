'''
script to create docs
'''

import os
import pathlib
import re
import shutil
import subprocess
import sys

def add_usage_info_to_readme():
    '''
    This is specific for errgrep. It will add output from errgrep --help to README.md
    '''
    MARKER='\n[CLI_OUTPUT_MARKER]::\n'

    output = subprocess.check_output('errgrep --help', shell=True).decode()

    readme = pathlib.Path('README.md').read_text()
    pre, _, post = readme.split(MARKER)
    full_text = pre + MARKER + '\n```\n' + output + '\n```\n' + MARKER + post
    full_text = full_text.replace('\r\n', '\n')
    pathlib.Path('README.md').write_text(full_text)

if __name__ == '__main__':
    assert subprocess.call([
        sys.executable,
        '-m',
        'pip',
        'install',
        'setuptools',
        'pdoc3',
    ]) == 0, 'Unable to install pdoc3'

    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    assert subprocess.call([
        sys.executable,
        '-m',
        'pdoc',
        '--html',
        'errgrep',
        '-o',
        'docs_tmp',
        '-f'
    ]) == 0, 'Unable to generate docs via pdoc'

    # remove existing docs dir
    shutil.rmtree('docs', ignore_errors=True)

    # remove extra dir nesting and move back to docs/
    shutil.move('docs_tmp/errgrep', 'docs')
    os.rmdir('docs_tmp')

    # special for errgrep
    add_usage_info_to_readme()