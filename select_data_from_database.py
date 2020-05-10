import os
from glob import glob
from names_and_constants import *

PATH = "path"
LANG1 = "lang1"
LANG2 = "lang2"
CORPUSNAME = "corpusname"
CORPUSNAMEWITHLANGUAGE = "corpusnamewithlanguage"

def produce_count_dict(alignment_list):

    lang1_to_lang2 = {}
    lang2_to_lang1 = {}

    for l1,l2 in alignment_list:
    
        # make into zero count
        lang1_nr = int(l1)
        lang2_nr = int(l2)
        if lang1_nr in lang1_to_lang2:
            lang1_to_lang2[lang1_nr].append(lang2_nr)
        else:
            lang1_to_lang2[lang1_nr] = [lang2_nr]
            
        if lang2_nr in lang2_to_lang1:
            lang2_to_lang1[lang2_nr].append(lang1_nr)
        else:
            lang2_to_lang1[lang2_nr] = [lang1_nr]
        
    return lang1_to_lang2, lang2_to_lang1

# Produce in fastalign format
def produce_database_alignment_format_from_count_dict(count_dict):
    alignment_lst = []
    for key in sorted(count_dict.keys()):
        for alignment in count_dict[key]:
            alignment_lst.append([int(key), int(alignment)])
    return alignment_lst

# Only used for debugging
def sort_alignement_list(alignment_lst):
    spl = alignment_lst.split(" ")
    spl = sorted(spl)
    return " ".join(spl)


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

def save_annotations(mc, corpus_name, current_data_point_nr, alignment_dict_format):
    first, second = alignment_dict_format
    print("first", first)
    raw_alignement_format_dict = {}
    for el in first:
        raw_alignement_format_dict[el["nr"]] = el["alignments"]

    print("raw_alignement_format_dict", raw_alignement_format_dict)
    annotated_alignment_to_save = produce_database_alignment_format_from_count_dict(raw_alignement_format_dict)
    mc.insert_annotated_alignment(corpus_name, annotated_alignment_to_save, current_data_point_nr)
    mc.insert_duplicates_for_annotated(corpus_name, current_data_point_nr)
    return "Annotations saved"


def delete_data_point(mc, corpus_name, current_data_point_nr):
    mc.insert_deleted_pair(corpus_name, current_data_point_nr)
    deleted_info = [str(current_data_point_nr)]
    happened = "Deleted data point " + " ".join(deleted_info)
    mc.insert_duplicates_for_annotated(corpus_name, current_data_point_nr)
    return happened

def list_available_corpora_from_database(mc):
    corpus_info = mc.get_all_corpus_info()

    corpus_infos = []
    for el in corpus_info:
        corpus_info = {}
        corpus_info[PATH] = "dummy"
        corpus_info[LANG1] = el[mc.LANG_1]
        corpus_info[LANG2] = el[mc.LANG_2]
        corpus_info[CORPUSNAME] = el[mc.CORPUS_NAME]
        corpus_info[CORPUSNAMEWITHLANGUAGE] = el[mc.CORPUS_NAME]
        corpus_infos.append(corpus_info)
       
    return corpus_infos


# corpus_name must exist in database
def select_unannotated_from_database(mc, corpus_name, select_difficult, do_active_selection, filter_str, alignment_method):
    info = mc.get_corpus_info(corpus_name)
    assert (info != None), "The name " + corpus_name + " does not exist in the database."
    
    alignments_ordered, sentences = mc.get_next_automatically_aligned(corpus_name,
                                                                      reverse = (not select_difficult),
                                                                      do_active_selection = do_active_selection,
                                                                      filter_str = filter_str)
    
    #TODO: This dict should be somewhere else
    alignment_method_dict = {"Gdfa" : mc.GDFA, "Intersection" : mc.INTERSECTION , "Embeddings" : mc.WITHEMBEDDING, "Empty" : mc.EMPTY, "EmbeddingGdfa" : mc.EFMARAL_AND_EMBEDDING_GDFA}
    if alignments_ordered:
        zero_count_dict_lang_1, zero_count_dict_lang_2  = produce_count_dict(alignments_ordered[alignment_method_dict[alignment_method]])
    else:
        zero_count_dict_lang_1 = None
        zero_count_dict_lang_2 = None
    return pack_next_data_point_info(mc, info, sentences, zero_count_dict_lang_1, zero_count_dict_lang_2)

def select_annotated_from_database(mc, corpus_name, datapoint_number,
                                     select_difficult, do_active_selection, reverse):
    info = mc.get_corpus_info(corpus_name)
    assert (info != None), "The name " + corpus_name + " does not exist in the database."
    
    alignments_ordered, sentences = mc.get_next_manually_annotated(corpus_name,
                                                                   datapoint_number,
                                                                   reverse)
    if alignments_ordered:
        zero_count_dict_lang_1, zero_count_dict_lang_2  = produce_count_dict(alignments_ordered[mc.ANNOTATION])
    else:
        zero_count_dict_lang_1 = None
        zero_count_dict_lang_2 = None

    return pack_next_data_point_info(mc, info, sentences, zero_count_dict_lang_1, zero_count_dict_lang_2)

def pack_next_data_point_info(mc, info, sentences, zero_count_dict_lang_1, zero_count_dict_lang_2):
    
    info_repacked = {}
    info_repacked[LANG1] = info[mc.LANG_1]
    info_repacked[LANG2] = info[mc.LANG_2]
    info_repacked[CORPUSNAME] = info[mc.CORPUS_NAME]
    info_repacked[CORPUSNAMEWITHLANGUAGE] = info[mc.CORPUS_NAME]
    
    if not sentences:
        return {"data_point" : None, "data_point_number": None,\
            "order_for_selected_in_current_ordering": None, "dir_info":  info_repacked}
    
    lang1_post_list = get_term_post_list(sentences[mc.SEG_1], zero_count_dict_lang_1)
    lang2_post_list = get_term_post_list(sentences[mc.SEG_2], zero_count_dict_lang_2)
    
    order = sentences[mc.ORDER]
    selected_results = [lang1_post_list, lang2_post_list]
  

    
    return {"data_point" : selected_results, "data_point_number": order,\
            "order_for_selected_in_current_ordering": order, "dir_info": info_repacked}




def test_select(corpus_name, mc):

    
    #  This must have been run in the mongo_connection_aligne
    #  print(mc.insert_corpus("test_name_2", "lang_1", "lang_2", paired_text_lists))
    #  alignments = [([(0, 0), (1, 1), (2, 2), (3, 4), (4, 3), (4, 5), (5, 5), (5, 6), (7, 6)], [(0, 0), (1, 1), (2, 2), (4, 3), (7, 6)]), ([(0, 1)], [(0, 0)])]
    #  mc.insert_automatic_alignments("test_name_2", alignments)
    lang1 = "de"
    lang2 = "sv"
    #name = "standard"
    
    
    datapoint_number = 20
    datapoint_order_for_current_ordering = 3
    print("Most difficult")
    print("-------------------")
    selections = select_next_data_point(mc, corpus_name, datapoint_number, datapoint_order_for_current_ordering, select_difficult = True, do_active_selection = True, select_annotated=False)
    
    print("selections", selections)
        #for nr, el in enumerate(selections):
        #print(el)


if __name__ == "__main__":
    
    from mongo_connector_align import MongoConnector
    mc = MongoConnector()
    
    corpus_name = "labour_market_social_security_de_sv"

    
    print("\n list_available_corpora_from_database")
    print("-----------------------------------\n")
    cs = list_available_corpora_from_database(mc)
    for el in cs:
        print(el)

    print("\n list_available_corpora()")
    print("-----------------------------------\n")
    ac = list_available_corpora()
    for el in ac:
        print(el)


    test_select(corpus_name, mc)

    print("\n select_data_point_from_corpus")
    print("-----------------------------------\n")
    print(select_unannotated_from_database(mc, corpus_name, 10, 3, True, True, True))

    original_list = [[0, 0], [1, 1], [2, 2], [3, 4], [4, 3], [4, 5], [5, 6]]
    print(original_list)
    dict = produce_count_dict(original_list)
    print(dict)
    lst = produce_database_alignment_format_from_count_dict(dict[0])
    print(lst)
