from flask import Flask, jsonify, abort, make_response, request, json, request, current_app, render_template
import sys
import os
import traceback
import linecache
import logging
from datetime import timedelta
from functools import update_wrapper
from flask import send_from_directory
from names_and_constants import *
import hashlib


# An import that should function both locally and when running an a remote server
try:
    from environment_configuration import *
except:
    from topics2themes.environment_configuration import *


if RUN_LOCALLY:
    from flask_cors import CORS
    import select_pre_aligned_data
    import select_data_from_database
    from mongo_connector_align import MongoConnector
else:
    import topics2themes.make_topic_models as make_topic_models
    from topics2themes.theme_sorter import ThemeSorter
    from topics2themes.environment_configuration import *
    from topics2themes.topic_model_constants import *


app = Flask(__name__, template_folder="user_interface")

def get_hash(path):
    hash = hashlib.sha1()
    with open(path, "rb") as f:
        b = f.read1(65536)
        while len(b):
            hash.update(b)
            b = f.read1(65536)
    return hash.hexdigest()

@app.template_filter('staticfile')
def staticfile_hash(filename):
    h = get_hash("user_interface/js/" + filename)
    return "js/" + h + "/" + filename

@app.template_filter('staticfile_css')
def staticfile_css_hash(filename):
    h = get_hash("user_interface/css/" + filename)
    return "css/" + h + "/" + filename




if RUN_LOCALLY:
    CORS(app)
else:
    app.config['MONGO_CONNECT'] = False

try:
    mongo_con = MongoConnector()
except:
    e = sys.exc_info()
    print("The following error occurred: ")
    print(e)
    print("The pymongo database might not be running")
    mongo_con = MongoConnector()
    exit(1)

# To not have a lot of space in the output
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

def get_more_exception_info():
    trace_back = traceback.format_exc()
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    all_info = str(exc_obj) + str(trace_back)
    return 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), all_info)

def get_exception_info(e, extra_log_file = None):
    more = get_more_exception_info()
    logging.error("\nTOPICS2THEMES ERROR: " + str(e))
    logging.error("TOPICS2THEMES ERROR: " + more)
    print(e)
    print(more)
    resp = make_response(jsonify({'error' : str(e) + " " + more}), 400)
    resp.headers['Cache-Control'] = 'no-cache'
    return resp

def get_port():
    if len(sys.argv) < 2:
        sys.exit("As an argument to the script, you need to give the port at which you are listening,"\
                 + " for instance 5000")
    current_port = int(sys.argv[1])
    print("Will start up server to listen at port " + str(current_port))
    return current_port


def load_keys(approved_keys, key_file_name):
    try:
        f = open(os.path.join(WORKSPACE_FOLDER, key_file_name))
        lines = f.readlines()
        f.close()
        
        if len(lines) == 0 or (len(lines) == 1 and lines[0].strip() == ""):
            print("\nYour file '" + key_file_name + " in your WORKSPACE_FOLDER, i.e. in " + WORKSPACE_FOLDER + "\nis empty. This file should contain user keys (that you choose), one line for each approved key. When the user then uses the web interface, the user will be prompted to provide a key file, and the user needs to give a key that it contained in your " + key_file_name + " to be allowed to use the tool.\n")
            raise LookupError()
        
        for line in lines:
            approved_keys.append(line.strip())

    except FileNotFoundError as e:
        print("\nYou need to create a file called '" + key_file_name + " in your WORKSPACE_FOLDER, i.e. in " + WORKSPACE_FOLDER + "\nThis file should contain user keys (that you choose), one line for each approved key. When the user then uses the web interface, the user will be prompted to provide a key file, and the user needs to give a key that it contained in your " + key_file_name + " to be allowed to use the tool.\n")
        raise(e)

def authenticate():
    key = request.values.get("authentication_key")
    print("key", key)
    print("APPROVED_KEYS", APPROVED_KEYS)
    if key not in APPROVED_KEYS:
        abort(403)


# Uses the following methods:
# select_unannotated_from_database(mc, corpus_name, select_difficult, do_active_selection, filter_str, alignment_method)
# When a filter_str is given and selection method is SearchContent, no active selection is carried out
@app.route(API_NAME + 'select_next_to_annotate', methods=['GET', 'POST'])
def select_next_to_annotate():
    try:
        authenticate()
        corpus = request.values.get("corpus")
        selection_method = request.values.get("selection_method")
        datapoint_number = int(request.values.get("datapoint_number"))
        alignment_method = request.values.get("alignment_method")
        filter_str = request.values.get("filter_str")
        
        
        # TODO: Add a choice for alignment_method to some kind of constant-file
        data_point = select_data_from_database.select_unannotated_from_database(mongo_con,
            corpus,
            select_difficult = (selection_method == 'Difficult'),
            do_active_selection = (selection_method != 'NotActive' and selection_method != 'SearchContent'),
            filter_str = filter_str,
            alignment_method = alignment_method)
                                         
        resp = make_response(jsonify({"result" : data_point}))
        resp.headers['Cache-Control'] = 'no-cache'
        return resp
    except Exception as e:
        return get_exception_info(e)

@app.route(API_NAME + 'select_next_already_annotated', methods=['GET', 'POST'])
def select_next_already_annotated():
    try:
        authenticate()
        corpus = request.values.get("corpus")
        selection_method = request.values.get("selection_method")
        datapoint_number = int(request.values.get("datapoint_number"))
        
        data_point = select_data_from_database.select_annotated_from_database(mongo_con, corpus,
                                                                                datapoint_number,
                                                                                selection_method == 'Difficult',
                                                                                selection_method != 'NotActive',
                                                                                reverse = False)
        resp = make_response(jsonify({"result" : data_point}))
        resp.headers['Cache-Control'] = 'no-cache'
        return resp
    except Exception as e:
        return get_exception_info(e)



@app.route(API_NAME + 'select_previous_already_annotated', methods=['GET', 'POST'])
def select_previous_already_annotated():
    try:
        authenticate()
        corpus = request.values.get("corpus")
        selection_method = request.values.get("selection_method")
        datapoint_number = int(request.values.get("datapoint_number"))
        
        data_point = select_data_from_database.select_annotated_from_database(mongo_con, corpus,
                                                                              datapoint_number,
                                                                              selection_method == 'Difficult',
                                                                              selection_method != 'NotActive',
                                                                              reverse = True)
        resp = make_response(jsonify({"result" : data_point}))
        resp.headers['Cache-Control'] = 'no-cache'
        return resp
    except Exception as e:
        return get_exception_info(e)


@app.route(API_NAME + 'list_available_corpora', methods=['GET', 'POST'])
def list_available_corpora():
    try:
        authenticate()
        #data_point = select_pre_aligned_data.list_available_corpora()
        data_point = select_data_from_database.list_available_corpora_from_database(mongo_con)
        resp = make_response(jsonify({"result" : data_point}))
        resp.headers['Cache-Control'] = 'no-cache'
        return resp
    except Exception as e:
        return get_exception_info(e)

@app.route(API_NAME + 'save_annotations', methods=['GET', 'POST'])
def save_annotations():
    try:
        authenticate()
        corpus = request.values.get("corpus")
        lang1 = request.values.get("lang1")
        lang2 = request.values.get("lang2")
        current_data_point = int(request.values.get("current_data_point"))
        lang1_dict = request.values.get("lang1_dict")
        lang2_dict = request.values.get("lang2_dict")
        print("lang1_dict", lang1_dict)
        print("lang2_dict", lang2_dict)
        
        lang1_dict = json.loads(lang1_dict)
        lang2_dict = json.loads(lang2_dict)
        
        #save_result = select_pre_aligned_data.save_annotations(corpus, lang1, lang2, current_data_point, (lang1_dict, lang2_dict))
        save_result = select_data_from_database.save_annotations(mongo_con, corpus, current_data_point, (lang1_dict, lang2_dict))
        resp = make_response(jsonify({"result" : save_result}))
        resp.headers['Cache-Control'] = 'no-cache'
        return resp
    
    except Exception as e:
        return get_exception_info(e)

@app.route(API_NAME + 'delete_data_point', methods=['GET', 'POST'])
def delete_data_point():
    try:
        authenticate()
        corpus = request.values.get("corpus")
        current_data_point = int(request.values.get("current_data_point"))
        
        delete_result = select_data_from_database.delete_data_point(mongo_con, corpus, current_data_point)
        
        resp = make_response(jsonify({"result" : delete_result}))
        resp.headers['Cache-Control'] = 'no-cache'
        return resp
    
    except Exception as e:
        return get_exception_info(e)



@app.route('/line-a-line/')
def start_page():
    return render_template("index.html")

@app.route('/line-a-line/js/<filename>')
def js_files(filename):
    return send_from_directory("user_interface/js", filename)
    
@app.route('/line-a-line/js/<hash>/<filename>')
def js_files_hash(filename, hash):
    return send_from_directory("user_interface/js", filename)
    

@app.route('/line-a-line/css/<filename>')
def css_files(filename):
    return send_from_directory("user_interface/css", filename)

@app.route('/line-a-line/css/<hash>/<filename>')
def css_files_hash(filename, hash):
    return send_from_directory("user_interface/css", filename)
    
@app.route('/line-a-line/fonts/<filename>')
def fonts_files(filename):
    return send_from_directory("user_interface/fonts", filename)



APPROVED_KEYS = []
FILE = open("log_file.txt", "w")
load_keys(APPROVED_KEYS, KEY_FILE_NAME)

if __name__ == '__main__':
    logging_level_to_use = None
    try:
        if LOGGING_LEVEL not in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]:
            logging_level_to_use = logging.DEBUG
            print("Using default logging level " + str(logging.DEBUG))
        else:
            logging_level_to_use = LOGGING_LEVEL
    except:
        logging_level_to_use = logging.DEBUG
        print("Using default logging level " + str(logging.DEBUG))

    logging.basicConfig(filename=os.path.join(WORKSPACE_FOLDER, 'align_log.log'),level=logging_level_to_use)
    logging.info("******** Starting align server ***************")
    current_port = get_port()
    logging.info("******* Listning to port " + str(current_port) + " ***************")

    if RUN_LOCALLY:
        print("You have specified in 'environment_configuration.py' to run on your local computer. That means you can access the application from your browser at:")
        print(LOCAL_PORT + str(current_port) + "/line-a-line/")
    applogger = app.logger
    applogger.setLevel(logging_level_to_use)
    app.run(port=current_port)

