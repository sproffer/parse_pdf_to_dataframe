# Parse PDF files and put contents into Pandas dataframe

## Summary
Sample build and invocation of Python modules, to parse PDF files, 
extract headers and contents, and put them to Padndas dataframe, 
and output to a CSV file. 

To be incorporated into AI processing with consumed PDF contents.

#### Dataframe format: 
     df = pd.DataFrame(None, columns=['pdf_file', 'header', 'content', 'combined'])

##  Package required: 
     (library version lagging for python3.11, so use 3.9)
     /usr/local/bin/python3 -m pip install py-pdf-parser\[dev\]
     /usr/local/bin/python3 -m pip install cython
     /usr/local/bin/python3 -m pip install tkinter
     /usr/local/bin/python3 -m pip install  py2app
     brew install python-tk@3.9
     brew install freetype imagemagick

## Create a MacOS app

### generate setup.py and customize content - for example, add Data files
    py2applet --make-setup pdf-to-dataframe.py
*****manually verify and edit setup.py*****

###  build app
    rm -rf dist build
    /usr/local/bin/python3 setup.py  py2app --packages charset_normalizer
*****dynamically imported packages are not imported during build, explicitly include them*****

##  Run the app, with launched Tkinter text console
    pdf-to-dataframe.app

*****<a href=https://youtu.be/ba7tWWsO7bA target=yt>Screen capture of a sample run</a>*****

2 sample PDF files included.

