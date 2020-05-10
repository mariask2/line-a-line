import run_aligner
import tempfile
import os
import nltk.translate.gdfa as gdfa


def run_aligner_on_fastalign(fastalign_format):
    res = None
    fastalign_format_str = "\n".join(fastalign_format) + "\n"
    with tempfile.TemporaryDirectory() as td:
        f_name = os.path.join(td, 'temp')
        with open(f_name, 'w') as fh:
            fh.write(fastalign_format_str)
            res = run_aligner.do_align(inputs = [f_name], seed = None)
    return res

def get_intersection(res_el_filtered, res_reversed_el_filtered):
    # Converts pharaoh text format into list of tuples.
    tuples_reversed = [tuple(map(int, a.split('-'))) for a in res_reversed_el_filtered.split()]
    tuples_reversed_flipped = [(b,a) for (a,b) in tuples_reversed]
    tuples = [tuple(map(int, a.split('-'))) for a in res_el_filtered.split()]

    intersection = (set(tuples_reversed_flipped)).intersection(set(tuples))
    return list(intersection)


def do_process_alignments(corpus_lang_name, mongo_connector):
    # One direction
    fastalign_format = mongo_connector.get_all_sentence_pairs_in_corpus_fastalign_format(corpus_lang_name)
    vocabulary = mongo_connector.get_extracted_vocabulary_in_fastalign_format(corpus_lang_name)
    res = run_aligner_on_fastalign(fastalign_format + vocabulary)
    
    #print(fastalign_format[:10])
    print(vocabulary[:10])
    
    # The other direction
    fastalign_format_reversed = mongo_connector.get_all_sentence_pairs_in_corpus_fastalign_format(corpus_lang_name, reverse=True)
    vocabulary_reverse = mongo_connector.get_extracted_vocabulary_in_fastalign_format(corpus_lang_name, reverse=True)
    res_reversed = run_aligner_on_fastalign(fastalign_format_reversed + vocabulary_reverse)
    

    
    #print(fastalign_format_reversed[:10])
    #print(vocabulary_reverse[:10])
    
    result_list = []
    for nr, (res_el, res_reversed_el, text) in enumerate(zip(res[:len(fastalign_format)], res_reversed[:len(fastalign_format)], fastalign_format)):
        [lang_1, lang_2] = text.split("|||")
        lang_1 = lang_1.strip()
        lang_2 = lang_2.strip()
        lang_1_len = len(lang_1.split())
        lang_2_len = len(lang_2.split())
        
        # For some reason, alignements with a word in only one of the languages is returned. Remove these
        res_el_filtered = " ".join([a for a in res_el.split() if a[-1] != "-"])
        res_reversed_el_filtered = " ".join([a for a in res_reversed_el.split() if a[-1] != "-"])


        gdfa_output = sorted(gdfa.grow_diag_final_and(lang_1_len, lang_2_len, res_el_filtered, res_reversed_el_filtered))
        intersection_output = sorted(get_intersection(res_el_filtered, res_reversed_el_filtered))
        confidence = len(intersection_output)/(lang_1_len + lang_2_len)/2

        embedding_alignment = mongo_connector.get_automatic_alignment_from_embedding_space(corpus_lang_name, nr)

        embedding_alignment_reversed = [(b, a) for (a, b) in embedding_alignment]
        
        print("embedding_alignment", embedding_alignment)
        print("intersection_output", intersection_output)
        embedding_union_intersection_output = sorted(list(set(embedding_alignment + intersection_output)))
        print("embedding_union_intersection_output", embedding_union_intersection_output)
        print("gdfa_output", gdfa_output)
        
       
         # Combine the results from embedding-alignments and from efmaral, and the do gdfa on those
        res_ls = [a for a in res_el_filtered.split()]
        res_tuples = [(int(b), int(c)) for (b,c) in [tuple(a.split("-")) for a in res_ls]]
        res_reversed_ls = [a for a in res_reversed_el_filtered.split()]
        res_tuples_reversed = [(int(b), int(c)) for (b,c) in [tuple(a.split("-")) for a in res_reversed_ls]]
        res_and_embedding = " ".join([str(a) + "-" + str(b) for (a, b) in sorted(list(set(res_tuples) & set(embedding_alignment)))])
        res_and_embedding_reversed = " ".join([str(a) + "-" + str(b) for (a, b) in sorted(list(set(res_tuples_reversed) & set(embedding_alignment_reversed)))])

        #print("res_and_embedding", res_and_embedding)
        #print("res_and_embedding_reversed", res_and_embedding_reversed)
        #print("res_el_filtered", res_el_filtered)

        gdfa_res_and_embedding = sorted(gdfa.grow_diag_final_and(lang_1_len, lang_2_len, res_and_embedding, res_and_embedding_reversed))
        print("embedding_gdfa", gdfa_res_and_embedding)
        result_list.append((gdfa_output, intersection_output, embedding_union_intersection_output, gdfa_res_and_embedding, confidence))
    
    
    mongo_connector.insert_automatic_alignments(corpus_lang_name, result_list)
    


