from keyfunctions import *
import re

#class function given separate file because big
def doinput(self, curses):
    oldcy = self.cy
    self.oldkey = self.key
    self.key = self.scr.getch()
    try:self.ck = chr(self.key)
    except: self.ck = ''
    if self.mode == 'edit':
        if self.key == curses.KEY_UP : upfunc(self)
        elif self.key == curses.KEY_DOWN : downfunc(self)
        elif self.key == curses.KEY_LEFT : leftfunc(self)
        elif self.key == curses.KEY_RIGHT : rightfunc(self)
        elif self.key in [curses.KEY_BACKSPACE, 127] : backfunc(self)
        elif self.ck == '\n' : enterfunc(self)
        elif self.ck == '(' : parenfunc(self)
        elif self.ck == '[' : squarebracketfunc(self)
        elif self.ck == '{' : bracketfunc(self)
        elif self.ck == '"' : quotefunc(self)
        elif self.ck == "'" : apostrophefunc(self)
        elif self.ck in [')', ']', '}', "'", '"'] : rightparenfunc(self)
        elif self.ck == '\t' : tabfunc(self)
        elif self.key == curses.KEY_BTAB : shifttabfunc(self)
        elif self.key == 0 : ctrlspacefunc(self)
        elif self.key == 22 : ctrlvfunc(self)
        elif self.key in [21, 26] : ctrlufunc(self)
        elif self.key == 25 : ctrlyfunc(self)
        elif self.key == 169 : altzfunc(self)
        elif self.key == 11 : ctrlkfunc(self)
        elif self.key == 19 : ctrlsfunc(self)
        elif self.key == 16 : ctrlpfunc(self)
        elif self.key == 17 : ctrlqfunc(self)
        elif self.key == 24 : ctrlxfunc(self)
        elif self.key == 29 : ctrlrbfunc(self)
        elif self.key == 28 : ctrlbsfunc(self)
        elif self.key == 3 : ctrlcfunc(self)
        elif self.key == 12 : ctrllfunc(self)
        elif self.key == 6 : ctrlffunc(self)
        elif self.key == 1 : ctrlafunc(self)
        elif 1 <= self.key <= 26 : pass #skip unused ctrl bindings
        elif self.key == 410 : pass
        elif self.key == 27 : pass
        else : defaultfunc(self)
    elif self.mode == 'terminal':
        t = self.terminal
        if self.key == 16 : ctrlpfunc(self)
        elif self.key == curses.KEY_LEFT:
            t.cx -= 1
            if t.cx < 0 : t.cx = 0
        elif self.key == curses.KEY_RIGHT:
            t.cx += 1
            if t.cx > len(t.s) : t.cx = len(t.s)
        elif self.key == curses.KEY_UP:
            t.sy += 1
        elif self.key == curses.KEY_DOWN:
            t.sy -= 1
        elif self.ck == '\t':
            if t.hi < 0 : t.hi = len(t.history)
            else : t.hi -= 1
            t.s = ([''] + t.history)[t.hi]
            t.cx = len(t.s)
        elif self.ck == '\n' : t.run()
        elif self.key == 127:
            if t.cx > 0:
                t.s = t.s[:t.cx-1] + t.s[t.cx:]
                t.cx -= 1
        #elif self.key == 263 : ctrlhfunc(self)
        elif self.key == 6:
            ctrlffunc(self)
        elif self.key == 3:
            t.kill()
        elif self.key >= 1 and self.key <= 26 : pass
        elif self.key == 410 : pass
        else:
            t.s = t.s[:t.cx] + self.ck + t.s[t.cx:]
            t.cx += 1
        if not self.ck in ['\t'] and not self.key in [curses.KEY_UP, curses.KEY_DOWN,
                        curses.KEY_LEFT, curses.KEY_RIGHT]: t.hi = -1
    elif self.mode == 'fileselect':
        if self.key == curses.KEY_UP:
            self.fi -= 1
            if self.fi < 0 : self.fi = 0
        elif self.key == curses.KEY_DOWN:
            self.fi += 1
            if self.fi > len(self.filecol): self.fi = len(self.filecol)            
        elif self.ck == '\n':
            if self.fi < len(self.filecol):
                self.changefile(self.filecol[self.fi])
            else : self.mode = 'newfilename'
        elif self.key == curses.KEY_RIGHT:
            if self.filecol[-1] != self.filelist[-1]:
                ind = self.filelist.index(self.filecol[-1]) + 1
                if ind < len(self.filelist):
                    self.filecol = self.filelist[ind:ind+self.edith-3]
            if self.fi > len(self.filecol): self.fi = len(self.filecol)
        elif self.key == curses.KEY_LEFT:
            if self.filecol[0] != self.filelist[0]:
                ind = self.filelist.index(self.filecol[0])
                self.filecol = self.filelist[ind-self.edith+3:ind]
        elif self.key == 16 : ctrlpfunc(self)
        elif self.key == 6 : self.mode = 'edit'
    elif self.mode == 'newfilename':
        if self.key in [curses.KEY_BACKSPACE, 127]:
            if len(self.newfname) > 0: self.newfname = self.newfname[:-1]
        elif self.ck == '\n':
            if len(self.newfname) > 0: self.changefile(self.newfname)
            else:
                self.newfname = ''
                self.mode = 'edit'
        elif self.key == 6 : self.mode = 'edit'
        else:
            self.newfname += self.ck
    else : int('a') #if this is ever called something went wrong

    if not self.key in [21, 26, 25] : self.redoq = []

    self.adjustcoords()

    if not self.isautocomp : self.aci = 0
    oldacword = self.acword
    l = self.lines[self.cy]

    #handle word list for autocomplete
    if oldcy < len(self.lines):
        newlws = re.findall('[_a-zA-Z][_a-zA-Z0-9]*', self.lines[oldcy])
        oldlws = self.linewords
        #remove unused words
        for w in oldlws:
            if not w in newlws and w in self.freqmap.keys():
                self.freqmap[w] -= 1
                if self.freqmap[w] <= 0 and w in self.lastwords:
                    self.lastwords.remove(w)
        #add new words
        for w in newlws:
            if not w in oldlws:
                if w in self.freqmap : self.freqmap[w] += 1
                else : self.freqmap[w] = 1
                if w in self.lastwords : self.lastwords.remove(w)
                self.lastwords.insert(0, w)
    self.linewords = re.findall('[_a-zA-Z][_a-zA-Z0-9]*', self.lines[self.cy])

    #get word to autocomplete and fill autocomplete menu
    if self.isautocomp:
        x = self.cx - 1
        if x < 0 : x = 0
        if x >= len(l) : x = len(l) - 1
        while x >= 0 and isalnum(l[x]) : x -= 1
        x += 1
        x1 = x
        x = self.cx
        if x >= len(l) : x = len(l) - 1
        while x >= 0 and x < len(l) and isalnum(l[x]) : x += 1
        x2 = x
        self.acword = l[x1:x2]
        self.acwordx = x1
    if self.isautocomp:
        self.acwords = [s for s in self.lastwords if s.startswith(self.acword)]
        if len(self.acwords) == 0 : self.acwords = [self.acword]
        self.acwords = self.acwords[:self.edith]

    if self.mode == 'edit' and not self.key in [curses.KEY_UP, curses.KEY_DOWN,
                        curses.KEY_LEFT, curses.KEY_RIGHT]:
        self.undoq.append(ministate(self.lines, self.cx, self.cy))
        while len(self.undoq) > 30 : self.undoq.pop(0)

    #autosave after every couple keystrokes
    self.keystrokes += 1
    if self.keystrokes % 20 == 0:
        file = open(self.filename, 'w')
        file.write('\n'.join(self.lines).strip())
        file.close()
        self.message = 'Autosaved at {} keystrokes'.format(self.keystrokes)

#states used for undo/redo
class ministate:
    def __init__(self, lines, cx, cy):
        self.lines = lines[:]
        self.cx = cx
        self.cy = cy

def isalnum(s):
    return re.match('[_a-zA-Z][_a-zA-Z0-9]*', s)
