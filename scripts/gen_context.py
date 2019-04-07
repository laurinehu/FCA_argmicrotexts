"""
TODO : write docstring
"""

import json
from contextlib import redirect_stdout
from itertools import chain
import io
import re
import argparse
from argparse import RawTextHelpFormatter
# gspan betterenvi : src https://github.com/betterenvi/gSpan
from gspan_mining.config import parser as gspan_parser
from gspan_mining.main import main as gspan_main


def str2list(str_lst):
    """
    from a string in the shape of a list, converts to a list
    """
    str_lst = str_lst.replace("[", "")
    str_lst = str_lst.replace("]", "")
    str_lst = str_lst.replace(" ", "")
    str_lst = [int(obj) for obj in str_lst.split(",")]
    return str_lst

def turn_dict(dict_attr_obj):
    """
    from a dict of attributes+ their corresponding objects, creates a
    dict of objects and their corresponding attributes
    """
    dict_obj_attr = {}
    # turn dictionnary
    for attr, objects in dict_attr_obj.items():
        for obj in objects:
            # case object already in dict
            if obj in dict_obj_attr.keys():
                dict_obj_attr[obj].append(attr)
            # add obj to dict key + add attr as first elem of the list
            else:
                dict_obj_attr[obj] = [attr]
    return dict_obj_attr


def format_gspan_output(output_gspan_txt):
    """
    from txt string as gspan output, creates a dictionnary of organized data
    format:
    {objects: [att1,att2,att3]
    attr2: ...}
    """
    regexp_attrib = r'(t #[^S]*)Support: (\d*)\nwhere: (\[[^\]]*])'
    dic_attr_objects = {}
    dic_ids_patterns = {}
    dic_attr_descr = {}

    #if re.findall(regexp_attrib, )
    idx = 0
    for (pattern, support, objects) in re.findall(regexp_attrib, output_gspan_txt):
        # print(" PAT >> %s \n" % pattern)
        # print(" SUPP >> %s \n" % support)
        # count vertices
        pat_size = 0
        for line in pattern.split("\n"):
            if len(line) != 0 and line[0] == "e": # if its an edge
                pat_size += 1

        # register descriptions of patterns
        dic_attr_descr[idx] = (int(support), pat_size)
        # print("sup : %s -  patt size : %s   \n -------------------" % (support, pat_size))

        # register correspondance between attribute ids and its corresponding pattern
        dic_ids_patterns[idx] = pattern
        objects = str2list(objects)
        dic_attr_objects[idx] = objects
        idx = idx + 1

    dic_objects_attributes = turn_dict(dic_attr_objects)
    return (dic_objects_attributes, dic_ids_patterns, dic_attr_descr)

def write_csv_context(formated_gspan, dic_attributes_descr, output_path, sep="\t"):
    """
    from a dictionnary containing objects and a list of their associated attributes,
    write the context as a csv file
    """
    # list of lines to write in output file
    lines = []
    # get a list of the attributes (for writing)
    all_attributes = list(formated_gspan.values())
    all_attributes = list({x for x in chain.from_iterable(all_attributes)})
    all_attributes.sort()
    with open(output_path, "w") as output_file:
        # first line, corresponds to attributes names
        line = sep + sep.join([str(x) for x in all_attributes]) + "\n"
        lines.append(line)
        # second line corresponds to attributes support
        line = sep + sep.join([str(dic_attributes_descr[x][0]) for x in all_attributes]) + "\n"
        lines.append(line)
        # third line corresponds to attributes pattern size
        line = sep + sep.join([str(dic_attributes_descr[x][1]) for x in all_attributes]) + "\n"
        lines.append(line)

        # iteratively builds the context from the objects
        for obj, attributes in formated_gspan.items():
            # first column corresponds to object id
            line = str(obj)
            # loop on the attributes to construct the line
            # 0 if no relation between object and attribute
            # 1 if a relation exist between objects and attributes
            for att in all_attributes:
                line = line + sep
                # case rel exist
                if att in attributes:
                    line = line + "1"
                else:
                    line = line + "0"
            line = line + "\n"
            lines.append(line)
        output_file.writelines(lines)

def write_ids_patterns(dict_attr_patterns, output_path):
    """
    save the output of json attributes/pattern dictionnary to outpout_path
    """
    with open(output_path, 'w') as file:
        file.write(json.dumps(dict_attr_patterns)) # use `json.loads` to do the reverse

def apply_gspan(graphs_path):
    """
    from a txt representation of  graphs, apply gspan betterenvi and outputs
    a list of attributes (patterns) represented by an identifier and sharing
    some objetcs
    """
    # open file if it exists
    try:

        # set optional arguments to gspan application
        support = 2
        show_objects = True
        args_str = '-s '+str(support)+' -w '+str(show_objects)+' '+graphs_path
        FLAGS, _ = gspan_parser.parse_known_args(args=args_str.split())

        # redirect prints of gspan to gs_ret variable
        gs_ret = io.StringIO()
        with redirect_stdout(gs_ret):
            gspan_main(FLAGS)

        gs_ret = gs_ret.getvalue()

        # loop over the output to recover objetcs, attributes, relations and
        # patterns associated to relations from gspan output
        (gs_formatted, dic_ids_patterns, dic_attr_descr) = format_gspan_output(gs_ret)
        return (gs_formatted, dic_ids_patterns, dic_attr_descr)

    except FileNotFoundError:
        print("""The file you entered doesn't exist or is not in the good format,
        please verify the path""")


def main():
    """
    generates a context from the output of gspan
    """
    # parser command line arguments
    description = "TODO : write it"
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('graphs_file',
                        metavar='graphs_files',
                        type=str,
                        help="""path to the file containing graphs in txt format,
                        here the type of the graph is not considered at all""")
    parser.add_argument('output',
                        metavar='output_path',
                        type=str,
                        help="""path to the file where u want to save the output context""")
    parser.add_argument('output_dic',
                        metavar="output_attribute_patterns",
                        type=str,
                        default="decode_patterns.json",
                        help="""specify the output file
                        for attribute / pattern dic saving""")
    # parser.add_argument('-r', metavar='--rst', type=str,
    #                     help='path to the file containing rst graphs in txt format')
    # parser.add_argument('-a', metavar='--arg', type=str,
    #                     help='path to the file containing argument graphs in txt format')
    args = parser.parse_args()

    # do the job
    # apply gspan and recover objects and attributes
    (gs_formatted_output, dic_ids_patterns, dic_attr_descr) = apply_gspan(args.graphs_file)
    # write context in csv file
    write_csv_context(gs_formatted_output, dic_attr_descr, args.output)
    write_ids_patterns(dic_ids_patterns, args.output_dic)



if __name__ == '__main__':
    main()
