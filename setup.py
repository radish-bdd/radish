# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

import os
import re
import codecs
from setuptools import setup, find_packages


def read_metafile(path):
    """
        Read contents from given metafile
    """
    with codecs.open(path, "rb", "utf-8") as f:
        return f.read()


def get_meta(name):
    """
        Get some metdata with the give name from the
        Meta file
    """
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=name.upper()),
        __META_DATA__, re.M
    )

    if not meta_match:
        raise RuntimeError("Unable to find __{0}__ string.".format(name))
    return meta_match.group(1)


__META_FILE__ = os.path.join("radish", "__init__.py")
__META_DATA__ = read_metafile(__META_FILE__)

setup(
    name="radish-bdd",
    version=get_meta("version"),
    license=get_meta("license"),
    description=get_meta("description"),
    author=get_meta("author"),
    author_email=get_meta("author_email"),
    maintainer=get_meta("author"),
    maintainer_email=get_meta("author_email"),
    platforms=["Linux", "Windows", "MAC OS X"],
    url=get_meta("url"),
    download_url=get_meta("download_url"),
    bugtrack_url=get_meta("bugtrack_url"),
    packages=find_packages(),
    package_data={"": ["radish/languages/*", "*.md"]},
    install_requires=[
        "docopt",
        "pysingleton",
        "colorful>=0.01.03",
        "lxml",
        "ipython",
        "coverage",
        "PyYAML"
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "radish = radish.main:main",
            'radish-test = radish.testing.__main__:main',
        ]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Microsoft :: Windows :: Windows 7",
        "Operating System :: Microsoft :: Windows :: Windows XP",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation",
        "Topic :: Education :: Testing",
        "Topic :: Software Development",
        "Topic :: Software Development :: Testing"
    ],
)
