from setuptools import setup, find_packages
from essay_builder import __version__

setup(
    name="gost",
    version=__version__,
    description="Academic Essay Templater — GTK4/libadwaita app for LaTeX and Typst templates",
    author="Cal St Francis",
    url="https://github.com/calstfrancis/gost",
    license="GPL-3.0-or-later",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "PyGObject",
    ],
    package_data={
        "essay_builder": ["fonts/*.ttf", "fonts/*.otf", "*.svg"],
    },
    entry_points={
        "console_scripts": [
            "gost=essay_builder.app:main",
        ],
    },
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: Text Processing :: Markup :: LaTeX",
    ],
)
