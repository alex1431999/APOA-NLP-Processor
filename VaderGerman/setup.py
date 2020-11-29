"""
All the setup required to make the project a library is done here
"""

# For reading requirements.txt
import os

# Setuptools is used to setup the library
import setuptools

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
REQUIREMENTS_PATH = CURRENT_DIR + "/requirements.txt"

install_requires = []
if os.path.isfile(REQUIREMENTS_PATH):
    with open(REQUIREMENTS_PATH) as f:
        install_requires = f.read().splitlines()

setuptools.setup(
    name="VaderGerman",
    version="1.0.0",
    description="The library contains the german Vader sentiment analysis tool",
    url="https://github.com/KarstenAMF/GerVADER.git",
    author="David Devlin",
    author_email="davidaddevlin@gmail.com",
    license="unlicense",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    zip_safe=False,
)
