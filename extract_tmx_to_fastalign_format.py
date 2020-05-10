# -*- coding: utf-8 -*-

# python 3
import os
import xml.etree.ElementTree as ET
#from nltk.translate import AlignedSent, Alignment, IBMModel5, IBMModel2, IBMModel3
from nltk.tokenize import TweetTokenizer
import extract_vocabulary_from_aligned_spaces
from mongo_connector_align import MongoConnector
import process_alignments

def get_name_from_corpus_and_langs(name, lang_1, lang_2):
    return name + "_" + lang_1 + "_" + lang_2

def run_extract_and_convert(name, files, lang_1, lang_2, lang1_path, lang2_path, lang1_stopword_name, lang2_stopword_name):
    
    mc = MongoConnector()

    tknzr = TweetTokenizer(preserve_case=True)
    lang_1_word_dict = {}
    lang_2_word_dict = {}
    paired_text_lists = []
    processed_sentence_pairs = 0
    for file in files:
        tree = ET.parse(file)
        root = tree.getroot()
        for tu in root.iter('tu'):
            for tuv_1, tuv_2 in zip(tu, tu[1:]):
                processed_sentence_pairs = processed_sentence_pairs + 1
                lang_tuv_1 = tuv_1.attrib['{http://www.w3.org/XML/1998/namespace}lang']
                lang_tuv_2 = tuv_2.attrib['{http://www.w3.org/XML/1998/namespace}lang']
                assert(lang_1 == lang_tuv_1)
                assert(lang_2 == lang_tuv_2)
                seg_1 = None
                seg_2 = None
                for seg in tuv_1:
                    seg_1 = tknzr.tokenize(seg.text)
                for seg in tuv_2:
                    seg_2 = tknzr.tokenize(seg.text)
                
                paired_text_lists.append((seg_1, seg_2))

    print("Read " + str(len(paired_text_lists)) + " lines from " + str(len(files)) + " files." )

    corpus_lang_name = get_name_from_corpus_and_langs(name, lang_1, lang_2)
    
    # Get the automatically constructed lexicon
    lang1_lines = [seg_1 for (seg_1, seg_2) in paired_text_lists]
    lang2_lines = [seg_2 for (seg_1, seg_2) in paired_text_lists]
    match_list = extract_vocabulary_from_aligned_spaces.do_extract_vocabulary(mc, corpus_lang_name, lang1_lines, lang2_lines, lang1_stopword_name, lang2_stopword_name, lang1_path, lang2_path, lang_1, lang_2)


    mc.insert_extracted_vocabulary(corpus_lang_name, match_list)
    voc = [el for el in mc.get_extracted_vocabulary(corpus_lang_name)]
    
    # TODO: Remove when finished debugging
    mc.delete_corpus(corpus_lang_name)



    mc.insert_corpus(corpus_lang_name, lang_1, lang_2, paired_text_lists)
    
    # Add the pre-alignments between sentences and save to database
    process_alignments.do_process_alignments(corpus_lang_name, mc)
    
    """
    c = mc.get_all_automatic_alignments(corpus_lang_name)
    for el in c:
        print(el)
    """




 

