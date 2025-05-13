# Cipher by BadBunnies

## Roster:
- Project Manager | Ethan Sie
- Wen Zhang
- Stanley Hoo
- Raymond Lin

## Site Description:

This project is focused on handwriting recognition using machine learning. We aim to convert handwritten documents into digital text by processing user-uploaded images or PDFs. While we start by cleaning and analyzing the images, our main goal is to train a model to recognize handwriting accurately. Since handwriting varies greatly between users, we hope to improve the model over time with user corrections. To make the project more interactive, users will be able to manage their own handwriting samples, view the transcribed text, and optionally contribute to improving the model’s accuracy. If possible, we will also work on a feature that will allow users to create their own font based on their handwriting. 

## Install Guide

Our project can be installed locally by carrying out the following steps. Users may also skip installation and go straight to the website at the top of our Launch Codes.
1. Clone and move into this repository
```
$ git clone git@github.com:chloepwong/p04.git
```
```
$ cd p04
```
2. Create a virtual environment
```
$ python3 -m venv foo
```
3. Activate the virtual environment: Linux/MacOS
```
$ . foo/bin/activate
```
3. Activate the virtual environment: Windows
```
$ foo\Scripts\activate
```
4. Install required packages
```
$ pip install -r requirements.txt
```
## Launch Codes
Our project can be launched locally by carrying out the following steps. Users may also go straight to http://159.223.128.39/.
1. Move into this repository
```
$ cd p04
```
2. Activate the virtual environment: Linux/MacOS
```
$ . foo/bin/activate
```
2. Activate the virtual environment: Windows
```
$ foo\Scripts\activate
```
3. Move into the app directory
```
$ cd app
```
4. Run the Flask app
```
$ python3 __init__.py
```
5. Navigate to localhost: http://127.0.0.1:5000
