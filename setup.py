from setuptools import setup
import os
import sys

THIS_FOLDER = os.path.abspath(os.path.dirname(__file__))

def getVersion():
    with open(os.path.join(THIS_FOLDER, 'errgrep', '__init__.py'), 'r') as f:
        text = f.read()

    for line in text.splitlines():
        if line.startswith('__version__'):
            version = line.split('=', 1)[1].replace('\'', '').replace('"', '')
            return version.strip()

    raise EnvironmentError("Unable to find __version__!")

setup(
    name='errgrep',
    author='csm10495',
    author_email='csm10495@gmail.com',
    url='http://github.com/csm10495/errgrep',
    version=getVersion(),
    packages=['errgrep'],
    license='MIT License',
    python_requires='>=3,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*,!=3.6.*',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    long_description_content_type="text/markdown",
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    entry_points = {
        'console_scripts': ['errgrep=errgrep.__main__:main'],
    },
    include_package_data = True,
    install_requires=['pytest', 'python-dateutil', 'colorama']
)