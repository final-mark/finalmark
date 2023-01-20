from setuptools import setup, find_packages

setup(

    name='finalmark',
    version='1.0',
    author='Matheus Melo',
    install_requires=[
        "beautifulsoup4==4.6.3",
        "html5lib==1.0.1",
        "mechanize==0.4.6",
        "prometheus_client==0.7.1"
    ],
    packages=find_packages()
)
