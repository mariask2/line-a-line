import os
from glob import glob
from names_and_constants import *

PATH = "path"
LANG1 = "lang1"
LANG2 = "lang2"
CORPUSNAME = "corpusname"
CORPUSNAMEWITHLANGUAGE = "corpusnamewithlanguage"

def produce_zero_count_dict(alignments_str):
    print("**********")
    print("alignments_str", alignments_str)
    alignments_str = alignments_str.strip()
    align_lst = alignments_str.split(" ")
    lang1_to_lang2 = {}
    lang2_to_lang1 = {}

    for alignment in align_lst:
        sp = alignment.split("-")
        # make into zero count
        lang1_nr = int(sp[0]) - 1
        lang2_nr = int(sp[1]) - 1
        if lang1_nr in lang1_to_lang2:
            lang1_to_lang2[lang1_nr].append(lang2_nr)
        else:
            lang1_to_lang2[lang1_nr] = [lang2_nr]
            
        if lang2_nr in lang2_to_lang1:
            lang2_to_lang1[lang2_nr].append(lang1_nr)
        else:
            lang2_to_lang1[lang2_nr] = [lang1_nr]

    print("lang1_to_lang2, lang2_to_lang1", lang1_to_lang2, lang2_to_lang1)

    return lang1_to_lang2, lang2_to_lang1

def produce_alignment_format_from_zero_count_dict(zero_count):
    alignment_lst = []
    for key in sorted(zero_count.keys()):
        for alignment in zero_count[key]:
            alignment_lst.append(str(int(key) + 1) + "-" + str(int(alignment) + 1))
    return " ".join(alignment_lst)

# Only used for debugging
def sort_alignement_list(alignment_lst):
    spl = alignment_lst.split(" ")
    spl = sorted(spl)
    return " ".join(spl)

"""
def produce_alignment_tuple_list(alignments_str):
    alignments_str = alignments_str.strip()
    align_lst = alignments_str.split(" ")
    align_tuple_lst = []
    
    for alignment in align_lst:
        sp = alignment.split("-")
        align_tuple_lst.append((int(sp[0]), int(sp[1])))

    return align_tuple_lst
"""

def get_term_post_list(terms, alignmentzerodictlang):

    term_list = []
    for nr, term in enumerate(terms):
        term_post = {}
        term_post["term"] = term
        term_post["nr"] = nr
        if nr in alignmentzerodictlang:
            term_post["alignments"] = alignmentzerodictlang[nr]
        else:
            term_post["alignments"] = []
        term_list.append(term_post)
    return term_list



def select_next_data_point(lang1, lang2, name, corpus_name, datapoint_number, datapoint_order_for_current_ordering,\
                           select_diffult = True, do_active_selection = True, select_unannotated = True, select_for_new_annotation=True):


    OUTDIR = get_aligned_output_dir_version(corpus_name, lang1, lang2, name)

    meta_data_file = open(os.path.join(OUTDIR, META_DATA_FILE_NAME))
    aligned_file = open(os.path.join(OUTDIR, ALIGNED_FILENAME))
    aligned_file_lines = aligned_file.readlines()

    lang1_file = open(get_data_to_align_file_name(corpus_name, lang1, lang2, lang1))
    lang2_file = open(get_data_to_align_file_name(corpus_name, lang1, lang2, lang2))
    annotated_alignments_file = open(get_aligned_file(corpus_name, lang1, lang2))
    
    lang1_lines = lang1_file.readlines()
    lang2_lines = lang2_file.readlines()
    annotated_alignments = annotated_alignments_file.readlines()
    not_to_select_because_not_matching_the_criterium_of_either_being_annotated_or_unannotated = set()
    for nr, annotated_alignment in enumerate(annotated_alignments):
        # datapoint_number should be -1 if just the first according to the selection criterium is to be chosen.
        # if it is something else, datapoints with a lower number than "datapoint_number" will not be selected
        #if nr <= datapoint_number:
        #    not_to_select_because_not_matching_the_criterium_of_either_being_annotated_or_unannotated.add(nr)
        
        if annotated_alignment.strip() != "":
            if select_unannotated:
                not_to_select_because_not_matching_the_criterium_of_either_being_annotated_or_unannotated.add(nr)
        else:
            if not select_unannotated:
                not_to_select_because_not_matching_the_criterium_of_either_being_annotated_or_unannotated.add(nr)


    # The meta-data file contains information on how difficult the automatic alignment was
    processed_meta_data = []

    for line in meta_data_file:
        
        sp = tuple([int(el) for el in line.strip().split("\t")])
        len_remaining_contested, len_intersection, len_no_intersection_not_reversed, len_no_intersection_reversed, len_result, nr = sp
        if nr in not_to_select_because_not_matching_the_criterium_of_either_being_annotated_or_unannotated:
            continue
        remaining_contested_per_len = len_remaining_contested/float(len_result)
        raiming_after_intersection_per_len = ((len_no_intersection_not_reversed + len_no_intersection_reversed)/2.0 - len_intersection)/float(len_result)
        meta_info = (remaining_contested_per_len, raiming_after_intersection_per_len, nr)

        processed_meta_data.append(meta_info)

    print("Number of files to select from: ", len(processed_meta_data))
    if do_active_selection:
        meta_data_sorted = sorted(processed_meta_data, reverse=select_diffult)
    else:
        meta_data_sorted = processed_meta_data
    selected_results = []
    selected_numbers = []
    selected_order_for_selected_in_current_ordering = []
    # Code prepared for making it possible to select several point. But now, only one point is selected

    if select_for_new_annotation:
        index_to_select = 0
    else:
        index_to_select = datapoint_order_for_current_ordering + 1
    for selected in meta_data_sorted[index_to_select:index_to_select+1]:
        print("selected", selected)
        
        if select_unannotated:
            # Read from the pre-annotations file
            alignmentzerodictlang1, alignmentzerodictlang2 = produce_zero_count_dict(aligned_file_lines[selected[2]].strip())
        else:
            # Read from the manually aligned file
            alignmentzerodictlang1, alignmentzerodictlang2 = produce_zero_count_dict(annotated_alignments[selected[2]].strip())
        
        terms_lang1 = lang1_lines[selected[2]].strip().split(" ")
        terms_lang2 = lang2_lines[selected[2]].strip().split(" ")
        print("----------")
        print("terms_lang1", terms_lang1)
        
        lang1_post_list = get_term_post_list(terms_lang1, alignmentzerodictlang1)
        lang2_post_list = get_term_post_list(terms_lang2, alignmentzerodictlang2)
        
        selected_results.append([lang1_post_list, lang2_post_list])
        selected_numbers.append(selected[2])
        selected_order_for_selected_in_current_ordering.append(index_to_select)
    
    meta_data_file.close()
    aligned_file.close()
    lang1_file.close()
    lang2_file.close()
    annotated_alignments_file.close()

    return selected_results, selected_numbers, selected_order_for_selected_in_current_ordering

def save_annotations(corpus_name, lang1, lang2, linenr_to_change, alignment_dict_format):
    first, second = alignment_dict_format
    print("first", first)
    raw_alignement_format_dict = {}
    for el in first:
        raw_alignement_format_dict[el["nr"]] = el["alignments"]

    annotated_alignment_to_save = produce_alignment_format_from_zero_count_dict(raw_alignement_format_dict)
    print("annotated_alignment", alignment_dict_format)
    print()
    print("raw_alignement_format_dict", raw_alignement_format_dict)

    annotated_alignments_file = open(get_aligned_file(corpus_name, lang1, lang2))
    annotated_alignments = annotated_alignments_file.readlines()
    annotated_alignments_file.close()
    new_alignment_data = []
    for nr, annotated_alignment in enumerate(annotated_alignments):
        if nr == linenr_to_change:
            new_alignment_data.append(annotated_alignment_to_save + "\n")
        else:
            new_alignment_data.append(annotated_alignment)

    annotated_alignments_file_to_write = open(get_aligned_file(corpus_name, lang1, lang2), "w")
    for el in new_alignment_data:
        annotated_alignments_file_to_write.write(el)
    annotated_alignments_file_to_write.close()
    return "Annotations saved"

# TODO: Should also "data_to_align" be changed?
def delete_data_point(corpus_name, lang1, lang2, linenr_to_delete):
    deleted_file = open(get_deleted_file(corpus_name, lang1, lang2), "a")
    deleted_info = [str(linenr_to_delete)]
    
    lang1_file = open(get_training_data_file_name(corpus_name, lang1, lang2, lang1))
    lang2_file = open(get_training_data_file_name(corpus_name, lang1, lang2, lang2))

    lang1_lines = lang1_file.readlines()
    lang2_lines = lang2_file.readlines()


    lang1_file.close()
    lang2_file.close()

    lang1_file_to_write = open(get_training_data_file_name(corpus_name, lang1, lang2, lang1), "w")
    lang2_file_to_write = open(get_training_data_file_name(corpus_name, lang1, lang2, lang2), "w")

    # Write "X" instead of the original content
    # And save deleted data to another file
    for nr, line in enumerate(lang1_lines):
        if nr == linenr_to_delete:
            deleted_info.append(line.strip())
            lang1_file_to_write.write("X" + "\n")
        else:
            lang1_file_to_write.write(line)
    
    for nr, line in enumerate(lang2_lines):
        if nr == linenr_to_delete:
            deleted_info.append(line.strip())
            lang2_file_to_write.write("X" + "\n")
        else:
            lang2_file_to_write.write(line)
    lang1_file_to_write.close()
    lang2_file_to_write.close()

    deleted_file.write("\t".join(deleted_info) + "\n")

    # Add a dummy annotation for the deleted line, so that this line will not be selected for annotation any more
    save_annotations(corpus_name, lang1, lang2, linenr_to_delete, ([{"term": 0, "nr": 0, "alignments": [0]}], [{"term": 0, "nr": 0, "alignments": [0]}]))

    happened = "Deleted data point " + " ".join(deleted_info)
    print(happened)
    return happened


def list_available_corpora():
    dirs = [el for el in glob(OUTDIRBASE + "/*") if os.path.isdir(el) and len(el.split("_")) > 2]
    dir_infos = []
    for el in dirs:
        dir_info = {}
        dir_info[PATH] = el
        dir_info[LANG1] = el.split("_")[-2]
        dir_info[LANG2] = el.split("_")[-1]
        dir_info[CORPUSNAME] = "_".join(os.path.split(el)[-1].split("_")[:-2])
        dir_info[CORPUSNAMEWITHLANGUAGE] = os.path.split(el)[-1]
        dir_infos.append(dir_info)
    return dir_infos

def get_dir_info_from_corpus_name_with_language(corpus_name):
    all_dir_infos = list_available_corpora()
    for dir_info in all_dir_infos:
        if dir_info[CORPUSNAMEWITHLANGUAGE] == corpus_name:
            return dir_info
    return None # no match found

def select_data_point_from_corpus(corpus_name, datapoint_number, datapoint_order_for_current_ordering,\
                                  select_difficult, do_active_selection, select_unannotated, select_for_new_annotation):
    print("corpus_name", corpus_name, "corpus_name")
    dir_info = get_dir_info_from_corpus_name_with_language(corpus_name)
    print("dir_info", dir_info)
    if not dir_info:
        raise FileNotFoundError("No directory in the data matching the name " + str(corpus_name))
    selected_results, selected_numbers, order_for_selected_in_current_ordering =\
        select_next_data_point(dir_info[LANG1], dir_info[LANG2], "standard", dir_info[CORPUSNAME],\
                                                                datapoint_number, datapoint_order_for_current_ordering,\
                                                                select_difficult, do_active_selection, select_unannotated,\
                                                                select_for_new_annotation)
    print("********")
    print("selected_results", selected_results)
    print("********")
    # Now only one element is returned (or none), but code is written to allow for a list of data points
    if len(selected_results) > 0 and len(selected_numbers) > 0:
        return {"data_point" : selected_results[0], "data_point_number": selected_numbers[0],\
            "order_for_selected_in_current_ordering": order_for_selected_in_current_ordering[0], "dir_info": dir_info}
    else:
        return {"data_point" : None, "data_point_number": None,\
                "order_for_selected_in_current_ordering": None, "dir_info": dir_info}


def test_select():
    
    lang1 = "de"
    lang2 = "sv"
    name = "standard"
    corpus_name = "labour_marked_social_security"
    
    OUTDIR = get_aligned_output_dir_version(corpus_name, lang1, lang2, name)
    datapoint_number = 20
    datapoint_order_for_current_ordering = 3
    print("Most difficult")
    print("-------------------")
    selections = select_next_data_point(lang1, lang2, name, corpus_name, datapoint_number, datapoint_order_for_current_ordering, True)
    for nr, el in enumerate(selections):
        print(el)
        output_file = os.path.join(OUTDIR, "difficult_" + str(nr) + ".pdf")

    print("*******************************************")
    print("Least difficult")
    selections = select_next_data_point(lang1, lang2, name, corpus_name, datapoint_number, datapoint_order_for_current_ordering,\
                                        False, True, True)
    for nr, el in enumerate(selections):
        print(el)
        output_file = os.path.join(OUTDIR, "easy_" + str(nr) + ".pdf")

    print("*******************************************")
    print("Least difficult, select annotated")
    selections = select_next_data_point(lang1, lang2, name, corpus_name, datapoint_number, datapoint_order_for_current_ordering,\
                                        False, False, True)
    for nr, el in enumerate(selections):
        print(el)


if __name__ == "__main__":
    test_select()
    ac = list_available_corpora()
    for el in ac:
        if "labour" in el[CORPUSNAMEWITHLANGUAGE] and "marked" in el[CORPUSNAMEWITHLANGUAGE]:
            print(el[CORPUSNAMEWITHLANGUAGE])
            print(select_data_point_from_corpus(el[CORPUSNAMEWITHLANGUAGE], 50, 20, True, True, True, False))
            print()
            print(select_data_point_from_corpus(el[CORPUSNAMEWITHLANGUAGE], 50, 20, False, True, True, False))
            print()
            print(select_data_point_from_corpus(el[CORPUSNAMEWITHLANGUAGE], 50, 20, False, False, True, False))


            OUTDIR = get_aligned_output_dir_version(el[CORPUSNAME], "de", "sv", "standard")
            aligned_file = open(os.path.join(OUTDIR, ALIGNED_FILENAME))
            aligned_file_lines = aligned_file.readlines()

            dict = produce_zero_count_dict(aligned_file_lines[400].strip())
            print("not zero count:")
            print(dict)
            print("original alignment:")
            print(sort_alignement_list(aligned_file_lines[400]).strip())
            non_zero_alignments = produce_alignment_format_from_zero_count_dict(dict[0])
            print("transformed and transformed back:")
            print(sort_alignement_list(non_zero_alignments))
            
            max = sorted(list(dict[0].keys()) + list(dict[1].keys()))[-1]
            print("max", max)
            
            alignment_info = get_term_post_list(range(0, max+1), dict[0])
            print(alignment_info)

            print(save_annotations(el[CORPUSNAME], "de", "sv", 400, (alignment_info, alignment_info)))

            print(delete_data_point(el[CORPUSNAME], "de", "sv", 3))


