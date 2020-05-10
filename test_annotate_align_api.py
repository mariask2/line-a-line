import urllib.request
import urllib.parse
import urllib
import json
import sys
import traceback
import linecache
from urllib.error import HTTPError
from names_and_constants import *


def get_exception_info():
    trace_back = traceback.format_exc()
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    all_info = str(exc_obj) + str(trace_back)
    return 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), all_info)

APPROVED_KEYS = []
f = open(KEY_FILE_NAME)
for line in f:
    APPROVED_KEYS.append(line.strip())


def test_list_available_corpora(urlbase, method):
    params_text = urllib.parse.urlencode({"authentication_key": APPROVED_KEYS[0]})
    try:
        url = urlbase + method + "?%s" % params_text
        with urllib.request.urlopen(url) as f:
            c = f.read().decode('utf-8')
            return c
    except HTTPError as e:
        print(str(e) + " " + get_exception_info())
        print(e.__class__)
        return "Could not select available corpora"


def test_select_next_to_annotate(urlbase, method, selection_method):
    params_text = urllib.parse.urlencode({"authentication_key": APPROVED_KEYS[0], "corpus": "labour_market_social_security_de_sv",\
                                         "selection_method": selection_method, "datapoint_number" : 40, "order_for_selected_in_current_ordering" : 5})
    try:
        url = urlbase + method + "?%s" % params_text
        with urllib.request.urlopen(url) as f:
            c = f.read().decode('utf-8')
            return c
    except HTTPError as e:
        print(str(e) + " " + get_exception_info())
        print(e.__class__)
        return "Could not select next data point to annotate"

def test_select_next_already_annotated(urlbase, method, selection_method):
    params_text = urllib.parse.urlencode({"authentication_key": APPROVED_KEYS[0], "corpus": "labour_market_social_security_de_sv",\
                                         "selection_method": selection_method, "datapoint_number" : 399, "order_for_selected_in_current_ordering" : 5})
    try:
        url = urlbase + method + "?%s" % params_text
        with urllib.request.urlopen(url) as f:
            c = f.read().decode('utf-8')
            return c
    except HTTPError as e:
        print(str(e) + " " + get_exception_info())
        print(e.__class__)
        return "Could not select next data point to annotate"

def test_save_annotations(urlbase, method):
    lang1_dict  = [{"alignments":[0],"nr":0,"term":"Ihren"},{"alignments":[3],"nr":1,"term":"privaten"},{"alignments":[4,8],"nr":2,"term":"Dienstleistungsanbieter"},{"alignments":[1,1],"nr":3,"term":"wählen"},{"alignments":[0,5],"nr":4,"term":"Sie"},{"alignments":[1,2,3,4],"nr":5,"term":"selbst"},{"alignments":[2,9],"nr":6,"term":"."}]
    lang2_dict = [{"alignments":[0,4],"nr":0,"term":"Du"},{"alignments":[3,5,3],"nr":1,"term":"väljer"},{"alignments":[6,5],"nr":2,"term":"själv"},{"alignments":[1,5],"nr":3,"term":"vilken"},{"alignments":[2,5],"nr":4,"term":"leverantör"},{"alignments":[4],"nr":5,"term":"du"},{"alignments":[],"nr":6,"term":"vill"},{"alignments":[],"nr":7,"term":"gå"},{"alignments":[2],"nr":8,"term":"hos"},{"alignments":[6],"nr":9,"term":"."}]
    
    params_text = urllib.parse.urlencode({"authentication_key": APPROVED_KEYS[0],
                                         "corpus_without_language": "labour_market_social_security_de_sv", "lang1": "de", "lang2": "sv",
                                         "current_data_point": "400", "lang1_dict" : json.dumps(lang1_dict), "lang2_dict" : json.dumps(lang2_dict)})

    try:
        url = urlbase + method + "?%s" % params_text
        with urllib.request.urlopen(url) as f:
            c = f.read().decode('utf-8')
            return c
    except HTTPError as e:
        print(str(e) + " " + get_exception_info())
        print(e.__class__)
        return "Could not save annotation"

def test_delete_data_point(urlbase, method):
    params_text = urllib.parse.urlencode({"authentication_key": APPROVED_KEYS[0],
                                         "corpus_without_language": "labour_marked_social_security", "lang1": "de", "lang2": "sv",
                                         "current_data_point": "4"})
    try:
        url = urlbase + method + "?%s" % params_text
        with urllib.request.urlopen(url) as f:
            c = f.read().decode('utf-8')
            return c
    except HTTPError as e:
        print(str(e) + " " + get_exception_info())
        print(e.__class__)
        return "Could not delete data point"



if __name__ == '__main__':
    
    if len(sys.argv) < 2:
        sys.exit("As an argument to the script, you need to give the port at which you are listening,"\
                 + " for instance 5000")
    port = sys.argv[1]
    
    urlbase = LOCAL_PORT + port + API_NAME

    print("\ntest_list_available_corpora")
    print("-----------------\n")
    print(test_list_available_corpora(urlbase, "list_available_corpora"))


    print("\ntest_select_next_to_annotate")
    print("-----------------\n")
    print(test_select_next_to_annotate(urlbase, "select_next_to_annotate", "Difficult"))
    print(test_select_next_to_annotate(urlbase, "select_next_to_annotate", "Easy"))
    print(test_select_next_to_annotate(urlbase, "select_next_to_annotate", "NotActive"))


    print(test_select_next_already_annotated(urlbase, "select_next_already_annotated", "NotActive"))

    print("test_delete data point")
    print("-----------------\n")
    print(test_delete_data_point(urlbase, "delete_data_point"))


    print("save")
    print("-----------------\n")
    print(test_save_annotations(urlbase, "save_annotations"))





