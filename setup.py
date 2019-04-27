from setuptools import setup, find_packages

setup(

    name='finalmark',
    version='1.0',
    author='Matheus Melo',
    install_requires=[
        "beautifulsoup4==4.6.3",
        "html5lib==1.0.1",
        "mechanize==0.3.7"
    ],
    packages=find_packages()
)
