from setuptools import setup, find_packages

# Replace these placeholder values with your actual package info
setup(
    name='paper2speech',
    version='0.2.0',
    description='Convert pdf papers and books to speech using Nougat and Google Cloud Text to Speech',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/kaieberl/paper2speech',
    author='Kai Eberl',
    author_email='kai.eberl@tum.de',
    license='MIT',
    packages=find_packages(),
    py_modules=["paper2speech"],
    install_requires=[
        'nougat',
        'transformers==4.37.2',
        'nougat-ocr==0.1.8',
        'beautifulsoup4',
        'markdown-it-py[plugins]',
        'google-cloud-texttospeech',
        'google-auth'
    ],
    entry_points={
        "console_scripts": [
            "paper2speech = paper2speech:main",
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
