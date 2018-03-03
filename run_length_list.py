# run_length_list.py
# The Raskin Center for Humane Interfaces (RCHI) 2004-2005

# Length Run Encoding List
# The list contains tuples of the form (value, length-of-run).

# Important bug caution. Previously a list was being assigned via a call like:
# self._styleNumbers = [styleID] * len(blah). However if self._styleNumbers was not a built in list
# (such as a class like LRE_List) then such an assignment would set the variable
# to be a list instead of just updating the contents of the vector.
# If one uses splice notation, then one does not endanger the class.

# One should be able to fix this problem in general with implementing the __eq__ method. This, in theory,
# should be equivalent to an equality statement: a.__eq__(y) <==> a = y. 
# However, __eq__ does not appear to be called when something like a = [1,2,3] is interpreted.

class RLE_List:
    def __init__(self):
    self._rle = []
    self._len = 0


    def __repr__(self):
    #return str(self._toList(0,self._len))
    return str(self._rle)

    def __len__(self):
    self._calcLen()
    return self._len

    def _calcLen(self):
    sum = 0
    for tuple in self._rle:
        sum += tuple[1]
    self._len = sum

    def _findTuplePos(self, i, returnOffset = 0):
    count = 0
    pos = 0

    while pos < len(self._rle):
        if i < count + self._rle[pos][1]:
        if returnOffset:
            return pos, i-count
        else:
            return pos
        
        count += self._rle[pos][1]
        pos += 1

    if returnOffset:
        return pos, 0
    else:
        return pos


    def _removeIfZero(self,i):
    try:
        if self._rle[i][1] == 0:
        self._rle.pop(i)
        return 1 
    except IndexError:
        pass
    return 0

    def _combine(self, i, j):
    if i < 0: i = 0
    if j < 0: j = 0
    if i == j: return 0
    
    try:
        if self._rle[i][0] == self._rle[j][0]:
        self._rle[i][1] += self._rle[j][1]
        self._rle.pop(j)
        return 1

    except IndexError:
        pass
    return 0

    def _simplify(self, i):
    for k in range(-1,2):
        if self._removeIfZero(i+k): i -= 1

    if self._combine(i, i-1): i -= 1
    if self._combine(i, i+1): i -= 1

    def _toList(self, start, end):
    start, end = self._checkSliceBounds(start, end)
    
    theList = []

    startPos, startOffset = self._findTuplePos(start,1)
    if end == len(self):
        endPos = len(self._rle)-1
        endOffset = self._rle[endPos][1]
    else:
        endPos, endOffset = self._findTuplePos(end,1)

    if startPos == endPos:
        return [self._rle[startPos][0]] * (end-start)
    for i in range(startPos, endPos+1):
        if i == startPos:
        theList.extend( [self._rle[i][0]] * (self._rle[i][1]-startOffset) )
        elif i == endPos:
        theList.extend( [self._rle[i][0]] * endOffset )
        else:
        theList.extend( [self._rle[i][0]] * self._rle[i][1] )
        
    return theList

    def _checkSliceBounds(self, i, j):
    length = len(self)
    
    if i < 0: i = length + i
    if j < 0: j = length + j

    if i > length: i = length
    if j > length: j = length

    return i,j

    

    def _compressList(self,theList):
    compressed_list = []
    last_i = theList[0]
    same_i_count = 1
    for i in theList[1:]:
        if i == last_i:
        same_i_count += 1
        else:
        compressed_list.append([last_i, same_i_count])
        same_i_count = 1
        last_i = i
    compressed_list.append([last_i, same_i_count])
    return compressed_list


    def __getitem__(self, i):
    pos = self._findTuplePos(i)
    return self._rle[pos][0]
        
    def __getslice__(self, i, j):
    i, j = self._checkSliceBounds(i,j)
    return self._toList(i,j)

    def __delslice__(self, i,j, doSimplify = 1):
    i,j = self._checkSliceBounds(i,j)

    pos, offset = self._findTuplePos(i, 1)
    startPos = pos
    for k in range(j-i):
        self._rle[pos][1] -= 1
        if pos == startPos:
        if self._rle[pos][1] == (i-offset):
            if self._rle[pos][1] == 0:
            self._rle.pop(pos)
            else:
            pos += 1
        else:
        if self._rle[pos][1] == 0:
            self._rle.pop(pos)
    
    if doSimplify: self._simplify(pos)

    def __delitem__(self, i):
    del self[i:i+1]


    def _break(self, i):
        pos, offset = self._findTuplePos(i, 1)
        if offset == 0 or offset == self._rle[pos][1]: return
        self._rle[pos][1] -= offset
        value = self._rle[pos][0]
        self._rle.insert(pos, [value, offset]) 

    def __setslice__(self, i, j, value):
        i,j = self._checkSliceBounds(i,j)
        #first break at the appropriate points
        self._break(i)
        self._break(j)
        #then find appropriate tuples
        start, end = self._findTuplePos(i), self._findTuplePos(j)
        #then del appropriate tuples
        del self._rle[start:end]
        if len(value) > 0:
            newList = self._compressList(value)
            self._rle[start:start] = newList
            self._simplify(start)
            self._simplify(start+len(newList)-1)
    

    

    def __setitem__(self, i, item):
    self.insert(i, item)
    del self[i+1:i+2]
    self._simplify(self._findTuplePos(i))

    def __eq__(self, item):
    print "This does not seem to work...?"
    self[:] = item

    def append(self, item):
    #If we are not looking at an empty array then we see if the new item is the same as the last value in the list. If it is increment the run by one. If it is not, put the new value on the end of the list with a run length of 1.
    if len(self._rle) > 0:
        value, run = self._rle[-1]
        if value == item:
        self._rle[-1][1] += 1
        self._len += 1
        return
        
    self._rle.append([item, 1])
    self._len += 1
    

    def insert(self, i, item):
    try:
        pos, offset = self._findTuplePos(i, 1)
    except IndexError:
        self.append(item)
        return

    if len(self) == 0:
        self.append(item)
        self._simplify(0)
        return
   
    startRun = offset
    endRun = self._rle[pos][1] - startRun

    if self._rle[pos][0] == item:
        self._rle[pos][1] += 1
    elif startRun == 0:
        self._rle.insert(pos, [item,1])
    elif endRun == 0:
        self._rle.insert(pos+1, [item,1])
    else:
        oldValue = self._rle[pos][0]
        
        self._rle[pos][1] = startRun
        self._rle.insert(pos+1, [item,1])
        self._rle.insert(pos+2, [oldValue, endRun])