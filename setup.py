from setuptools import setup, find_packages

setup(
    name='fileSort',
    version='1.86',
    packages=find_packages(),
    install_requires=[
        'reportlab',
        'Requests',
        'setuptools',
        'pymupdf',
        'PyPDF2'
    ],
)

