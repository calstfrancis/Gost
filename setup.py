from setuptools import setup, find_packages

setup(
    name="gost",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'gost=essay_builder.app:main',
        ],
    },
    install_requires=[
        'pygobject',
        'requests',
        'pyyaml',
        'jinja2',
    ],
)
