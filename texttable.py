'''
Copyright 2009 Hatem Nassrat.
This software is released under the terms of the GPLv3

Module to facilitate printing of a table in textual format.

Usage
-----

::

  from texttable import *

  # create a table object
  table = [
      [Cell(2,2, 'the lazy brown'), Cell(1,1, 'jumped')],
      [Cell(1,2, 'over')],
      [Cell(1,1, 'fox'), Cell(1,1, 'cow')],
      [Cell(2,1, 'quick dumb'), Cell(1,1, 'red')],
  ]

  # pretty print the table to stdout
  pprint_table(table)
  # pretty print the table to a string buffer
  import cStringIO
  pprint_table(table, cStringIO.StringIO())

The above example would output

::

  +----------------------+
  |the lazy brown |jumped|
  |               |over  |
  |fox        |cow|      |
  |quick dumb     |red   |
  +----------------------+

'''

import sys
import random

__all__ = ['Cell', 'pprint_table']

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


def pad(s,k):
    '''
    Pad string `s` with spaces such that len(`s`) == `k`.
    note: if len(`s`) >= `k`, s is returned as is
    '''
    return s+' '*(k-len(s))

def find_next_col(l, i, b=0):
    '''
    finds the next column index in the xlist `l` that returns None
    `i` is the row to be searched
    `b` is the col to begin search from
    '''
    if b >= len(l[i]):
        return b
    for x in range(b, len(l[i])):
        if l[i][x] is None:
            return x
    return x+1

def find_next_box(l, i, cs, rs):
    '''
    finds the index of the next box of size `rs` x `cs` in the xlist `l`
    `i` is the row to be searched
    '''
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
    '''
    finds the start co-ordinated of cell with cell id `cid`
    returns (-1,-1) when no match is found
    '''
    for i in range(len(l)):
        for j in range(len(l[i])):
            if l[i][j] == cid:
                return i,j
    return -1,-1

def determine_layout(table):
    '''
    lays out `table`in 2D xlist, returning (`cmap`, `l`)
    `cmap` is a mapping of cell_id to cell object from table
    `l` is a 2D xlist instance that contains cells, each cell containing a
    cell_id representing the cell the occupies this area.
    '''
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
    return cmap,l

def calculate_colsize(cmap, l):
    '''
    Based on `cmap` and `l` retrned from `determine_layout`
    figures out how wide each cell should be.

    returns a list of ints representing the width of each collumn
    '''
    # Getting Minimum Col Size (colspan = 1)
    cols = [0]* len(l[0])
    for j in range(len(cols)):
        for i in range(len(l)):
            cell = cmap[l[i][j]]
            if cell.colspan == 1:
                if len(cell.contents) > cols[j]:
                    cols[j] = len(cell.contents)
    # Considering entries with colspan
    for cid, cell in cmap.items():
        i,j = find_cell(l, cid)
        cs = range(j,j+cell.colspan)
        s = len(cell.contents) - sum([cols[x] for x in cs])
        x = 0
        while s > 0:
            cols[cs[x%len(cols)]] += 1
            s -= 1
    return cols


def print_table_cols(cmap, l, cols, stream=sys.stdout):
    '''
    pprints the table parsed using `determine_layout`, `l`
    with the cell mapping `cmap`. And the list of col sizes `cols`
    The table is printed to `stream`
    '''
    stream.write('+%s+\n' %('-'*(sum(cols)+len(cols)-1)))
    for i in range(len(l)):
        stream.write('|')
        j = 0
        while j < len(l[i]):
            if l[i][j] not in cmap:
                a = l[i][j]
                b = -1 if j >= len(l[i])-1 else l[i][j+1]
                stream.write(pad(' ', cols[j]))
                if a != b:
                    stream.write('|')
                else:
                    stream.write(' ')
                j += 1
                continue
            cell = cmap.pop(l[i][j])
            cs = range(j,j+cell.colspan)
            s = sum([cols[x] for x in cs]) + (len(cs) -1) # added for the |'s
            stream.write(pad(cell.contents, s)+'|')
#             stream.write(pad(str(l[i][j]), s)+'|') # Debug
            j += cell.colspan
        stream.write('\n')
    stream.write('+%s+\n' %('-'*(sum(cols)+len(cols)-1)))


def pprint_table(table, stream=sys.stdout):
    '''
    pprint a table in textual format.
    A table is represented as a list of lists containing Cell instances.
    `table` is pprinted to `stream`
    '''
    cmap,l = determine_layout(table)
#     print l # Debug
    cols = calculate_colsize(cmap, l)
#     print cols # Debug
    print_table_cols(cmap, l, cols, stream)


if __name__ == '__main__':
    # Test Code
    table = [None]*4
    table[0] = [Cell(2,2), Cell(1,1)]
    table[1] = [Cell(1,2)]
    table[2] = [Cell(1,1), Cell(1,1)]
    table[3] = [Cell(2,1), Cell(1,1)]
    pprint_table(table)
