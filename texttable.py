import sys
import random

class Cell(object):
    '''
    An object representing a table cell
    A table is represented as a list of lists containing Cell instances.
    '''
    def __init__(self, colspan, rowspan, contents=None):
        if contents is None:
            # for testing only
            # this will be removed
            contents = ''.join([
                chr(random.randint(97,122))
                for x in range(random.randint(0,15))])
        self.colspan = colspan
        self.rowspan = rowspan
        self.contents = contents

class xlist(list):
    '''
    An N dimentional list (or array) that expands as you request indices,
    thus never returning an index out of bounds error.

    Same as list.__init__ + accepts `dim` kwarg.
    `dim` is the number of dimensions represented by the xlist.
    defaults to `xlist.default_dim`
    '''
    default_dim = 2 # defaults to 2D xlist
    default_leaf = None
    def __init__(self, *args, **kwargs):
        self.dim = kwargs.pop('dim', self.default_dim)
        list.__init__(self, *args, **kwargs)
    @property
    def default(self):
        return self.default_leaf if self.dim <= 1 else xlist(dim=self.dim-1)
    def _expand(self, i):
        if i>= len(self):
            for j in range(i - len(self) + 1):
                self.append(self.default)
    def __getitem__(self,i):
        self._expand(i)
        return list.__getitem__(self, i)
    def __setitem__(self, i, x):
        self._expand(i)
        return list.__setitem__(self, i, x)


def find_next_col(l, i, b=0):
    if b >= len(l[i]):
        return b
    for x in range(b, len(l[i])):
        if l[i][x] is None:
            return x
    return x+1

def find_next_box(l, i, cs, rs):
    ''' i = row, cs, rs are spans '''
    b = 0
    while True:
        j = max([find_next_col(l, x, b) for x in range(i, i+rs)])
        for x in range(i, i+rs):
            for y in range(j, j+cs):
                if l[x][y] is not None:
                    b = x
                    break
        else:
            break
    return j

def find_cell(l, cid):
    for i in range(len(l)):
        for j in range(len(l[i])):
            if l[i][j] == cid:
                return i,j
    return -1,-1

def pad(s,k):
    return s+' '*(k-len(s))

table = [None]*4
table[0] = [Cell(2,2), Cell(1,1)]
table[1] = [Cell(1,2)]
table[2] = [Cell(1,1), Cell(1,1)]
table[3] = [Cell(2,1), Cell(1,1)]

l = xlist()

cid = 0
cmap = {}
for i,r in enumerate(table):
    for c in r:
        dy = find_next_box(l, i, c.colspan, c.rowspan)
        for x in range(i, i+c.rowspan):
            for y in range(dy, dy+c.colspan):
                l[x][y] = cid
        cmap[cid] = c
        cid += 1

print l

# Calculating col sizes

cols = [0]* len(l[0])
for j in range(len(cols)):
    for i in range(len(l)):
        a = -1 if j == 0 else l[i][j-1]
        b = l[i][j]
        c = -1 if j == len(cols) -1 else l[i][j+1]
        if a!=b and b!=c:
            cell = cmap[b]
            if len(cell.contents) > cols[j]:
                cols[j] = len(cell.contents)

for cid, cell in cmap.items():
    i,j = find_cell(l, cid)
    cs = range(j,j+cell.colspan)
    s = len(cell.contents) - sum([cols[x] for x in cs])
    x = 0
    while s > 0:
        cols[cs[x%len(cols)]] += 1
        s -= 1

print cols

## Actually printing the table

sys.stdout.write('+%s+\n' %('-'*(sum(cols)+len(cols)-1)))
for i in range(len(l)):
    sys.stdout.write('|')
    j = 0
    while j < len(l[i]):
        if l[i][j] not in cmap:
            sys.stdout.write(pad(' ', cols[j])+'|')
            j += 1
            continue
        cell = cmap.pop(l[i][j])
        cs = range(j,j+cell.colspan)
        s = sum([cols[x] for x in cs]) + (len(cs) -1) # added for the |'s
        sys.stdout.write(pad(cell.contents, s)+'|')
#         sys.stdout.write(pad(str(l[i][j]), s)+'|') # Debug
        j += cell.colspan
    sys.stdout.write('\n')
sys.stdout.write('+%s+\n' %('-'*(sum(cols)+len(cols)-1)))
