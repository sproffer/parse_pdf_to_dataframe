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
from py_pdf_parser.visualise import visualise
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

def build_headerdata(pdfdoc, headermaxlen=200, ignorelen=5, ignorecombinedlen=20):
    """
    Parse document to establish header mapping (based on font size)
        [font_size, max_length, count, combined_len, typecol]
    :param pdfdoc:   the PDF document
    :param headermaxlen:  max length that can be considered as header
    :param ignorelen:     any section less than this is discoarded, to ignore such things as page numbers
    :param ignorecombinedlen:  any section with combined length less than this, is discarded
    :return:   dataframe font_size and typecol (with 'h1', 'h2', 'h3', 'text')
    """
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
    if len(h1) > 5:
        hh = f'{h1} - {h2} - {h3}'
        df.loc[len(df.index)] = [afile, hh, ctext, f'{hh} : {ctext}' ]


def parsepdf(df, pdffile, viewpdf=False):
    """
    parse a PDF file and add contents to the dataframe
    :param df:     existing dataframe, could already have data
    :param pdffile:   pdffile name
    :param viewpdf:   whether to launch a PDF visualize, default is False.
    :return:    updated dataframe with this PDF file:  DataFrame(None, columns=['pdf_file', 'header', 'content', 'combined'])
    """
    pdfdoc = load_file(pdffile)
    if viewpdf == True:
        ## has problem of exiting and continue
        visualise(pdfdoc)

    headerdf = build_headerdata(pdfdoc)
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

