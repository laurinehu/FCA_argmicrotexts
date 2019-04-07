""""
merge contexts
"""

# imports
from itertools import chain
import argparse
from argparse import RawTextHelpFormatter
import os
import pandas as pd

def get_dic(csv_context, prefix="", delim="\t"):
    """
    from a csv context, outputs the dataset as a dic
    objects : [list of attributes]
    """
    context_dtf = pd.read_csv(csv_context, sep=delim, index_col=0, header=0)
    dic_obj_attr = {}
    # loop over objects
    for obj_idx in context_dtf.index:
        obj_attr = context_dtf.loc[obj_idx]
        # loop over attributes and register those that have truth val at 1
        attributes = []
        for (attr, truth_val) in obj_attr.iteritems():
            if truth_val == 1:
                attributes.append(prefix+attr)

        dic_obj_attr[obj_idx] = attributes
    return dic_obj_attr

def merge_dicts(dicts):
    """
    merge a list of dicts
    """
    all_keys = []
    # recover all keys
    for dic in dicts:
        for k in dic.keys():
            if k not in all_keys:
                all_keys.append(k)

    # create dict for merging
    merged = dict.fromkeys(all_keys, [])
    for dic in dicts:
        # loop over key/ value and merge dictionnaries
        for k, v in dic.items():
            if k in merged: # key already in merged
                merged[k] = merged[k] + v
            else: # add key
                merged[k] = [v]
    return merged

def write_csv_context(formated_gspan, output_path, sep="\t"):
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

def merge_contexts(*contexts, merged_context_filename="merged_context.csv"):
    """
    from a given number of contexts with same attributes,
    merge them into a single context
    contexts must have the following name :
        arg_[output/context...].csv
        rst_[output/context...].csv
        sdrt_[output/context...].csv
    """
    dic_contexts = []

    # loop over given contexts to save them
    for context_filename in contexts:

        # define an attribute prefix, specifying where the attribute coms from (arg, rst, sdrt)
        if os.path.basename(context_filename)[:3] == "rst":
            attr_prefix = "r_"
        if os.path.basename(context_filename)[:3] == "arg":
            attr_prefix = "a_"
        if os.path.basename(context_filename)[:3] == "sdrt":
            attr_prefix = "s_"

        # create dictionnary representing context and save it to list
        dic_contexts.append(get_dic(context_filename, prefix=attr_prefix))
        merge_context = merge_dicts(dic_contexts)

        # write new merged context
        write_csv_context(merge_context, merged_context_filename)

def main():
    """
    generates a context from the output of gspan
    """
    # parser command line arguments
    description = "from 2 context file, merge them and save to output"
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=RawTextHelpFormatter)
    # TODO: parse undefined nb of contexts: list of files
    # here we just merge 2 
    parser.add_argument('path2context1',
                        metavar='path2context1',
                        type=str,
                        help="""path to file containing context1 in .csv""")
    parser.add_argument('path2context2',
                        metavar='path2context2',
                        type=str,
                        help="""path to file containing context2 in .csv""")
