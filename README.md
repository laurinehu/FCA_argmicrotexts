# argmicrotext_conversions
Repository to save the work done on argmicrotexts corpora


## Argumentation structure to text representation

The script for doing this is the one named **argtotexttrees.txt**  

usage :   

    > argtotexttrees.py corpora output  

where :
- **corpora** is the glob pattern / or list of xml files you want to add to the output
- **output** is the file where to save output (file must not exist)


This script converts a set of .xml graphs to a unique .txt
file containing the binary trees in the following format

The output format is the following :
t # txtid
v id label
...
e idsrc idtrg label
...

each txt graph is defined by a txtid
V = {v1, ... vn} the set of vertices
a vertice v is defined from a unique id and a label
E = {e1, ... en} the set of edges
an edge is defined from the ids of its source (idsrc) and its target (idtrg)

## Argumentation structure to text representation
