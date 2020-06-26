import functools
import re
from pathlib import Path

from setuptools import find_packages, setup

#: Holds a list of packages to install with the binary distribution
PACKAGES = find_packages(where="src")
META_FILE = Path("src").absolute() / "radish" / "__init__.py"
KEYWORDS = ["testing", "bdd", "tdd", "gherkin", "cucumber", "automated"]
CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "Intended Audience :: Other Audience",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: Implementation :: CPython",
    "Topic :: Education :: Testing",
    "Topic :: Software Development",
    "Topic :: Software Development :: Testing",
]

#: Holds the runtime requirements for the end user
INSTALL_REQUIRES = [
    "lark-parser==0.7.6a1",
    "click",
    "colorful>=0.5.4",
    "tag-expressions>=1.0.0",
    "parse_type>0.4.0",
    "humanize",
    "PyYAML",
]
#: Holds runtime requirements and development requirements
EXTRAS_REQUIRES = {
    # extras for end users
    "xml": ["lxml"],
    "ipython-debugger": ["ipython"],
    "coverage": ["coverage"],
    # extras for contributors
    "docs": ["sphinx", "towncrier"],
    "tests": ["freezegun", "coverage[toml]", "pytest", "pytest-mock"]
    + ["lxml", "PyYAML"],
}
EXTRAS_REQUIRES["dev"] = (
    EXTRAS_REQUIRES["tests"] + EXTRAS_REQUIRES["docs"] + ["pre-commit"]
)

#: Holds the contents of the README file
with open("README.md", encoding="utf-8") as readme:
    __README_CONTENTS__ = readme.read()


@functools.lru_cache()
def read(metafile):
    """
    Return the contents of the given meta data file assuming UTF-8 encoding.
    """
    with open(str(metafile), encoding="utf-8") as f:
        return f.read()


def get_meta(meta, metafile):
    """
    Extract __*meta*__ from the given metafile.
    """
    contents = read(metafile)
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta), contents, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


setup(
    name="radish-bdd",
    version=get_meta("version", META_FILE),
    license=get_meta("license", META_FILE),
    description=get_meta("description", META_FILE),
    long_description=__README_CONTENTS__,
    long_description_content_type="text/markdown",
    author=get_meta("author", META_FILE),
    author_email=get_meta("author_email", META_FILE),
    maintainer=get_meta("author", META_FILE),
    maintainer_email=get_meta("author_email", META_FILE),
    platforms=["Linux", "Windows", "MAC OS X"],
    url=get_meta("url", META_FILE),
    download_url=get_meta("download_url", META_FILE),
    bugtrack_url=get_meta("bugtrack_url", META_FILE),
    packages=PACKAGES,
    package_dir={"": "src"},
    package_data={"": ["radish/parser/grammer.g"]},
    include_package_data=True,
    python_requires=">=3.5.*",
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRES,
    entry_points={
        "console_scripts": [
            "radish = radish.__main__:cli",
            "radish-test = radish.step_testing.__main__:cli",
            "radish-parser = radish.parser.__main__:cli",
        ]
    },
    keywords=KEYWORDS,
    classifiers=CLASSIFIERS,
)
