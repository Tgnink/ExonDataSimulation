import functools
import random
import re
from types import MethodType


def equal_text(line, text, match='=='):
    if match == '==':
        return line.strip() == text or line == text
    elif match == 're':
        return re.match(text, line)


def get_pos_text(filed, text, aim=0, match='re', **pos):
    '''return pos'''
    if 'pos' in pos:
        filed.seek(pos['pos'], 0)
    line = filed.readline()
    while(line):
        if equal_text(line, text, match):
            if aim == 0:
                return filed.tell()-len(line)
            elif aim == 1:
                return filed.tell()
        line = filed.readline()
    return -1


def get_line_text(filed, text, aim=0, match='re', **kw):
    '''
    return match line.
    aim=0,current line;aim=1,next line.
    match=re, regular expression;match='=',entirely match
    '''
    num = 1
    if 'pos' in kw:
        filed.seek(kw['pos'], 0)
    if 'num' in kw:
        num = kw['num']
    while(num):
        line = filed.readline()
        if equal_text(line, text, match):
            num -= 1
        if not line:
            return None
    if aim == 0:
        return line
    elif aim == 1:
        return filed.readline()


def get_column_row(file, text, aim=0, match='re', tail=False, **pos):
    '''
    caculate column of aimed row ,text is search content,
    aim=0 get current row ,aim=1 get next row
    match='==' is complete match, match='re' only match head ingore tail
    '''
    with open(file, 'r') as f:
        line = get_line_text(f, text, aim, match, **pos)
        if line:
            if tail:
                return len(line)
            else:
                return len(line.strip())
        else:
            return 0

def tidy_small_word(text, column,  cur=0):
    words=[]
    x = column-cur
    words.append(text[0:x])
    l = len(text)
    for x in range(column-cur, l, column):
        words.append('\n'+text[x:x+column])
    # writed.write('\n'+text[x:x+column])
    if l-x:
        cur = l-x
    else:
        cur = column
    return words
def write_small_word(writed, text, column,  cur=0):
    ''' write text to a opend file with coulum words every row'''
    x = column-cur
    writed.write(text[0:x])
    l = len(text)
    for x in range(column-cur, l, column):
        writed.write('\n'+text[x:x+column])
    # writed.write('\n'+text[x:x+column])
    if l-x:
        cur = l-x
    else:
        cur = column
    return cur


def write_big_words(writed, texts, colum, cur=0):
    for x in texts:
        cur = write_small_word(writed, x, colum, cur)
    return cur


def get_words_text(text, column):
    words = []
    for x in range(0, len(text), column):
        words.append(text[x:x+column]+'\n')
    return words


def get_words(filed, begin, length, memory, column, step, pos=-1):
    if pos > -1:
        pos += len2pos(begin, column, step)
        filed.seek(pos, 0)
    else:
        filed.read(begin-1)
    seqs = []
    s, l = [], memory
    line = filed.readline()
    while(line):
        line = line.strip()
        t = len(line)
        length -= t
        if length < 0:
            s.append(line[:length])
            break
        else:
            s.append(line)
        l -= t
        if l < 0:
            s = ''.join(s)
            seqs.append(s)
            s = [line[l:]]
            l = memory-len(s[0])
        line = filed.readline().strip()
    if s:
        s = ''.join(s)
        seqs.append(s)
        s = []
    return seqs


'''
def write_word(filed, writed, length, f_column, w_column, f_cur, w_cur, **kw):
    divisor = 1000
    integer = length//divisor
    remainder = length % divisor
    if 'pos' in kw:
        filed.seek(kw['pos'], 0)
    for x in range(integer):
        text, f_cur = get_small_word(filed, divisor, f_column, f_cur)
        w_cur = write_small_word(writed, text, w_column,  w_cur)
    text, f_cur = get_small_word(filed, remainder, f_column, f_cur)
    w_cur = write_small_word(writed, text, w_column, w_cur)
    return f_cur, w_cur
'''


def str2chromosome(chrr):
    if chrr in ('X', 'x'):
        return 23
    elif chrr in ('Y', 'y'):
        return 24
    elif chrr in ('12920', 'M', 'm'):
        return 25
    return int(chrr)


def str2int(llist):
    nlist = []
    for x in range(len(llist)):
        try:
            nlist.append(int(llist[x]))
        except:
            nlist.append(llist[x])
    return nlist


def len2pos(length, column, row_step, cur=0):
    length = length-1
    if not cur:
        raw = length//column
        cur = length % column
        return raw*(column+row_step)+length % column
    else:
        return len2pos(length+cur, column, row_step)-cur


def value2unnegtive(value):
    if value < 0:
        return 0
    else:
        return value


def value2positive(value):
    if value < 1:
        return 1
    else:
        return value


def merge_ranges(elist, join_gap):
    '''llist like [(x1,y1),(x2,y2),(x3,y3)]'''
    nlist = []
    if len(elist) <= 1:
        return elist
    else:
        elist.sort(key=lambda x: x[0])
        size = len(elist)
        x = 0
        y = 1
        end = elist[x][1]
        while(y <= size-1):
            if end+1+join_gap >= elist[y][0]:
                end = max(end, elist[y][1])
                y += 1
            elif end+1+join_gap < elist[y][0]:
                nlist.append((elist[x][0], end))
                x, end, y = y, elist[y][1], y+1
        nlist.append((elist[x][0], end))
    return nlist


def differ_range(elist, slist):
    nlist = []
    elist.sort()
    slist.sort()
    n = 0
    for x in slist:
        while(x[1] >= slist[n][0]):
            y = slist[n]
            if y[1] < x[0] or y[0] > x[1]:  # l==r
                nlist.append(y)
            else:  # l!=r
                l = max(y[0], min(y[1], x[0]))
                r = min(y[1], max(y[0], x[1]))
                if l != y[0]:
                    nlist.append((y[0], l))
                if r != y[1]:
                    nlist.append((r, y[1]))
            n += 1
    return nlist


def differ_insert_ranges(elist, slist):
    l = len(slist)
    if not l:
        return elist
    elist.sort()
    slist.sort()
    n, t, nlist = 0, 0, []
    y = slist[n]
    for x in elist:
        while(x[0] >= y[1]):
            t += y[2]-y[1]+y[0]-1
            n += 1
            if n >= l:
                break
            y = slist[n]
        if n >= l:
            break
        if y[0] > x[1]:
            nlist.append((x[0]+t, x[1]+t))
            continue
        else:
            l = max(x[0], min(x[1], y[0]))
            r = min(x[1], max(x[0], y[1]))
            if l != x[0]:
                nlist.append((x[0]+t, l+t))
            t += y[2]-y[1]+y[0]-1
            if r != x[1]:
                nlist.append((r+t, x[1]+t))
    return nlist


def in_range(plist, clist):
    '''plist are already sorted'''
    y = 0
    nlist = []
    for x in clist:
        for y in plist:
            if x[0] <= y[1] and x[1] >= y[0]:
                nlist.append((y[0], y[1]))
                mark = False
                break
        if mark:
            nlist.append(-1)
        mark = True
    return nlist


def count_range(alist, blist):
    ndict = {}
    for x, y in zip(alist, blist):
        if x in ndict:
            ndict[x].append(y)
        else:
            ndict[x] = [y]
    return ndict


def split_range(llist, slist):
    curr, b = llist
    nlist = []
    for x, y in slist:
        if y != '.' and x > curr:
            nlist.append((curr, x-1))
            curr = y+1
        elif y == '.' and x >= curr:
            nlist.append((curr, x))
            curr = x+1
    if y != b:
        nlist.append((curr, b))
    return nlist


def deeplen(llist):
    n = 0
    if isinstance(llist, (list, tuple)):
        for x in llist:
            n += deeplen(x)
    elif llist:
        n += 1
    return n


def content_range(llist, pos1, pos2):
    pos = -1
    attach = False
    for i, x in enumerate(llist):
        pos = pos+len(x)
        if attach:
            if pos >= pos2:
                right = x[:len(x)+pos2-pos]
                r = i
        elif pos > pos1:
            attach = True
            if pos < pos2:
                left = x[pos1-pos-1:]
                l = i
            else:
                return [x[pos1-pos:len(x)+pos2-pos]]
    return left+llist[l:r+1]+right


def not_indexs(string, char):
    l, s, x, y, i, t = [], [], 0, 0, 0, False
    for i, n in enumerate(string):
        if n != char and not t:
            x = i
            t = True
        elif n == char and t:
            y = i
            l.append((x, y-1))
            t = False
    if t:
        l.append((x, i))
    if l:
        for n in l:
            s.append(string[n[0]:n[1]+1])
    return l, s


def split_formula(string, char=','):
    count = 0
    substrings = []
    s = ''
    for x in string:
        s += x
        if x == '(':
            count += 1
        elif x == ')':
            count -= 1
        elif x == char and count == 0:
            substrings.append(s[:-1].strip())
            s = ''
    if s.strip():
        substrings.append(s.strip())
    return substrings


def haskey(plist, clist):
    for x in clist:
        if x not in plist:
            return False
    return True


def random_weight_choice(dictt, summ):
    t = random.randint(1, summ)
    for char, val in dictt.items():
        t -= val
        if t <= 0:
            return char


def file_end(filed):
    filed.seek(0, 2)
    pos_end = filed.tell()
    filed.seek(0, 0)
    return pos_end
#!!!!


def log_file(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        print('input file: %s \t' % args[0])
        print('output file: %s' % args[1])
        return func(*args, **kw)
    return wrapper
