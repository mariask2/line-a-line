import os

LOCAL_PORT = "http://127.0.0.1:"
API_NAME = "/line-a-line/api/v1.0/"
KEY_FILE_NAME = "approved_keys.txt"

OUTDIRBASE = "outputdir"
ALIGNED_FILENAME = "intersected_expanded.aligned"
META_DATA_FILE_NAME = "meta_data.txt"
TRAINING_DATA_FILE_NAME = "data_for_training_aligner."
ALIGNED_FILE_NAME = TRAINING_DATA_FILE_NAME + "aligned"
DATA_TO_ALIGN_FILE_NAME = "data_to_align."
DELETED_NAME = "deleted.csv"

# To be able to compare results when lexicon is used and not, also produce training files without lexicon
TRAINING_DATA_FILE_NAME_NO_LEXICON = "data_for_training_aligner_no_lexicon."

DATADIR = "data"
DATADIRFASTTEXTFORMAT = "datafasttextformat"

LANG1 = "LANG1"
LANG2 = "LANG2"
ALIGNMENTS = "ALIGNMENTS"
ALIGNMENTSZERODICTLANG1 = "ALIGNMENTSZERODICTLANG1"
ALIGNMENTSZERODICTLANG2 = "ALIGNMENTSZERODICTLANG2"
SENTENCENR = "SENTENCENR"
ALIGNMENTTUPLES = "ALIGNMENTTUPLES"


def get_dir_for_fasttext_format_data(name, lang_1, lang_2):
    return os.path.join(DATADIRFASTTEXTFORMAT, name + "_" + lang_1 + "_" + lang_2)

# For the directory with the data
def get_dir_for_data(name, lang_1, lang_2):
    return os.path.join(DATADIR, name + "_" + lang_1 + "_" + lang_2)

def get_training_data_file_name(name, lang_1, lang_2, lang):
    return os.path.join(get_dir_for_data(name, lang_1, lang_2), TRAINING_DATA_FILE_NAME + lang)

def get_training_data_file_name_no_lexicon(name, lang_1, lang_2, lang):
    return os.path.join(get_dir_for_data(name, lang_1, lang_2), TRAINING_DATA_FILE_NAME_NO_LEXICON + lang)

def get_aligned_file(name, lang_1, lang_2):
    return os.path.join(get_dir_for_data(name, lang_1, lang_2), ALIGNED_FILE_NAME)

def get_data_to_align_file_name(name, lang_1, lang_2, lang):
    return os.path.join(get_dir_for_data(name, lang_1, lang_2), DATA_TO_ALIGN_FILE_NAME + lang)

def get_deleted_file(name, lang_1, lang_2):
    file_name = os.path.join(get_dir_for_data(name, lang_1, lang_2), DELETED_NAME)
    
    if not os.path.isfile(file_name):
        f = open(file_name, "w")
        f.close()
    return file_name

# For the alignment output produced by the aligner
def get_aligned_output_dir(name, lang_1, lang_2):
    return os.path.join(OUTDIRBASE, name + "_" + lang_1 + "_" + lang_2)

def get_aligned_output_dir_version(name, lang_1, lang_2, version_name):
    return os.path.join(get_aligned_output_dir(name, lang_1, lang_2), version_name)

#os.path.join(OUTDIRBASE, config['sourceLanguage'] + "_" + config['targetLanguage'])
