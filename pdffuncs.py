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

def updateHeaderRow(df, sizenum, lengthnum):
    if df.loc[(df['font_size'] == sizenum)].any().all():
        if df.loc[ (df['font_size'] == sizenum) & (df['length'] < lengthnum) ].any().all():
            df.loc[df.font_size == sizenum, 'length'] = lengthnum

        c = df.loc[df.font_size == sizenum, 'count']
        c += 1
        df.loc[df.font_size == sizenum, 'count'] = c
    else:
        df.loc[len(df.index)] = [sizenum, lengthnum, 1]

def combined_len(row):
    return row['length'] * row['count']

#  build a header mapping from font size,  h1, h2, h3 and text
#  [font_size, type, ...]
#  where font_size is an integer, type: h1, h2, h3, text
#
#  header h1, h2, h3 has to be less than headermaxlen
#  ignore paragraph with length less than ignore len
#  ignore text with combined length less than ignorecombinedlen
def build_headerdata(pdfdoc, headermaxlen, ignorelen, ignorecombinedlen):
    df = pd.DataFrame(None, columns=['font_size', 'length', 'count'])
    elementlist = pdfdoc.elements;
    for anelem in elementlist:
        fs = int(anelem.font_size)
        tl = len(anelem.text())
        updateHeaderRow(df, fs, tl)

    sortdf = df.sort_values(by="font_size", ascending=False)
    sortdf = sortdf.reset_index(drop=True)
    sortdf['combined_len'] = sortdf.apply(combined_len, axis=1)
    stoph = False
    typecol = ['h1']
    for i in sortdf.index:
        if i == 0:
            continue
        elif i == 1:
            if sortdf.loc[i].length <= headermaxlen:
                typecol.append('h2')
            else:
                typecol.append('text')
                stoph = True
        elif (i == 2) & (stoph == False) :
            if sortdf.loc[i].length <= headermaxlen:
                typecol.append('h3')
            else:
                typecol.append('text')
        else:
            typecol.append('text')
    sortdf['typecol'] = typecol
    # drop 'text' rows max length is ignorelen, page no etc.
    filterdf = sortdf.loc[ (sortdf['length'] > ignorelen) | (sortdf['typecol'] != 'text') ]
    # drop 'text' rows that length * count < ignorecombinedlen, insignificant
    filterdf = filterdf.loc[ (filterdf['combined_len'] > ignorecombinedlen) | (filterdf['typecol'] != 'text')]
    return(filterdf)

#  from fontsize, map to type of section
#  return value could be h1, h2, h3, text, ignore
def headermap(fs, headerdf):
    returntyp = 'ignore'
    if headerdf.loc[ headerdf['font_size'] == fs ].any().all():
        returntyp = headerdf.loc[ headerdf.font_size == fs, 'typecol'].squeeze()
    return(returntyp)

def addrow(df, afile, h1, h2, h3, ctext):
    if len(h1) > 2 and len(ctext) > 100:
        hh = f'{h1} - {h2} - {h3}'
        df.loc[len(df.index)] = [afile, hh, ctext, f'{hh} : {ctext}' ]

# add more contents to dataframe with format of
#   DataFrame(None, columns=['pdf_file', 'header', 'content', 'combined'])
def parsepdf(df, pdffile):
    pdfdoc = load_file(pdffile)
    headerdf = build_headerdata(pdfdoc, 200, 10, 150)
    #write(headerdf.to_string())
    h1 = ''
    h2 = ''
    h3 = ''
    # second scan put into df
    concattext = ''
    elementlist = pdfdoc.elements
    for anelem in elementlist:
        fs = int(anelem.font_size)
        stext = ' '.join(anelem.text().split())
        coltype = headermap(fs, headerdf)
        if coltype == 'h1':
            addrow(df, pdffile, h1, h2, h3, concattext)
            concattext = ''
            h1 = stext
            h2 = ''
            h3 = ''
        elif coltype == 'h2':
            addrow(df, pdffile, h1, h2, h3, concattext)
            concattext = ''
            h2 = stext
            h3 = ''
        elif coltype == 'h3':
            addrow(df, pdffile, h1, h2, h3, concattext)
            concattext = ''
            h3 = stext
        elif coltype == 'text':
            concattext = concattext + ' ' + stext
    addrow(df, pdffile, h1, h2, h3, concattext)
    return(df)

def validpdffile(afile):
    try:
        if afile.lower() == 'stop':
            return True

        temppdfdoc = load_file(afile)
        return True
    except Exception as ex:
        tkfuncs.write_text(text_window, f'    error loading file {afile=} : {ex=}\n')
        return False
