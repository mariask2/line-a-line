import pymongo
import datetime
import os
import json
import re
from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps

# An import that should function both locally and when running an a remote server
"""
try:
    from environment_configuration import *
except:
    from topics2themes.environment_configuration import *

if RUN_LOCALLY:
    from topic_model_constants import *
else:
    from topics2themes.topic_model_constants import *
"""

DEFAULT_DATABASE_NAME = "default_database_name_align"

class MongoConnector:
    def __init__(self):
        self.DATABASE = DEFAULT_DATABASE_NAME
       
        self.client = None
       
        self.DATE = "date"
        self.ID = "_id"
    
        self.CORPUS_NAME = "corpus_name"
        self.LANG_1 = "lang_1"
        self.LANG_2 = "lang_2"
        self.HAS_DIST_SEMANTICS_WORD_PAIRS = "has_dist_semantics_word_pairs"
        self.SEG_1 = "seg_1"
        self.SEG_2 = "seg_2"
        self.ORDER = "order"
        
        self.GDFA = "gdfa"
        self.INTERSECTION = "intersection"
        self.WITHEMBEDDING = "with_embedding"
        self.EMPTY = "empty"
        self.TIME = "time"
        self.CONFIDENCE = "confidence"
        
        self.ANNOTATION = "annotation"
        
        self.DUPLICATES = "duplicates"
        
        self.EMBEDDING_ALIGNMENT = "embedding_alignment"
        
        self.EFMARAL_AND_EMBEDDING_GDFA = "efmaral_and_embedding_gdfa"
        
        
        # The name of the corpus has to be unique (i.e., different names for the same corpus but with different language pairs
        self.get_corpus_metadata_collection().create_index([(self.CORPUS_NAME, pymongo.ASCENDING)], unique=True)
    
    def get_connection(self):
        maxSevSelDelay = 5 #Check that the server is listening, wait max 5 sec
        if not self.client:
            self.client = MongoClient(serverSelectionTimeoutMS=maxSevSelDelay)

        return self.client

    def close_connection(self):
        if self.client:
            self.client.close()
            self.client = None

    def get_database(self):
        con = self.get_connection()
        db = con[self.DATABASE]
        return db

    def get_all_collections(self):
        return self.get_database().collection_names()
    
    def get_corpus_metadata_collection(self):
        db = self.get_database()
        corpus_collection = db["CORPUS_COLLECTION"]
        return corpus_collection
    
    def get_sentence_pair_collection(self):
        db = self.get_database()
        sentence_pair_collection = db["SENTENDE_PAIR_COLLECTION"]
        return sentence_pair_collection

    def get_automatic_alignment_collection(self):
        db = self.get_database()
        automatic_alignment_collection = db["AUTOMATIC_ALIGNMENT_COLLECTION"]
        return automatic_alignment_collection
    
    def get_annotated_alignment_collection(self):
        db = self.get_database()
        automatic_alignment_collection = db["AUTOMATIC_ANNOTATION_COLLECTION"]
        return automatic_alignment_collection
    
    def get_deleted_pairs_collection(self):
        return self.get_database()["DELETED_PAIRS"]
    
    def get_duplicates_collection(self):
        return self.get_database()["DUPLICATES"]
    
    def get_extracted_vocabulary_collection(self):
        return self.get_database()["EXTRACTED_VOCABULARY"]
    
    def get_automatic_alignment_from_embedding_space_collection(self):
        return self.get_database()["AUTOMATIC_ALIGNMENT_FROM_EMBEDDING_COLLECTION"]
    
    # Contains the time when a new automatic alighment was last inserted
    def get_last_version_indicating_date_automatic_alignment_collection(self):
        db = self.get_database()
        return db["AUTOMATIC_ALIGNMENT_LAST_VERSION_COLLECTION"]


    ### Storing corpus data for a corpus and two languages
    def corpus_already_exists(self, corpus_name):
        if self.get_corpus_metadata_collection().find_one({self.CORPUS_NAME : corpus_name}):
            return True
        else:
            return False

    def insert_corpus_metadata(self, corpus_name, lang_1, lang_2, has_dist_semantics_word_pairs):
        post = {self.CORPUS_NAME: corpus_name, self.LANG_1: lang_1, self.LANG_2: lang_2, self.HAS_DIST_SEMANTICS_WORD_PAIRS: has_dist_semantics_word_pairs}
        self.get_corpus_metadata_collection().insert_one(post)

    def delete_corpus(self, corpus_name):
        self.get_corpus_metadata_collection().delete_many({self.CORPUS_NAME: corpus_name})
        self.get_sentence_pair_collection().delete_many({self.CORPUS_NAME: corpus_name})
        self.delete_automatic_alignments(corpus_name)
    
    def insert_paired_sentences(self, corpus_name, paired_text_lists):
        posts = []
        for nr,(seg_1, seg_2) in enumerate(paired_text_lists):
            posts.append({self.SEG_1: seg_1, self.SEG_2: seg_2, self.ORDER: nr, self.CORPUS_NAME: corpus_name})
        self.get_sentence_pair_collection().insert_many(posts)
    

    def insert_corpus(self, corpus_name, lang_1, lang_2, paired_text_lists):
        if self.corpus_already_exists(corpus_name):
            raise ValueError("There is already a corpus inserted with the name " + corpus_name)

        self.insert_paired_sentences(corpus_name, paired_text_lists)
        try:
            self.insert_corpus_metadata(corpus_name, lang_1, lang_2, False) # TODO:  Add word pairs later
        except:
            self.get_sentence_pair_collection().delete_many({self.CORPUS_NAME: corpus_name}) # If the creation of corpus metadata was unsuccessfull, delete sentence pairs storted for this
            raise

    def insert_automatic_alignments(self, corpus_name, alignments):
        posts = []
        time = datetime.datetime.utcnow()
        for nr, (gdfa, intersection, with_embedding, efmaral_and_embedding_gdfa, confidence) in enumerate(alignments):
            post = {self.GDFA: gdfa,
                    self.INTERSECTION: intersection,
                    self.ORDER: nr,
                    self.CORPUS_NAME: corpus_name,
                    self.TIME: time,
                    self.WITHEMBEDDING: with_embedding,
                    self.EFMARAL_AND_EMBEDDING_GDFA: efmaral_and_embedding_gdfa,
                    self.CONFIDENCE : confidence}
            posts.append(post)

        self.get_automatic_alignment_collection().insert_many(posts)
        self.insert_last_version_indicating_time_automatic_alignment(time, corpus_name)


    def delete_automatic_alignments(self, corpus_name):
        self.get_automatic_alignment_collection().delete_many({self.CORPUS_NAME: corpus_name})
    
    def insert_automatic_alignment_from_embedding_space(self, corpus_name, order_nr, alignment):
        self.get_automatic_alignment_from_embedding_space_collection().insert_one({self.CORPUS_NAME: corpus_name,
                                                                                  self.ORDER: order_nr,
                                                                                  self.EMBEDDING_ALIGNMENT: alignment})
    def get_automatic_alignment_from_embedding_space(self, corpus_name, order_nr):
        res = self.get_automatic_alignment_from_embedding_space_collection().find_one({self.CORPUS_NAME: corpus_name,
                                                                                self.ORDER: order_nr})
        return [tuple(el) for el in res[self.EMBEDDING_ALIGNMENT]]
    
    ### Retrieving corpus data
    def get_all_sentence_pairs_in_corpus(self, corpus_name):
        return self.get_sentence_pair_collection().find({self.CORPUS_NAME: corpus_name}).sort(self.ORDER, pymongo.ASCENDING)

    def get_all_sentence_pairs_in_corpus_fastalign_format(self, corpus_name, reverse=False):
        result_list = []
        c = self.get_all_sentence_pairs_in_corpus(corpus_name)
        for el in c:
            if reverse:
                result_list.append((" ".join(el[self.SEG_2]) + " ||| " + " ".join(el[self.SEG_1])))
            else:
                result_list.append((" ".join(el[self.SEG_1]) + " ||| " + " ".join(el[self.SEG_2])))
        return result_list
    
    def get_all_sentence_pairs_in_corpus_that_match_segments(self, corpus_name, seg_1, seg_2):
        return self.get_sentence_pair_collection().find({self.CORPUS_NAME: corpus_name,
                                                        self.SEG_1: seg_1,
                                                        self.SEG_2: seg_2})

    # TODO: This is both slow and case sensitive. Also not used at the moment, the code used is even slower
    def get_all_sentence_pairs_in_corpus_that_contain_token(self, corpus_name, token, reverse = False):
        if not reverse:
            return [el[mc.ORDER] for el in self.get_sentence_pair_collection().find({self.CORPUS_NAME: corpus_name, self.SEG_1: token})]
        else:
            return [el[mc.ORDER] for el in self.get_sentence_pair_collection().find({self.CORPUS_NAME: corpus_name, self.SEG_2: token})]

    def get_all_automatic_alignments(self, corpus_name):
        return self.get_automatic_alignment_collection().find({self.CORPUS_NAME: corpus_name})
    
    def insert_last_version_indicating_time_automatic_alignment(self, time, corpus_name):
        self.get_last_version_indicating_date_automatic_alignment_collection().insert({self.TIME: time, self.CORPUS_NAME:corpus_name})
    
    def find_last_version_indicating_time_automatic_alignment(self, corpus_name):
        saved_time_objects = self.get_last_version_indicating_date_automatic_alignment_collection().find({self.CORPUS_NAME:corpus_name}).sort([(self.TIME,pymongo.DESCENDING)])
        most_recent_time = saved_time_objects.next()[self.TIME]
        return most_recent_time
    
    def get_all_corpus_info(self):
        return self.get_corpus_metadata_collection().find({})

    def do_filter_on_str(self, filtered_alignment_list, corpus_name, filter_str):
        if filter_str != "":
            filtered_alignment_list_filtered_on_words = []
            for el in filtered_alignment_list:
                sentence_pair = self.get_sentence_pair_collection().find_one({self.CORPUS_NAME: corpus_name, self.ORDER: el[self.ORDER]})
                if filter_str.lower() in [w.lower() for w in sentence_pair[self.SEG_1]] or\
                    filter_str.lower() in [w.lower() for w in sentence_pair[self.SEG_2]]:
                        filtered_alignment_list_filtered_on_words.append(el)
            return filtered_alignment_list_filtered_on_words
        else:
            return filtered_alignment_list
        
    def get_next_automatically_aligned(self, corpus_name, reverse, do_active_selection, filter_str):
        last_version_time = self.find_last_version_indicating_time_automatic_alignment(corpus_name)
        all_alignments_for_last_automatic_version = \
            [el for el in self.get_automatic_alignment_collection().find({self.CORPUS_NAME: corpus_name, self.TIME: last_version_time})]
        manually_annotated_alignments = [el for el in self.get_all_annotated_alignments(corpus_name)]
        manually_annotated_nrs_for_corpus = [el[self.ORDER] for el in manually_annotated_alignments]
        deleted_nrs_for_corpus = [el[self.ORDER] for el in self.get_deleted_pairs(corpus_name)]
        
        # Make sure that the exact same sentence pairs don't need to be annotated more than once
        duplicates_list = self.get_duplicates_collection().find({self.CORPUS_NAME: corpus_name})
        flattened_duplicates_list = []
        for el in duplicates_list:
            flattened_duplicates_list.extend(el[self.DUPLICATES])
        flattened_duplicates_list = list(set(flattened_duplicates_list))
        
        print("flattened_duplicates_list", flattened_duplicates_list)
        
        # Include the ones not annotated
        filtered_alignment_list = \
            [el for el in all_alignments_for_last_automatic_version if el[self.ORDER] not in manually_annotated_nrs_for_corpus
             and el[self.ORDER] not in deleted_nrs_for_corpus and el[self.ORDER] not in flattened_duplicates_list]

        # Filter to only include sentence pairs with a particular string
        filtered_alignment_list_filtered_on_words = self.do_filter_on_str(filtered_alignment_list, corpus_name, filter_str)

        
        print("Number of not annotatated", len(filtered_alignment_list))
        print("Number of not annotatated with word filter criterium", len(filtered_alignment_list_filtered_on_words))
        
        if do_active_selection:  # Filter according to how difficult they are. Order depends on the reverse flag
            filtered_alignment_list_filtered_on_words = \
                sorted(filtered_alignment_list_filtered_on_words, key=lambda k: k[self.CONFIDENCE], reverse=reverse)

        if len(filtered_alignment_list_filtered_on_words) > 0:
            alignments_to_select = filtered_alignment_list_filtered_on_words[0]
            sentences = self.get_sentence_pair_collection().find_one({self.CORPUS_NAME: corpus_name, self.ORDER: alignments_to_select[self.ORDER]})
            
            # Add the option to not have any pre-alignments at all
            alignments_to_select[self.EMPTY] = []
        else:
            alignments_to_select = None
            sentences = None
        return alignments_to_select, sentences
    
    # It's always allowed to redo the most recent annotation, even if that annotation was done a long time ago. Perhaps this should be changed
    def get_next_manually_annotated(self, corpus_name, datapoint_number, reverse):
 
        manually_annotated_alignments = [el for el in self.get_all_annotated_alignments(corpus_name)]
        deleted_for_corpus = [el for el in self.get_deleted_pairs(corpus_name)]
        annotated_list = manually_annotated_alignments + deleted_for_corpus
        
        annotated_list = sorted(annotated_list, key=lambda k: k[self.TIME])
        
        

        if reverse:
            step = -1
        else:
            step = 1
        
        nrs_in_annotated_list = [el[self.ORDER] for el in annotated_list]

        assert len(nrs_in_annotated_list) == len(list(set(nrs_in_annotated_list))), "The same annotation is saved several times"

        if datapoint_number == -1:
            # datapoint_number == -1 --> when a corpus is opened an the first sentence is looked at
            index_to_select = 0
        elif datapoint_number in nrs_in_annotated_list:
            index_for_last_point = nrs_in_annotated_list.index(datapoint_number)
            #Can never step back more than till the first or forward to last
            if (index_for_last_point == 0 and reverse) or (index_for_last_point == len(annotated_list) - 1 and not reverse):
                index_to_select = None
            else:
                index_to_select = index_for_last_point + step
        else:
            index_to_select = len(annotated_list) - 1

        # if datapoint_number in nrs_in_annotated_list, the user is browsing among annotated
        # if not, the current data point has not been annotaded, so the the point most recently
        # annotated is to be select = index_to_select -1
        
        if index_to_select != None: #Can never step back more than till the first or forward to last
            alignments_to_select = annotated_list[index_to_select]
            sentences = self.get_sentence_pair_collection().find_one({self.CORPUS_NAME: corpus_name, self.ORDER: alignments_to_select[self.ORDER]})
        else:
            alignments_to_select = None
            sentences = None
        
        return alignments_to_select, sentences


    def get_corpus_info(self, corpus_name):
        return self.get_corpus_metadata_collection().find_one({self.CORPUS_NAME: corpus_name})

    # Save annotations in the database
    # If there is already an annotation for this sentence, it will be updated
    def insert_annotated_alignment(self, corpus_name, alignment, nr):
        self.get_deleted_pairs_collection().delete_one({self.CORPUS_NAME: corpus_name,
                                                       self.ORDER: nr}) # Cannot be both in inserted and deleted. If fails, the user have to re-annotate
        time = datetime.datetime.utcnow()
        print("annotated alignments", alignment)
        res = self.get_annotated_alignment_collection().replace_one({self.CORPUS_NAME: corpus_name, self.ORDER: nr},
                                                              {self.CORPUS_NAME: corpus_name, self.ORDER: nr,
                                                                    self.ANNOTATION: alignment, self.TIME: time}, upsert = True)
        return res

    def get_all_annotated_alignments(self, corpus_name):
        #sort_order = pymongo.ASCENDING
        return self.get_annotated_alignment_collection().find({self.CORPUS_NAME: corpus_name}) #.sort(self.TIME, sort_order)
    
    def insert_deleted_pair(self, corpus_name, nr):
        self.get_annotated_alignment_collection().delete_one({self.CORPUS_NAME: corpus_name, self.ORDER: nr})
         # Cannot be both in inserted and deleted. If fails, the user have to re-annotate
        time = datetime.datetime.utcnow()
        res = self.get_deleted_pairs_collection().replace_one({self.CORPUS_NAME: corpus_name,
                                                              self.ORDER: nr},
                                                              {self.CORPUS_NAME: corpus_name,
                                                             self.ORDER: nr,
                                                             self.TIME: time,
                                                             self.ANNOTATION: []}, upsert = True) # Empty annotation
        print("res", res)
        return res
    
    def get_deleted_pairs(self, corpus_name):
        return self.get_deleted_pairs_collection().find({self.CORPUS_NAME: corpus_name})

    def insert_duplicates_for_annotated(self, corpus_name, nr):
        sentence_pair = self.get_sentence_pair_collection().find_one({self.CORPUS_NAME: corpus_name, self.ORDER: nr})
        matches = self.get_all_sentence_pairs_in_corpus_that_match_segments(corpus_name, sentence_pair[self.SEG_1], sentence_pair[self.SEG_2])
        duplicate_numbers = [match[self.ORDER] for match in matches if match[self.ORDER] != nr]
        self.get_duplicates_collection().insert_one({self.CORPUS_NAME: corpus_name, self.ORDER: nr, self.DUPLICATES: duplicate_numbers})

    def insert_extracted_vocabulary(self, corpus_name, match_list):
        posts = []
        for (seg_1, seg_2) in match_list:
            posts.append({self.SEG_1: seg_1, self.SEG_2: seg_2, self.CORPUS_NAME: corpus_name})
        self.get_extracted_vocabulary_collection().insert_many(posts)

    def get_extracted_vocabulary(self, corpus_name):
        return self.get_extracted_vocabulary_collection().find({self.CORPUS_NAME: corpus_name})

    def get_extracted_vocabulary_in_fastalign_format(self, corpus_name, reverse=False):
        result_list = []
        c = self.get_extracted_vocabulary(corpus_name)
        for el in c:
            if reverse:
                result_list.append(el[self.SEG_2] + " ||| " + el[self.SEG_1])
            else:
                result_list.append(el[self.SEG_1] + " ||| " + el[self.SEG_2])
        return result_list

###
# Start
###
if __name__ == '__main__':
    mc = MongoConnector()
    print(mc.get_connection())
    print(mc.get_database())
    print(mc.get_all_collections())
    print(mc.delete_corpus("test_name"))
    print(mc.corpus_already_exists("test_name"))
    mc.insert_corpus_metadata("test_name", "lang_1", "lang_2", False)
    print(mc.get_all_collections())
    print(mc.corpus_already_exists("test_name"))
    paired_text_lists = [(['Unterschrift'], ['Namnteckning']), (['Name', 'in', 'Druckbuchstaben'], ['Namnförtydligande']), (['Unterschrift'], ['Namnteckning'])]
    print(mc.delete_corpus("test_name_2"))
    print(mc.insert_corpus("test_name_2", "lang_1", "lang_2", paired_text_lists))
    c = mc.get_all_sentence_pairs_in_corpus("test_name_2")
    for el in c:
        print(el)
    print("Test segment comparison")
    compare_with_1 =  ['Unterschrift']
    compare_with_2 =  ['Namnteckning']
    returned = mc.get_all_sentence_pairs_in_corpus_that_match_segments("test_name_2", compare_with_1, compare_with_2)
    for el in returned:
        print("el", el)
    print(mc.delete_corpus("test_name_3"))
    print(mc.insert_corpus("test_name_3", "lang_1", "lang_2", paired_text_lists))
    print(mc.get_all_sentence_pairs_in_corpus_fastalign_format("test_name_2"))
    mc.delete_automatic_alignments("test_name_2")
    print("deleted alignments")
    alignments = [([[0, 0], [1, 1], [2, 9], [3, 10], [4, 8], [5, 11], [6, 12], [7, 2], [7, 13], [8, 3], [9, 2], [9, 4], [10, 3], [10, 5], [11, 6], [12, 7]],[[1, 1], [9, 2], [10, 3]], [[1, 1], [9, 2], [10, 3]], 0.05),
         ([[0, 0], [1, 1], [2, 2], [3, 4], [4, 3], [4, 5], [5, 6]],[[0, 0], [1, 1], [2, 2], [4, 3]], [[1, 1], [9, 2], [10, 3]], 0.9)]
        #alignments = [
#           [(0, 0, 0.3), (1, 1, 0.3), (2, 2, 0.3), (3, 4, 0.9), (4, 3, 0.3), (4, 5, 0.1), (5, 5, 0.3), (5, 6, 0.3), (7, 6, 0.3)], [(0, 0, 0.4), (1, 1, 0.4), (2, 2, 0.8), (4, 3, 0.4), (7, 6, 0.2)]), ([(0, 1, 0.5)], [(0, #0, 0.6)])]
    mc.insert_automatic_alignments("test_name_2", alignments)
    c = mc.get_all_automatic_alignments("test_name_2")
    for el in c:
     print(el)
   
    print(mc.find_last_version_indicating_time_automatic_alignment("test_name_2"))

    print("Next alignment not reversed", mc.get_next_automatically_aligned("test_name_2", False, True))
    print("Next alignment reversed", mc.get_next_automatically_aligned("test_name_2", True,True))

    c = mc.get_all_corpus_info()
    for el in c:
        print(el)

    print("mc.get_corpus_info('test_name_2')", mc.get_corpus_info("test_name_2"))

    print("insert_annotated_alignment", mc.insert_annotated_alignment("test_name_2", alignments, 5))
    print("insert_annotated_alignment", mc.insert_annotated_alignment("test_name_2", alignments, 5))
    print("insert_annotated_alignment", mc.insert_annotated_alignment("test_name_2", alignments, 1))
    print("insert_annotated_alignment", mc.insert_annotated_alignment("test_name_3", alignments, 4))
    c = mc.get_all_annotated_alignments("test_name_2")
    print("get_all_annotated_alignments")
    for el in c:
        print(el)
    c = mc.get_all_annotated_alignments("test_name_2")
    print("alignments", [el[mc.ORDER] for el in c])
    print(mc.insert_deleted_pair("test_name_2", 500))
    c = mc.get_deleted_pairs("test_name_2")
    for el in c:
        print(el)

    print("Search token")
    print(mc.get_all_sentence_pairs_in_corpus_that_contain_token("test_name_2", "Unterschrift", reverse = False))


    print(mc.get_all_sentence_pairs_in_corpus_that_contain_token("test_name_2", "Namnteckning", reverse = True))



