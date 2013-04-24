from distutils.core import setup

setup(
    name="jirafe-python-client",
    version="0.1",
    url="https://github.com/jirafe/jirafe-python-client",
    packages=["jirafe"],
    license="Copyright 2013, Jirafe under MIT License",
    description="Client library for the Jirafe api",
    long_description=open("README.md").read(),
    install_requires=['requests'],
)
