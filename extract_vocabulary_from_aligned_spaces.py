# -*- coding: utf-8 -*-
import io
import numpy as np
from nltk.corpus import stopwords

MIN_ALLOWED_WORD_LENGTH = 4
punctuation = [".", ",", ":", ";", "?", "!", "___", "__", "_", ")", "(", "/", "]", "[","–", "-"  ]

# Load the word2vec space for the words included in the corpus, as well as for subwords of the words included in the corpus
def load_vec(emb_path, word_set, stopwords, nmax):
    vectors = []
    word2id = {}
    
    potential_vectors = []
    potential_word2id = {}
    
    with io.open(emb_path, 'r', encoding='utf-8', newline='\n', errors='ignore') as f:
        next(f)
        for i, line in enumerate(f):
            word, vect = line.rstrip().split(' ', 1)
            vect = np.fromstring(vect, sep=' ')
            assert word not in word2id, 'word found twice'
            if word in stopwords and word in punctuation:
                continue
            elif word in word_set : # only include words found in the corpus
                vectors.append(vect)
                word2id[word] = len(word2id)
                if len(word2id) == nmax:
                    break
            else:
                potential_vectors.append(vect)
                potential_word2id[word] = len(potential_word2id)


    subword_dict = {}
    
    for corpus_word in word_set:
        if corpus_word not in word2id and corpus_word not in stopwords and corpus_word not in punctuation and not includes_number(corpus_word) and len(corpus_word) >= MIN_ALLOWED_WORD_LENGTH:
            subwords = list_subwords(corpus_word, potential_word2id)
            if subwords:
                subword_dict[corpus_word] = subwords
                for subword in subwords:
                    if subword not in word2id:
                        subword_vector = potential_vectors[potential_word2id[subword]]
                        vectors.append(subword_vector)
                        word2id[subword] = len(word2id)

    id2word = {v: k for k, v in word2id.items()}
    embeddings = np.vstack(vectors)
    #print(len(word2id))
    #print(len(id2word))
    return embeddings, id2word, word2id, subword_dict


def get_nn(word, src_emb, src_id2word, src_word2id, tgt_emb, tgt_id2word, K, cashes, lang_identifier):
    cash_to_use = cashes[lang_identifier][K]
    if word in cash_to_use:
        return cash_to_use[word]


    #print("Nearest neighbors of \"%s\":" % word)
    #word2id = {v: k for k, v in src_id2word.items()}
    word = word.lower()
    if word in src_word2id:
        word_emb = src_emb[src_word2id[word]]
        scores = (tgt_emb / np.linalg.norm(tgt_emb, 2, 1)[:, None]).dot(word_emb / np.linalg.norm(word_emb))
        k_best = scores.argsort()[-K:][::-1]
        result = []
        for i, idx in enumerate(k_best):
            result.append((scores[idx], tgt_id2word[idx]))
            #print('%.4f - %s' % (scores[idx], tgt_id2word[idx]))
        cash_to_use[word] = result
        return result
    else:
        cash_to_use[word] = None
        return None

def get_vocabulary(lines):
    words = set()
    for line in lines:
        for el in line:
            words.add(el.lower())
    return words


def includes_number(w):
    if "/" in w or "." in w:
        return True
    for i in range(0, 10):
        if str(i) in w:
            return True
    return False

# For a word, extract possible subwords (and only allow subwords that are included in the word space)
def list_subwords(word, src_word2id):
    subwords = []
    for i in range(len(word)-1, MIN_ALLOWED_WORD_LENGTH-1, -1):
        subword = word[0:i].lower()
        if subword in src_word2id:
            subwords.append(subword)
    for i in range(4, len(word)-MIN_ALLOWED_WORD_LENGTH):
        subword = word[i:].lower()
        if subword in src_word2id:
            subwords.append(subword)
    return subwords


def do_words_match(lang1_word, lang2_word, lang2_neighbours, lang1_neighbours, top_n):
    lang1_word = lang1_word.lower()
    lang2_word = lang2_word.lower()

    if lang1_word == lang2_word: # sometimes, a Swedish word is used in the german text, so then they should match
        return True
    
    # For a word pair in languages ax and by to be considered a match, ax most be included among the nearest neighbours of by
    # and by must be included in among the nearest neighbours of ax:
    if lang2_neighbours and lang1_neighbours:
        if lang1_word in [ws for (val, ws) in lang2_neighbours] and lang2_word in [wd for (val, wd) in lang1_neighbours]:
            return True

    if not lang2_neighbours:
        return False
    
    if not lang1_neighbours:
        return False

    return False

def do_subwords_match(lang1_word, lang2_word, top_n):
    get_subwords(lang2_word, lang2_embeddings, lang2_id2word, lang2_word2id, lang1_embeddings, lang1_id2word, top_n)






# match_list stores the found matches
# Loop through each word pairs in the two sentences, to evaluate whether these word pairs are a possible match.
def find_matches_for_line(lang2_split, lang1_split, match_list, top_n, lang1_embeddings, lang1_id2word, lang1_word2id, lang1_subword_list, lang1_stopwords, lang1_identifier, lang2_embeddings, lang2_id2word, lang2_word2id, lang2_subword_list, lang2_stopwords, lang2_identifier, cashes, reverse=False):
    not_found = 0
    found_index_tuples = []
    lang1_found_indeces = [] # To monitor if there are words for which no match is found
    for lang2_index, lang2_word in enumerate(lang2_split):
        found_match = False
        if lang2_word in punctuation or lang2_word.lower() in lang2_stopwords or includes_number(lang2_word):
            continue
        lang2_neighbours = get_nn(lang2_word, lang2_embeddings, lang2_id2word, lang2_word2id, lang1_embeddings, lang1_id2word, top_n, cashes, lang2_identifier)
        for lang1_index, lang1_word in enumerate(lang1_split):
            if lang1_word in punctuation or lang1_word.lower() in lang1_stopwords or includes_number(lang1_word):
                continue
            lang1_neighbours = get_nn(lang1_word, lang1_embeddings, lang1_id2word, lang1_word2id, lang2_embeddings, lang2_id2word, top_n, cashes, lang1_identifier)
            if do_words_match(lang1_word, lang2_word, lang2_neighbours, lang1_neighbours, top_n):
                    if reverse:
                        match_list.append((lang2_word, lang1_word))
                        found_index_tuples.append((lang2_index, lang1_index))
                    else:
                        match_list.append((lang1_word, lang2_word))
                        found_index_tuples.append((lang1_index, lang2_index))
                    found_match = True
                    lang1_found_indeces.append(lang1_index)
            
        if not found_match:
            # if no match is found for lang2_word, also try with subwords
            for lang1_index, lang1_word in enumerate(lang1_split):
                if lang1_word in punctuation or lang1_word.lower() in lang1_stopwords or includes_number(lang1_word) \
                        or (lang1_word.lower() not in lang1_subword_list and lang2_word.lower() not in lang2_subword_list):
                    continue
                lang1_word_and_subwords = [lang1_word.lower()]
                if lang1_word.lower() in lang1_subword_list:
                    lang1_word_and_subwords = lang1_word_and_subwords + lang1_subword_list[lang1_word.lower()]
                lang2_word_and_subwords = [lang2_word.lower()]
                if lang2_word in lang2_subword_list:
                    lang2_word_and_subwords = lang2_word_and_subwords + lang2_subword_list[lang2_word.lower()]
                for lang2_subword in lang2_word_and_subwords:
                    lang2_neighbours = get_nn(lang2_subword, lang2_embeddings, lang2_id2word, lang2_word2id, lang1_embeddings, lang1_id2word, top_n, cashes, lang2_identifier)
                    for lang1_subword in lang1_word_and_subwords:
                        lang1_neighbours = get_nn(lang1_subword, lang1_embeddings, lang1_id2word, lang1_word2id, lang2_embeddings, lang2_id2word, top_n, cashes, lang1_identifier)
                        if do_words_match(lang1_subword, lang2_subword, lang2_neighbours, lang1_neighbours, top_n):
                            lang1_found_indeces.append(lang1_index)
                            #print("found", lang1_subword, lang2_subword)
                            if reverse:
                                match_list.append((lang2_word, lang1_word))
                                found_index_tuples.append((lang2_index, lang1_index))
                            else:
                                match_list.append((lang1_word, lang2_word))
                                found_index_tuples.append((lang1_index, lang2_index))
                            found_match = True
        
        if not found_match:
            #print("not found:", lang2_word)
            #print(lang2_line, lang1_line)
            not_found = not_found + 1
    return lang1_found_indeces, not_found, found_index_tuples

def do_extract_vocabulary(mc, corpus_name, lang1_lines, lang2_lines, lang1_stopword_name, lang2_stopword_name, lang1_path, lang2_path, lang1_identifier, lang2_identifier, nmax=1000000):
    
    print("identifiers: ", lang1_identifier, lang2_identifier)
    lang1_words = get_vocabulary(lang1_lines)
    lang2_words = get_vocabulary(lang2_lines)
    
    lang1_stopwords = set(stopwords.words(lang1_stopword_name))
    lang2_stopwords = set(stopwords.words(lang2_stopword_name))

    lang1_embeddings, lang1_id2word, lang1_word2id, lang1_subword_list = load_vec(lang1_path, lang1_words, lang1_stopwords, nmax)
    lang2_embeddings, lang2_id2word, lang2_word2id, lang2_subword_list = load_vec(lang2_path, lang2_words, lang2_stopwords, nmax)

    total_not_found = 0
    match_list = [] # Stores the found matches
    
    cashes = {}
    
    top_n_first_attempt = 2
    top_n_second_attempt = top_n_first_attempt + 18
    
    cashes[lang1_identifier] = {}
    cashes[lang2_identifier] = {}
    
    cashes[lang1_identifier][top_n_first_attempt] = {}
    cashes[lang1_identifier][top_n_second_attempt] = {}
    cashes[lang2_identifier][top_n_first_attempt] = {}
    cashes[lang2_identifier][top_n_second_attempt] = {}
    
    for lang_nr, (lang2_line, lang1_line) in enumerate(zip(lang2_lines, lang1_lines)):
        lang1_found_indeces, not_found, found_index_tuples  = find_matches_for_line(lang2_line, lang1_line, match_list, top_n_first_attempt, lang1_embeddings, lang1_id2word, lang1_word2id, lang1_subword_list, lang1_stopwords, lang1_identifier, lang2_embeddings, lang2_id2word, lang2_word2id, lang2_subword_list, lang2_stopwords, lang2_identifier, cashes)
        total_not_found = total_not_found + not_found
    
        # if there is a word for Swedish, for which no German equivalent is found run in opposite direction, with just those words for which no match is found
        # also allow a wider neighbour search (search in the top_n_second_attempt nr of neighbours instead in the top_n_first_attempt nearest neighbours)
        # "lang1_to_study" stores those indeces
        lang1_found_indeces = [int(ind) for ind in lang1_found_indeces]
        lang1_to_study = []
        for index in range(0, len(lang1_line)):
            if index not in lang1_found_indeces:
                lang1_to_study.append(lang1_line[index])

        lang1_found_indeces, not_found, found_index_tuples_reverse = find_matches_for_line(lang1_to_study, lang2_line, match_list, top_n_second_attempt, lang2_embeddings, lang2_id2word, lang2_word2id, lang2_subword_list, lang2_stopwords, lang2_identifier, lang1_embeddings, lang1_id2word, lang1_word2id, lang1_subword_list, lang1_stopwords, lang1_identifier, cashes, reverse=True)
        if not_found == 1:
            pass
        total_found_index_tuples = [tuple(el) for el in found_index_tuples + found_index_tuples_reverse]
        
        #print("****")
        #print(total_found_index_tuples)
        #print(lang2_line, lang1_line)

        mc.insert_automatic_alignment_from_embedding_space(corpus_name, lang_nr, total_found_index_tuples)
    print("total_not_found", total_not_found)
    return match_list




if __name__ == "__main__":
    f = open("temp_neighbour.txt", "w")
    
    lang1_path = '/Users/maria/sprakresurser/muse/MUSE/data/wiki.multi.sv.vec.txt'
    lang2_path = '/Users/maria/sprakresurser/muse/MUSE/data/wiki.multi.de.vec.txt'
    #nmax = 50000  # maximum number of word embeddings to load
    
    lang2_file_name= "/Users/maria/sprakresurser/parallellcorpus_kod/de_sv/ut.de"
    lang1_file_name = "/Users/maria/sprakresurser/parallellcorpus_kod/de_sv/ut.sv"
    
    lang1_stopword_name = 'swedish'
    lang2_stopword_name = 'german'
    
    lang1_identifier = "sv"
    lang2_identifier = "de"
    
    lang1_file = open(lang1_file_name)
    lang2_file = open(lang2_file_name)

    lang1_lines = lang1_file.readlines()
    lang2_lines = lang2_file.readlines()
    lang1_file.close()
    lang2_file.close()

    lang1_lines = [line.strip().split(" ") for line in lang1_lines]
    lang2_lines = [line.strip().split(" ") for line in lang2_lines]

    match_list = do_extract_vocabulary(lang1_lines, lang2_lines, lang1_stopword_name, lang2_stopword_name, lang1_path, lang2_path, lang1_identifier, lang2_identifier)
    
    for (lang1_word, lang2_word) in match_list:
        f.write(lang1_word + "\t" + lang2_word + "\n")

    f.close()
