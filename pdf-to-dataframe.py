#!/usr/local/bin/python3
#
#  Parse PDF files from command line arguments and puyt into Pandas DataFrame
#
#  package installed: (version lagging for python3.11)
#     /usr/local/bin/python3 -m pip install py-pdf-parser\[dev\]
#     /usr/local/bin/python3 -m pip install cython
#     brew install python-tk@3.9
#     brew install freetype imagemagick
#
from py_pdf_parser.loaders import load_file
import pandas as pd
import sys, time, random, os
import tkfuncs, pdffuncs

randp = random.randrange(100)
x = 50 + randp
y = 100 + randp
text_window = tkfuncs.createTextWindow("App Console", height=40, width=160, posx=x, posy=y)

# assume the command line arguments provide one or more PDF file names
df = pd.DataFrame(None, columns=['pdf_file', 'header', 'content', 'combined'])

def processfile(afile):
    global text_window
    global df

    tkfuncs.write_text(text_window, "\nProcessing file "+afile + "...\n\n", True, "boldhighlight")
    try:
        pdffuncs.parsepdf(df, afile)
        tkfuncs.write_text(text_window, df.to_string(columns={'pdf_file','header'}, max_rows=4, col_space=3), True, "normalfont")
        tkfuncs.promptforinput(text_window, 'Enter more PDF filename: ', processfile, saveexit)
    except Exception as err:
        tkfuncs.write_text(text_window, f' error parsing file {afile=}: {err=} \n', True, "italicfont")
        tkfuncs.promptforinput(text_window, '\n\nTry again with PDF filename: ', processfile, saveexit)

def saveexit():
    global df
    tkfuncs.write_text(text_window, 'graceful exit, write to file ' + os.getcwdb().decode('utf-8') + '/outdata.csv....\n\n', True, 'italicfont')
    df.to_csv('outdata.csv', sep="\t")
    tkfuncs.delayexit(10)

# main
tkfuncs.promptforinput(text_window, 'Enter PDF file name: ', processfile, saveexit)
text_window.mainloop()
