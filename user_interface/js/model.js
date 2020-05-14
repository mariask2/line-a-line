"use strict";


// The URL to communicate with the restful api. Looking at the local server at the
// moment.

var SELECTDATASETTEXT = "------------ data set ------------";
var BASEURL = "/line-a-line/api/v1.0/";
var modelDataSetChoices = null;
var modelCurrentDataset = null;
var modelCurrentSorting = null;
var modelCurrentAction = null;
var modelCurrentFilterStr = "";
var modelCurrentDataPointNumber = -1;
var modelCurrentPreannotationLang1 = null;
var modelCurrentPreannotationLang2 = null;

var modelCurrentDragLang1Nr = null;
var modelCurrentDragNode1Alignments = null;

var modelCorpusname = null;
var modelCurrentPrealignmentMethod = null;
var modelLang1Name = null;
var modelLang2Name = null;
var modelPreviousDataPointNumber = -1;
var modelUndoClicked = false;
var modelReverseLang = false;

var modelNodesLang1 = null;
var modelNodesLang2 = null;


/////////
// General functionality used for communicating with server
///////

function get_data(url, success_function, dataToSend) {
    dataToSend["authentication_key"] = authenticationKey
    $.ajax({url:BASEURL + url, dataType: "json",
           data: dataToSend,
           type: "GET",
           success: function(json, status) {
           success_function(json["result"]);
           },
           error: function(xhr,status,error) {
           alert("Something went wrong with " + url + " " + error)
           }
           });
}

function save_data(url, success_function, dataToSend) {
    dataToSend["authentication_key"] = authenticationKey
    $.ajax({url:BASEURL + url, dataType: "json",
           data: dataToSend,
           type: "POST",
           success: function(json, status) {
           success_function(json["result"]);
           },
           error: function(xhr,status,error) {
           alert("Something went wrong with " + url + " " + error)
           }
           });
}


////
// Reseting model data
/////

// When a new dataset is selected, previously shown model selection data should reset (and therefore no analysis data)
function resetSortingChoiceData(){
    modelCurrentSorting = null;
    resetActionChoiceData();
}

// When no model is selected, no data related to analysis can be presented
function resetActionChoiceData(){
    modelCurrentAction = null;
    modelCurrentFilterStr = "";
}


function resetModelData(){
    modelDataSetChoices = null;
    
    modelResetPointData();

    modelCorpusname = null;
    modelLang1Name = null;
    modelLang2Name = null;


    
    resetSortingChoiceData();
    resetActionChoiceData();
}

function modelResetPointData(){
    modelCurrentPreannotationLang1 = null;
    modelCurrentPreannotationLang2 = null;
    modelCurrentDataPointNumber = -1;
    modelPreviousDataPointNumber = -1;
    modelCurrentDragLang1Nr = null;

    modelNodesLang1 = null;
    modelNodesLang2 = null;
}


///////
/// Fill datasets
////

function modelFillDataSetChoices(){
    modelDataSetChoices = [];
    get_data("list_available_corpora", modelDoFillDataSetChoices, {});
}

function modelDoFillDataSetChoices(choices){
    for (let i = 0; i < choices.length; i++) {
        var choice = choices[i]["corpusnamewithlanguage"];
        modelDataSetChoices.push({"value" : choice})
    }
    
    modelDataSetChoices.push({"value" : SELECTDATASETTEXT})
    
    controllerDoPopulateDataChoices(modelDataSetChoices);
 
}

function modelGetDataSetChoices(){
    if(modelDataSetChoices == null){
        modelFillDataSetChoices();
    }
    else{
    controllerDoPopulateDataChoices(modelDataSetChoices);
    }
}


////////////////////////////
// Load data for annotation
////////////////////////////


// Don't care about what the data point number is when in annotation mode, as next unannotated point will be selected
// "datapoint_number" : -1
function  modelLoadNextAlignment(){
    get_data("select_next_to_annotate", modelDoLoadNextAlignment,
	     {"selection_method" : modelCurrentSorting, "corpus" : modelCurrentDataset, 
	      "datapoint_number" : modelCurrentDataPointNumber, "alignment_method" :modelCurrentPrealignmentMethod, "filter_str": modelCurrentFilterStr});
    

    /*
    modelCurrentPreannotationLang1 = [{'term': 'Ihren', 'nr': 0, 'alignments': [0]}, {'term': 'privaten', 'nr': 1, 'alignments': [3]}, {'term': 'Dienstleistungsanbieter', 'nr': 2, 'alignments': [4, 8]}, {'term': 'wählen', 'nr': 3, 'alignments': [1]}, {'term': 'Sie', 'nr': 4, 'alignments': [0, 5]}, {'term': 'selbst', 'nr': 5, 'alignments': [1, 2, 3, 4]}, {'term': '.', 'nr': 6, 'alignments': [2, 9]}];

    modelCurrentPreannotationLang2 = [{'term': 'Du', 'nr': 0, 'alignments': [0, 4]}, {'term': 'väljer', 'nr': 1, 'alignments': [3, 5]}, {'term': 'själv', 'nr': 2, 'alignments': [6, 5]}, {'term': 'vilken', 'nr': 3, 'alignments': [1, 5]}, {'term': 'leverantör', 'nr': 4, 'alignments': [2, 5]}, {'term': 'du', 'nr': 5, 'alignments': [4]}, {'term': 'vill', 'nr': 6, 'alignments': []}, {'term': 'gå', 'nr': 7, 'alignments': []}, {'term': 'hos', 'nr': 8, 'alignments': [2]}, {'term': '.', 'nr': 9, 'alignments': [6]}];

     prepareToShowPreAnnotation();
     */

}

function modelLoadNextAnnotatedAlignment(){
    get_data("select_next_already_annotated", modelDoLoadNextAlignment, 
	     {"selection_method" : modelCurrentSorting, "corpus" : modelCurrentDataset, 
	      "datapoint_number" : modelCurrentDataPointNumber});
}

function modelLoadPreviousAnnotatedAlignment(){
      get_data("select_previous_already_annotated", modelDoLoadNextAlignment, 
	     {"selection_method" : modelCurrentSorting, "corpus" : modelCurrentDataset, 
	      "datapoint_number" : modelCurrentDataPointNumber});
}

function modelDoLoadNextAlignment(nextAlignment){
    let data_point_number = nextAlignment["data_point_number"];
  
    if (data_point_number == null){
	alert("No more data to load in this direction and with this selection criterium.");
	return;
    }

    // data_point contains a 2-tuple, the first with a list for the words in the first language, and the second with a list of the words in the second language
    let data_point = nextAlignment["data_point"];
    let dir_info = nextAlignment["dir_info"];

    modelCorpusname = dir_info["corpusname"];
    modelLang1Name = dir_info["lang1"];
    modelLang2Name = dir_info["lang2"];

    modelPreviousDataPointNumber = modelCurrentDataPointNumber;
    modelCurrentDataPointNumber = data_point_number;
    modelCurrentPreannotationLang1 = data_point[0];
    modelCurrentPreannotationLang2 = data_point[1];
    
    modelNodesLang1 = getNodesForLang(modelCurrentPreannotationLang2);
    modelNodesLang2 = getNodesForLang(modelCurrentPreannotationLang1);
    
    prepareToShowPreAnnotation();
}

function getNodesForLang(otherLangData){
    let nodesLang = [];
    let nodeCounter = 0;
    let alreadyConnectedInNode = [];
    
    for (let j = 0; j < otherLangData.length; j++){
        // If two or more of the tokens in this lang are connected to the same token in the other langue
        // these tokens should be connected to a node
          if(otherLangData[j].alignments.length > 1){

              // Check that none of the tokens in this language are already connected to a node
              let newNode = null;
              for(let i = 0; i < otherLangData[j].alignments.length; i++){
                  if(alreadyConnectedInNode.indexOf(otherLangData[j].alignments[i]) == -1){
                      newNode = true;
                  }
              }
    
              if(newNode){
                  nodesLang.push({"alignments": otherLangData[j].alignments, "nr": nodeCounter});
                  for(let i = 0; i < otherLangData[j].alignments.length; i++){
                      alreadyConnectedInNode.push(otherLangData[j].alignments[i])
                  }
                  nodeCounter = nodeCounter + 1;
              }
          }
      }
    return nodesLang;
}


function modelremoveLangLangLink(lang1Nr, lang2Nr){

    let leftAnnotations = null;
    let rightAnnotations = null;
    if(!modelReverseLang){
	leftAnnotations = modelCurrentPreannotationLang1;
	rightAnnotations = modelCurrentPreannotationLang2;
    }
    else{
	leftAnnotations = modelCurrentPreannotationLang2;
	rightAnnotations = modelCurrentPreannotationLang1;
    }

    let indexInLang1Array = leftAnnotations[lang1Nr].alignments.indexOf(lang2Nr);
    let indexInLang2Array = rightAnnotations[lang2Nr].alignments.indexOf(lang1Nr);
    
    leftAnnotations[lang1Nr].alignments.splice(indexInLang1Array, 1);
    rightAnnotations[lang2Nr].alignments.splice(indexInLang2Array, 1);

    modelNodesLang1 = getNodesForLang(modelCurrentPreannotationLang2);
    modelNodesLang2 = getNodesForLang(modelCurrentPreannotationLang1);
    
    prepareToShowPreAnnotation();
}

function modelAddLangLangLink(lang1Nr, lang2Nr){
    let leftAnnotations = null;
    let rightAnnotations = null;
    if(!modelReverseLang){
	leftAnnotations = modelCurrentPreannotationLang1;
	rightAnnotations = modelCurrentPreannotationLang2;
    }
    else{
	leftAnnotations = modelCurrentPreannotationLang2;
	rightAnnotations = modelCurrentPreannotationLang1;
    }

    for (let j = 0; j < leftAnnotations[lang1Nr].alignments.length; j++){
        if (leftAnnotations[lang1Nr].alignments[j] == lang2Nr){
            return; // connection exists
        }
    }
    
    for (let j = 0; j < rightAnnotations[lang2Nr].alignments.length; j++){
        if (rightAnnotations[lang2Nr].alignments[j] == lang1Nr){
            return; // connection exists
        }
    }
    
    leftAnnotations[lang1Nr].alignments.push(parseInt(lang2Nr));
    rightAnnotations[lang2Nr].alignments.push(parseInt(lang1Nr));

    modelNodesLang1 = getNodesForLang(modelCurrentPreannotationLang2);
    modelNodesLang2 = getNodesForLang(modelCurrentPreannotationLang1);
    
    prepareToShowPreAnnotation();

}


///////////
// Button clicks
//////////

function modelSaveDataLoadNext(){

    save_data("save_annotations", modelLoadNextAlignment, {"corpus": modelCorpusname, "lang1": modelLang1Name, "lang2": modelLang2Name,
              "current_data_point": modelCurrentDataPointNumber, "lang1_dict" : JSON.stringify(modelCurrentPreannotationLang1), "lang2_dict" : JSON.stringify(modelCurrentPreannotationLang2)});
    
}

function modelDeleteDataLoadNext(){
    save_data("delete_data_point", modelLoadNextAlignment, {"corpus": modelCorpusname, "lang1": modelLang1Name, "lang2": modelLang2Name,
              "current_data_point": modelCurrentDataPointNumber});
    
}

// for debugging
function empty(){
}


