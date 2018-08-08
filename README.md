# hfy_ebook
A tool to create ebooks from /r/HFY posts

Currently only the Jenkinsverse canon posts are supported.

This program consists of two parts. The first part is a Python script that creates a .spec file for you. The second part is node based and that part creates the actual ebook based on the .spec file.

## Installation - Python
Create a virtualenv and install the software in requirements.txt:
```
virtualenv venv
source venv/bin/activate
pip install -r python/requirements.txt
```

After installation of the Python code, you have to modify two variables in the script, so it has your reddit.com API key in it. Open python/hfy.py in your text editor of choice and set REDDIT\_CLIENT\_ID and REDDIT\_CLIENT\_SECRET. You can obtain these by going to https://www.reddit.com/prefs/apps/ and clicking the 'create app' button on the bottom.

## Installation - Node
```
npm install
```

## Running the tools
Run the Python tool to create the .spec file:
```
source venv/bin/activate
python python/hfy.py
```
Then follow that by creating the ebook:
```
node ebook.js HFY_Canon.spec
```
You can find a HTML, epub and LaTeX version in the output folder.
