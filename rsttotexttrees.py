'''
Script to convert a set of argmicrotext xml structure to a unique file
containing the txt representation
'''

# import the necessary packages
import argparse
from argparse import RawTextHelpFormatter
import subprocess
import os
import sys
import re

def get_relations(dep_string):
    """
    get list of relations from a string representing dependency structure
    """
    output = []
    regexp_rels = r'(\d*).*(\d)\t(\w*)'
    if re.findall(regexp_rels, dep_string) is not None:
        for (src, trg, typ) in re.findall(regexp_rels, dep_string):
            output.append([src, trg, typ])
    return output


def get_units(rels):
    """
    get list of units from a string representing dependency structure
    """
    units = [x[0] for x in rels]
    return units

def get_and_del_from_trg(trg, rels):
    """
    from a target, finds a relation and delete from list
    """
    rel = None
    for rel in rels:
        if int(rel[1]) == int(trg):
            outrel = rel
            break
    rels.remove(rel)
    return outrel

def get_cc(rels):
    """
    from list of rels, returns CC
    """
    for rel in rels:
        if rel[2] == "ROOT":
            cclaim = rel[0]
    return cclaim


def parcours(relations):
    """
    get the resut of parcours en profondeur
    """

    # remplir une liste des relations au fur et à mesure
    output = []

    # get root
    for (src, trg, typee) in relations:
        if typee == "ROOT":
            root = src

    # save noeuds visités
    last = []

    # add root to last visited
    last.append(root)

    # loop for parcours
    while relations != [] and last != []:
        #while last[-1] in [x[1] for x in relations]:
        if last[-1] in [x[1] for x in relations]:
            # get relation with last as target
            rel = get_and_del_from_trg(last[-1], relations)

            # add relation to output list
            output.append(rel)

            # set new last element (its the src of last added relation)
            last.append(rel[0])
        else:
            last.pop()
    return output


def test_rst_files(corpora):
    """
    if a file is empty or is not an rs3 file; ignore it
    and alert user that it's been ignored
    """
    good_corpora = []

    for file in corpora:
        if os.path.getsize(file) != 0 and file.endswith(".rs3"):
            good_corpora.append(file)
        else:
            if os.path.getsize(file) == 0:
                print("File " + file + " ignored because file is empty.")
            elif not file.endswith(".xml"):
                print("File " + file + " ignored because it's not an rs3 file")
    return good_corpora


def test_output_file(output_file):
    """
    if outputfile already exist, alert user and exit
    """
    if os.path.exists(output_file):
        sys.exit("""output file already exist, please enter a new filename or
                 delete the existing file""")
    else:
        return output_file

def test_rst2dep_exist(path):
    """
    if rst2dep script doesnt exist, alert user and exit
    """
    if not os.path.exists(path):
        sys.exit("""The needed rst2dep conversion tree was not find in the
        given place. Please set the right path, or download the script if it is
        not done yet. To download, go to : https://github.com/amir-zeldes/rst2dep
        """)

def write_txt(corpora, output_path, rst2dep_path):
    """
    produce txt representation of rs3 files from corpora
    the format is the following :
    t # id
    v id label
    ....
    e idsrc idtrg label
    """
    with open(output_path, "w") as output_file:
        for rs3_file in corpora:
            # get txtid from filename
            output_name = rs3_file.replace(".rs3", ".txt")
            txt_id = os.path.basename(output_name)
            txt_id = txt_id.replace("micro_", "")
            txt_id = txt_id.replace(".txt", "")

            try:
                output = subprocess.check_output(['/usr/bin/python2.7', rst2dep_path, rs3_file],
                                                 stderr=subprocess.STDOUT)
                output = output.decode("utf-8")
                rels = get_relations(output)
                cclaim = get_cc(rels)
                ordered_rels = parcours(rels)
                print(ordered_rels)
                units = get_units(get_relations(output))

            except subprocess.CalledProcessError as exception:
                output = exception.output

            # write in output file
            output_file.write("t # "+str(txt_id)+"\n")
            for unit in units:
                print(unit)
                if unit == cclaim:
                    output_file.write("v "+unit+" CC"+"\n")
                else:
                    output_file.write("v "+unit+" _"+"\n")
            for rel in ordered_rels:
                output_file.write("e "+rel[0]+" "+rel[1]+" "+rel[2]+"\n")

def main():
    """
    main function, recovers arguments and launches the conversion
    """

    description = """ This script converts a set of .rs3 trees to a unique .txt
    file containing the binary trees in the following format : \n
    t # idgraph \n
    v id label \n
    ... \n
    e idsrc idtrg label \n
    ... \n
    """
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('corpora_path',
                        metavar='corpora',
                        type=str,
                        nargs='*',
                        help='path to the corpora')
    #parser.add_argument('corpora_path', metaver='corpora', type=file, action='store', nargs='+')
    parser.add_argument('output_filename',
                        metavar='output',
                        type=str,
                        nargs=1,
                        help='path to the output filename')
    parser.add_argument('rst2dep',
                        metavar='rst2dep',
                        type=str,
                        nargs=1,
                        help="""path to the rst2dep.py converter - to download it,
                        see https://github.com/amir-zeldes/rst2dep""")

    args = parser.parse_args()

    # prepare and test all arguments
    # test existance of conversion script
    test_rst2dep_exist(args.rst2dep[0])
    # test existance of rst_files
    rst_files = test_rst_files(args.corpora_path)
    if len(args.output_filename) == 1:
        output_path = test_output_file(args.output_filename[0])
    else:
        sys.exit("just one outputfile required")

    # if all the tested files are ok, launch conversion
    write_txt(rst_files, output_path, args.rst2dep[0])


if __name__ == '__main__':
    main()
