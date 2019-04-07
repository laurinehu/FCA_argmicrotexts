'''
Script to convert a set of argmicrotext xml structure to a unique file
containing the txt representation
'''

# import the necessary packages
import argparse
from argparse import RawTextHelpFormatter
import os
import sys
from xml.dom import minidom


def find_prem(edges, rel):
    """
    from a set of edges and a relation, returns the premisse of the relation
    """
    for edge in edges:
        if edge.attributes["id"].value == rel:
            out = edge.attributes["src"].value
    return out


def get_adus_edges_cc(graphxml_path):
    """
    from a xml_graph
    return adus and edges
    """
    edges_dic = {}
    rel_list = []
    with open(graphxml_path) as xmlfile:
        xmlgraph = minidom.parse(xmlfile)
        adus = xmlgraph.getElementsByTagName("adu")
        adus = [a.attributes["id"].value for a in adus]
        edges = xmlgraph.getElementsByTagName("edge")

        # recover edges in a dict
        # key : src adu
        # value : (trg adu, type)
        for edge in edges:
            (trg, ttype) = (edge.attributes["trg"].value, edge.attributes["type"].value)
            edges_dic[edge.attributes["src"].value] = (trg, ttype)


        # loop over adus to find relations
        for adu in adus:

            # cas ou la relation n'existe pas dans l'ordre lexicographic
            if adu in edges_dic.keys():
                # case target is a relation,
                # replace target by premisse of rel
                if edges_dic[adu][0][0] == 'c':
                    rel = (adu,)+(find_prem(edges, edges_dic[adu][0]),)+(edges_dic[adu][1],)
                    rel_list.append(rel)
                # normal case
                else:
                    rel_list.append((adu,)+edges_dic[adu])

        # recover cc
        srcs = [x for (x, y, z) in rel_list]
        trgts = [y for (x, y, z) in rel_list]
        for trg in trgts:
            if trg not in srcs:
                cclaim = trg

        return (adus, rel_list, cclaim)

def write_txt(corpora, output_path):
    """
    produce txt representation of graph from corpora
    the format is the following :
    t # id
    v id label
    ....
    e idsrc idtrg label
    """
    i_txt = 0
    corresp_ids = {}
    with open(output_path, "w") as output:
        for xmlgraph in corpora:
            id_name = os.path.basename(xmlgraph).replace("micro_", "").replace(".xml", "")
            (args, rels, cclaim) = get_adus_edges_cc(xmlgraph)
            output.write("t # "+str(id_name)+"\n")
            #output.write("t # "+str(i)+"\n")
            i_arg = 0
            for arg in args:
                corresp_ids[arg] = i_arg
                if arg == cclaim:
                    output.write("v "+str(i_arg)+" CC"+"\n")
                else:
                    output.write("v "+str(i_arg)+" _"+"\n")
                i_arg = i_arg+1

            for rel in rels:
                output.write("e "+str(corresp_ids[rel[0]])+" "+str(corresp_ids[rel[1]])+" "+rel[2]+"\n")

            # increment txt id
            i_txt = i_txt+1

def test_args_files(corpora):
    """
    if a file is empty or is not an xml file; ignore it and alert user that
    it's been ignored
    """
    good_corpora = []
    for file in corpora:
        if os.path.getsize(file) != 0 and file.endswith(".xml"):
            good_corpora.append(file)
        else:
            if os.path.getsize(file) == 0:
                print("File " + file + " ignored because file is empty.")
            elif not file.endswith(".xml"):
                print("File " + file + " ignored because it's not an xml file")
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

def main():
    """
    main function, recovers arguments and launches the conversion
    """

    description = """ This script converts a set of .xml graphs to a unique .txt
    file containing the binary trees in the following format : \n
    t # idgraph \n
    v id label \n
    ... \n
    e idsrc idtrg label \n
    ... \n
    """
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('corpora_path', metavar='corpora', type=str, nargs='*',
                        help='path to the corpora')
    parser.add_argument('output_filename', metavar='output', type=str, nargs=1,
                        help='path to the output filename')

    args = parser.parse_args()

    # prepare and test all arguments
    args_xml_files = test_args_files(args.corpora_path)
    if len(args.output_filename) == 1:
        output_path = test_output_file(args.output_filename[0])
    else:
        sys.exit("just one outputfile required")

    # if all the tested files are ok, launch conversion
    write_txt(args_xml_files, output_path)


if __name__ == '__main__':
    main()
