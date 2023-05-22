#!/usr/local/bin/python3
#  /usr/local/bin/python3 -m pip install tkinter
import sys, time, random
import tkinter as tk
import tkinter.font as tkFont
from tkinter import *
from tkinter import scrolledtext

####  global variables ######
window = tk.Tk()
text_window = None
inputmark = "1.0"

# pre-define some fonts
cour14normal = tkFont.Font(family="Courier",size=14,weight="normal")
cour14bold = tkFont.Font(family="Courier",size=14,weight="bold")
cour14italic = tkFont.Font(family="Courier",size=14,weight="normal",slant="italic")
cour16input = tkFont.Font(family="Courier", size=16, weight="bold")
################################


def createTextWindow(windowname, height=20, width=80, posx=10, posy=10, bg='light cyan', font=cour14normal):
    """
    Create a text window, with dimension of widthxheight+posx+posy .
    :param windowname:  the name of the window
    :param height:  the number of rows for this text window
    :param width:   the number of chars as width
    :param posx:    the top-left corner of the window is at posx,posy (in pixels)
    :param posy:
    :param bg:      background color
    :param font:    text font
    :return:  created text window object, already set in global variable
    """
    global text_window
    global window

    window.resizable(False, False)
    window.title(windowname)
    window.geometry("+%d+%d" %(posx,posy))

    text_window = scrolledtext.ScrolledText(window, height=height, width=width, bg="light cyan", font=cour14normal, insertbackground="red", relief="raised", wrap="word")
    text_window.pack()

    text_window.tag_configure('normalfont', font=cour14normal)
    text_window.tag_configure('boldfont', font=cour14bold)
    text_window.tag_configure('boldhighlight', background='yellow', font=cour14bold)
    text_window.tag_configure('italicfont', font=cour14italic)
    text_window.tag_configure('inputfont', font=cour16input)
    return(text_window)

def write_text(text_window, outtext, newline=True, fontstr='normalfont'):
    """
    Write some text to a scrolled text window, assuming cursor is at the end of the line of current line.

    :param text_window:  scrolledtext object
    :param outtext:   the text to be written
    :param newline:   True, write the text in a new line; False, overwrite current line
    :param fontstr:   'normalfont', 'boldfont', 'boldhighlight', 'italicfont' etc.

    """
    if newline == False:
        (l,c) = text_window.index(tk.INSERT).split(".")
        p = str(l) + '.0'
        text_window.delete(p, tk.END)

    text_window.insert(END, '\n')
    b = text_window.index(tk.INSERT)
    text_window.insert(END, outtext)   ## append to the end
    e = text_window.index(tk.INSERT)
    text_window.tag_add(fontstr, b, e)
    text_window.see(END)    # make the rows auto-scroll to the end
    text_window.update()

def processinput(event, inputprocessor, exitprocessor):
    """
    Get input string and process it according to procname.
    If &lt;Return&gt; is pressed but input is less than 3 char, the function do nothing, continue wait for further inputs. short multi-lines are concatenated into single line for processing.
    This function is bound to &lt;Return&gt; , used by promptforinput().
    :param event:  KeyPress event keysym=Return, not used in this function
    :param procname:  a string indicate how to process this input string
    :param exitproc: a method to exit the process, customize to add finishing tasks.
    """
    global inputmark
    #print(f'global {inputmark=}')
    text_window.update()

    s = text_window.get(inputmark, tk.INSERT).strip()
    if len(s) > 3:
        if s == 'stop':
            # we are done here
            exitprocessor()

        text_window.unbind('<Return>')
        inputprocessor( s.replace('\n', ' ').replace("'", "\\'") )

def promptforinput(text_window, prompttxt, inputprocessor, exitprocessor=sys.exit):
    """
    Create a input prompt in a text window, with provided prompt text, and set input starting point
    with a global variable inputmark.
    :param text_window:  text window object
    :param prompttxt:    prompt text for input
    :param inputprocessor:  function object to process input string
    :param exitprocessor:   function object to  exit program
    """
    global inputmark

    write_text(text_window, prompttxt, True, 'inputfont')
    text_window.see(tk.END)
    text_window.update()
    text_window.focus()
    #  mark the input starting point
    inputmark = text_window.index(tk.INSERT)
    text_window.bind('<Return>', lambda event: processinput(event, inputprocessor, exitprocessor))

def delayexit(waitsec=5):
    c = 0
    while c< waitsec:
        c += 1
        write_text(text_window, f'   waited {c} seconds', False, 'italicfont')
        time.sleep(0.5)
    write_text(text_window, ' Gone !', True, 'boldfont')
    time.sleep(1)
    sys.exit()