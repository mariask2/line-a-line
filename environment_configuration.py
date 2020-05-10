import logging

WORKSPACE_FOLDER = "."
#Here, give a path to the folder where you have the directory 'data_folder', which contains your data
#For instance:
#WORKSPACE_FOLDER = "/Users/maria/mariaskeppstedtdsv/potsdam/visulizationideas/topic_modelling"
# (If this is not given, an error will be thrown)

# Whether Topics2Themes is run locally or on a remote server
# (If this is not given, an error will be thrown)
RUN_LOCALLY = True

# The logging level
# Can be any of logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL
# If it's not given, logging.DEBUG will be used
LOGGING_LEVEL = logging.DEBUG





