import sys
import random

class Cell(object):
    def __init__(self,c,r,t=None):
        if t is None:
            t = ''.join([
                chr(random.randint(97,122))
                for x in range(random.randint(0,15))])
        self.colspan = c
        self.rowspan = r
        self.contents = t

class xlist(list):
    def make_dynamic(self):
        self.default_attr = 'ddefault'
    def _get_default(self):
        return getattr(self, self.default_attr)
    ddefault = property(lambda self: xlist())
    sdefault = None
    default_attr = 'sdefault'
    default = property(_get_default)
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


matrix = [None]*4
matrix[0] = [Cell(2,2), Cell(1,1)]
matrix[1] = [Cell(1,2)]
matrix[2] = [Cell(1,1), Cell(1,1)]
matrix[3] = [Cell(2,1), Cell(1,1)]


l = xlist()
l.make_dynamic()

def find_next_col(i, b=0):
    if b >= len(l[i]):
        return b
    for x in range(b, len(l[i])):
        if l[i][x] is None:
            return x
    return x+1

def find_next_box(i, cs, rs):
    ''' i = row, cs, rs are spans '''
    b = 0
    while True:
        j = max([find_next_col(x, b) for x in range(i, i+rs)])
        for x in range(i, i+rs):
            for y in range(j, j+cs):
                if l[x][y] is not None:
                    b = x
                    break
        else:
            break
    return j

def find_cell(cid):
    for i in range(len(l)):
        for j in range(len(l[i])):
            if l[i][j] == cid:
                return i,j
    return -1,-1


cid = 0
cmap = {}
for i,r in enumerate(matrix):
    for c in r:
        dy = find_next_box(i, c.colspan, c.rowspan)
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
    i,j = find_cell(cid)
    cs = range(j,j+cell.colspan)
    s = len(cell.contents) - sum([cols[x] for x in cs])
    x = 0
    while s > 0:
        cols[cs[x%len(cols)]] += 1
        s -= 1

print cols

## Actually printing the table

def pad(s,k):
    return s+' '*(k-len(s))

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
