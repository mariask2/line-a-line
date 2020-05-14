"use strict";

// Offset size used for the container panel headings
var TOP_OFFSET = 45;

// Just for consistency in the code. All links equal here
var LINK_WIDTHS = [0.5, 0.5];

// Current window size (used to ignore redundant resize events)
var windowWidth;
var windowHeight;


var DIRECTHIGHLIGHT = "direct-highlight";

var HIGHLIGHT = "highlight";

var NOTCHOSEN = "not-chosen";

var SELECTDATASETTEXT = "Select data set";
var SELECTMODELTEXT = "Select model";
var SELECTANALYSISTEXT = "Select analysis";

var authenticationKey = null;

var ANNOTATE = "annotate";
var BROWSEANNOTATED = "browse-annotated";
var SEARCHCONTENT = "SearchContent"

//var searchWriteMode = false;
var showLeftNodes = false;
var showRightNodes = false;


/////////////////////
// Script entry point
//////////////////////

$(document).ready(function(){
                  
    getAuthenticationKey();
                  
    disableButtons();
   
	
    windowWidth = $(window).width();
	windowHeight = $(window).height();
	
	resizeContainers();
	
    ////////////////////////
	// Set up the handlers
    /////////////////////////
    
    // Handlers for selecting and/or constructing data sets, models and analysis 
    $("#dataset").change(onDatasetChange);
    $("#sortingChoice").change(onSortingChoiceChange);
    $("#prealignmentChoice").change(onPrealignmentChoiceChange);
    $("#actionChoice").change(onActionChoiceChange);
    $("#textinput").keydown(onTextInputChange);
                  
    $("#lang1List, #lang2List").scroll(onListScroll);	
    $("#lang2List").on("click", ".term-element .lang-lang-remove-button", onAlignRemove);
	     
    $("#save").click(onSave);
    $("#delete").click(onDelete);
    $("#stepBackward").click(onStepBack);
    $("#changeOrder").click(onChangeOrder);
                  
    $("#nodes1").click(onClickLeft);
    $("#nodes2").click(onClickRight);
                  
    // Drag'n'drop handlers
    $("#lang1List")
        .on("dragstart", ".term-element", onLangElementDragStart)
        .on("dragend", ".term-element", onLangElementDragEnd);
                
    $("#lang2List")
        .on("dragenter", ".term-element", onLangElementDragEnterOver)
        .on("dragover", ".term-element", onLangElementDragEnterOver)
        .on("dragleave", ".term-element", onLangElementDragLeave)
        .on("drop", ".term-element", onLangElementDrop);

    // Drag'n'drop handlers
    $("#nodes1List")
        .on("dragstart", ".term-element", onNodeElementDragStart)
        .on("dragend", ".term-element", onNodeElementDragEnd);

    
    $("#nodes2List")
        .on("dragenter", ".term-element", onLangElementDragEnterOver)
        .on("dragover", ".term-element", onLangElementDragEnterOver)
        .on("dragleave", ".term-element", onLangElementDragLeave)
        .on("drop", ".term-element", onNodeElementDrop);
    
    
	// Highlight handlers
    $("#lang1List")
		.on("mouseenter", ".term-element", onLang1ElementMouseEnter)
        .on("mouseleave", ".term-element", onLang1ElementMouseLeave);
	$("#lang2List")
		.on("mouseenter", ".term-element", onLang2ElementMouseEnter)
		.on("mouseleave", ".term-element", onLang2ElementMouseLeave);
	
    $("#nodes1List")
        .on("mouseenter", ".term-element", nodes1ListElementMouseEnter)
        .on("mouseleave", ".term-element", nodes1ListElementMouseLeave);
    $("#nodes2List")
        .on("mouseenter", ".term-element", nodes2ListElementMouseEnter)
        .on("mouseleave", ".term-element", nodes2ListElementMouseLeave);
                  
    resetInterface();
    resetModelData();
                  
    populateDataChoices();
                  
});


function prepareToShowPreAnnotation(){
    enableWhenLoadingAnnotation();
    showPreannotation();
    
    if (modelCurrentAction == BROWSEANNOTATED){
         disablePrealignmentChoices();
     }
}

function showNodes(nodesList, isShown, nodeData, draggable){
    d3.select(nodesList).selectAll("li").remove();
    if(isShown){
        d3.select(nodesList).selectAll("li")
        .data(nodeData)
        .enter()
        .append("li")
	.attr("draggable", draggable)
        .classed("list-group-item", true)
    
        .each(function(d, i){
              let element = $(this);
              element.addClass("term-element");
              let titleLabel = $("<span></span>");
              titleLabel.addClass("title-label");
              titleLabel.append(d.nr);
              element.append(titleLabel);
   
    });
    }
}

function showPreannotation(){
    $("#lang1List").empty();
    $("#lang2List").empty();
    $("#nodes1List").empty();
    $("#nodes2List").empty();
    
    resetLinks();

    var leftData = null;
    var rightData = null;
    var leftNodes = null;
    var rightNodes = null;
    
    if (!modelReverseLang){
	leftData = modelCurrentPreannotationLang1;
	rightData = modelCurrentPreannotationLang2;
    leftNodes = modelNodesLang1;
    rightNodes = modelNodesLang2;
    }
    else{
	leftData = modelCurrentPreannotationLang2;
	rightData = modelCurrentPreannotationLang1;
    leftNodes = modelNodesLang2;
    rightNodes = modelNodesLang1;
    }
    
    if (!modelReverseLang){
	$("#langtitle1").text("Language: " + modelLang1Name)
	$("#langtitle2").text("Language: " + modelLang2Name)
    }
    else{
	$("#langtitle1").text("Language: " + modelLang2Name)
	$("#langtitle2").text("Language: " + modelLang1Name)
    }
    // Append the terms lang1
	d3.select("#lang1List").selectAll("li")
	.data(leftData)
	.enter()
	.append("li")
	.classed("list-group-item", true)
	.attr("draggable", true)
	.each(function(d, i){
		let element = $(this);
		element.addClass("term-element");
		element.attr("title", "Term: " + d.term);
		let titleLabel = $("<span></span>");
		titleLabel.addClass("title-label");
		titleLabel.append(d.term);
          
		element.append(titleLabel);
	});
      // Append the terms lang2
	d3.select("#lang2List").selectAll("li")
	.data(rightData)
	.enter()
	.append("li")
	.classed("list-group-item", true)
    
	.each(function(d, i){
	    let element = $(this);
	    element.addClass("term-element");
	    element.attr("title", "Term: " + d.term);
	    let titleLabel = $("<span></span>");
	    titleLabel.addClass("title-label");
	    titleLabel.append(d.term);
	    element.append(titleLabel);
	    
	    let lang1Container = $("<span></span>");
	    lang1Container.addClass("lang-link-container");
	    lang1Container.addClass("pull-right")
	    populateLang1Container(d, lang1Container);
	    element.append(lang1Container)
	});
    

    showNodes("#nodes1List", showLeftNodes, leftNodes, true);
    showNodes("#nodes2List", showRightNodes, rightNodes, false);

    renderLinks();
    
    enableSaveButton();
    enableChangeOrderButton();
    
    disableDeleteButton();
    if (modelCurrentAction == ANNOTATE){
	 enableDeleteButton();
    }

    disableStepBack(); // Should only be allowed to step back on step
    if(modelPreviousDataPointNumber != -1 && !modelUndoClicked){
	enableStepBack();
    }
    
    enableActionChoices();
    //searchWriteMode = false; // When the pre-annotation is loaded, the save button should again function as a save button,
    // not as a load-next-button 
}


function getAuthenticationKey(){
    authenticationKey = "m"
    return
    // TODO: Do this correctly
    // TODO: Use localStorage.setItem to save item
    let key = prompt("Please enter authentication key");
   
    if (key != null && key.trim() != ""){
        authenticationKey = key
    }
    else{
        alert("Authentication key needed");
        getAuthenticationKey();
    }
}



///////
// Resize
///////

// Handles window resize
$(window).resize(function() {
    if(this.resizeTO) clearTimeout(this.resizeTO);
    this.resizeTO = setTimeout(function() {
        $(this).trigger("resizeEnd");
    }, 500);
});

$(window).bind("resizeEnd", function(){
	// Check if the resize really occurred
	var newWidth = $(window).width();
	var newHeight = $(window).height();
	
	if (newWidth != windowWidth
		|| newHeight != windowHeight) {
		windowWidth = newWidth;
		windowHeight = newHeight;
	} else {
		// Abort the handler
		return;
	}
		
	// Update the element sizes
	resizeContainers();
	
	// Update the links
	renderLinks();
});

// Resizes the containers based on the current window size
function resizeContainers() {
	var otherHeight = 0;
	$(".outer-element").each(function(){
		otherHeight += $(this).outerHeight(true);
	})
		
	// Several magic numbers below to account for heights of headers, spaces, etc.
	var maxAvailableHeight = windowHeight - otherHeight
		- parseInt($("body > div.container-fluid").css("margin-top")) - parseInt($("body > div.container-fluid").css("border-top-width"));
	var mainAvailableHeight = maxAvailableHeight - $("#mainPanelLower").outerHeight();
	
	// Adjust the sizes of the inner containers
	var innerAvailableHeight = mainAvailableHeight - TOP_OFFSET;
	$("#termsList, #topicsList, #themesList, #textsList").css("max-height", innerAvailableHeight + "px");
    
}



///////////////
/// For the panel above with datasets, models and analyses versions
///////////////

// Data set changes
//////

function populateDataChoices(){
    modelGetDataSetChoices();
}

function controllerDoPopulateDataChoices(choices){
    $("#dataset").empty();
    
    // Append the terms
    d3.select("#dataset").selectAll("option")
    .data(choices)
    .enter()
    .append("option")
    .each(function(d, i){
          let element = $(this);
          if (d.value == SELECTDATASETTEXT){
          element.attr("selected", true);
          element.attr("disabled", true);
          }
          element.attr("value", d.value);
          element.attr("title", d.value);
          element.append(d.value);
          });
    
}


function onDatasetChange() {
    var newDataset = $("#dataset").val();
    
    if (newDataset == modelCurrentDataset){
        return;
    }
    modelCurrentDataset = newDataset;
    
    
    modelCurrentPrealignmentMethod =  $("#prealignmentChoice").val();
    
    resetInterface();
    enableActionChoices();
}

function addAnnotateSortingOptions(){
    $('#sortingChoice')
        .find('option')
        .remove()
        .end()
        .append('<option value="">---------- sorting ----------</option>')
        .val('')
    ;

    $('#sortingChoice')
           .find('option')
           .end()
           .append('<option value="Difficult">show most difficult first</option>')
       ;
    
    $('#sortingChoice')
           .find('option')
           .end()
           .append('<option value="Easy">show easiest first</option>')
       ;
    $('#sortingChoice')
        .find('option')
        .end()
        .append('<option value="NotActive">order in corpus</option>')
    ;
    $('#sortingChoice')
             .find('option')
             .end()
             .append('<option value="SearchContent">search content</option>')
         ;
    
}

function addBrowseSortingOptions(){
    $('#sortingChoice')
        .find('option')
        .remove()
        .end()
        .append('<option value="">---------- sorting ----------</option>')
        .val('')
    ;
    
    $('#sortingChoice')
        .find('option')
        .end()
        .append('<option value="NotActive">order in corpus</option>')
    ;
}

function onActionChoiceChange(){
    modelResetPointData();
    let newAction = $("#actionChoice").val();
    if (newAction == modelCurrentAction || newAction == ""){
        return;
    }
    
    resetInterface();
    enableActionChoices();
    modelCurrentAction = newAction;
    
    if (modelCurrentAction == ANNOTATE){
        addAnnotateSortingOptions();
    }
    if (modelCurrentAction == BROWSEANNOTATED){
        addBrowseSortingOptions();
    }
    
    enableSortingChoices();
    disablePrealignmentChoices();
    

    /*
    var select = document.getElementById("sortingChoice");
    var option = document.createElement("option");
    option.text = "Text";
    option.value = "myvalue";
    select.appendChild(option);
    */
     
     
    /*
    if (modelCurrentAction == BROWSEANNOTATED){
	resetInterface();
        modelLoadNextAnnotatedAlignment();
	$("#saveGlyphicon").removeClass("glyphicon-save");
	$("#saveGlyphicon").addClass("glyphicon-step-forward");

	$("#backGlyphicon").removeClass("glyphicon-arrow-left");
	$("#backGlyphicon").addClass("glyphicon-step-backward");
	
    }
    else{
	enableSortingChoices();
	//enablePrealignmentChoices();
    }
     */
}


function onPrealignmentChoiceChange(){
    modelCurrentPrealignmentMethod =  $("#prealignmentChoice").val();
    
    setButtonsInAnnotationModeAndLoadNextAlignment();
    //enableSortingChoices();
}

function setButtonsInAnnotationModeAndLoadNextAlignment(){
    $("#saveGlyphicon").addClass("glyphicon-save");
    $("#saveGlyphicon").removeClass("glyphicon-step-forward");

    $("#backGlyphicon").addClass("glyphicon-arrow-left");
    $("#backGlyphicon").removeClass("glyphicon-step-backward");

    modelLoadNextAlignment();
}

function onSortingChoiceChange(){
    if ($("#sortingChoice").val() == ""){
            return;
    }
    
    modelCurrentSorting = $("#sortingChoice").val();
   
    // resetInterface();
    if (modelCurrentAction == ANNOTATE && modelCurrentSorting != SEARCHCONTENT){
        //searchWriteMode = false;

        // Reset data for text filtering
        modelCurrentFilterStr = "";
        $("#textinput").val("");
        disableSearchInput();
	
        setButtonsInAnnotationModeAndLoadNextAlignment();
    }

    if (modelCurrentAction == ANNOTATE && modelCurrentSorting == SEARCHCONTENT){
        //searchWriteMode = true; // If search content is selected, you need to write a string to search, before you can search
        enableSearchInput();
        disableButtons();
        disablePrealignmentChoices();
        $("#textinput").focus();

	//$("#saveGlyphicon").addClass("glyphicon-step-forward");
	//$("#saveGlyphicon").removeClass("glyphicon-save");
    }
    
    if (modelCurrentAction == BROWSEANNOTATED){
        disablePrealignmentChoices();
        modelLoadNextAnnotatedAlignment();
        $("#saveGlyphicon").removeClass("glyphicon-save");
        $("#saveGlyphicon").addClass("glyphicon-step-forward");

        $("#backGlyphicon").removeClass("glyphicon-arrow-left");
        $("#backGlyphicon").addClass("glyphicon-step-backward");
    }
    
}

function onTextInputChange(event){
    if(event.keyCode == 13){
        event.preventDefault();
        event.stopPropagation();
        modelCurrentFilterStr = $("#textinput").val().replace("\n", "");
        setButtonsInAnnotationModeAndLoadNextAlignment();

    }
    /*
    enableSaveButton();
    $("#saveGlyphicon").addClass("glyphicon-step-forward");
    $("#saveGlyphicon").removeClass("glyphicon-save")
     */
}




///////////
// Add data to interface
/////////

// Initializes/resets the interface
function resetInterface() {
    $("#lang1List").empty();
    $("#lang2List").empty();
    resetLinks();
    
    disableSortingChoices();
    disableActionChoices();
    disablePrealignmentChoices();
    disableSearchInput();
    enableDatasetChoices();

    //searchWriteMode = false;
    $("#textinput").val("");
}

function disableDatasetChoices(){
    $("#dataset").addClass("disabled");
    $("#dataset").attr("disabled", true);
}

   
function enableDatasetChoices(){
    $("#dataset").removeClass("disabled");
    $("#dataset").attr("disabled", false);
}

function disableSortingChoices(){
    $("#sortingChoice").addClass("disabled");
    $("#sortingChoice").attr("disabled", true);
}

function enableSortingChoices(){
    $("#sortingChoice").removeClass("disabled");
    $("#sortingChoice").attr("disabled", false);
}

function disableActionChoices(){
    $("#actionChoice").addClass("disabled");
    $("#actionChoice").attr("disabled", true);
}

function enableActionChoices(){
    $("#actionChoice").removeClass("disabled");
    $("#actionChoice").attr("disabled", false);
}

function enablePrealignmentChoices(){
    $("#prealignmentChoice").removeClass("disabled");
    $("#prealignmentChoice").attr("disabled", false);
}

function disablePrealignmentChoices(){
    $("#prealignmentChoice").addClass("disabled");
    $("#prealignmentChoice").attr("disabled", true);
}


function  disableSearchInput(){
    $("#textinput").addClass("disabled");
    $("#textinput").addClass("searchtextinput_disabled");
    $("#textinput").attr("disabled", true);
}

function  enableSearchInput(){
    $("#textinput").addClass("enabled");
    $("#textinput").removeClass("searchtextinput_disabled");
    $("#textinput").attr("disabled", false);
}

function disableButtons(){
    $("#changeOrder").addClass("disabled");
    $("#changeOrder").attr("disabled", true);

    $("#save").addClass("disabled");
    $("#save").attr("disabled", true);

    disableStepBack();
    disableDeleteButton();
}

function enableSaveButton(){
    $("#save").removeClass("disabled");
    $("#save").attr("disabled", false);
}

function enableChangeOrderButton(){
    $("#changeOrder").removeClass("disabled");
    $("#changeOrder").attr("disabled", false);
}

function enableDeleteButton(){
    $("#delete").removeClass("disabled");
    $("#delete").attr("disabled", false);
}

function disableDeleteButton(){
    $("#delete").addClass("disabled");
    $("#delete").attr("disabled", false);
}

function disableStepBack(){
    $("#stepBackward").addClass("disabled");
    $("#stepBackward").attr("disabled", true);
}

function enableStepBack(){
    $("#stepBackward").removeClass("disabled");
    $("#stepBackward").attr("disabled", false);
}

function disableAfterStartingAnnotate(){
    disablePrealignmentChoices();
    disableSortingChoices();
    disableSearchInput();
    disableStepBack()
        
}

function enableWhenLoadingAnnotation(){
    enablePrealignmentChoices();
    enableSortingChoices();
    enableStepBack();
    
    
    if (modelCurrentAction == ANNOTATE && modelCurrentSorting == SEARCHCONTENT){
        enableSearchInput();
    }
    
    /*
    if (searchWriteMode) { // If search content is selected, you should be allowed to search, before you can search
        enableSearchInput();
    }
     */
        
}

// Populates the remove buttons for links
function populateLang1Container(lang2Term, lang1Container) {
    var leftPreannotations = null;
    if(!modelReverseLang){
	leftPreannotations = modelCurrentPreannotationLang1;
    }
    else{
	leftPreannotations = modelCurrentPreannotationLang2;
    }

    for (let j = 0; j < leftPreannotations.length; j++){
	if (leftPreannotations[j].alignments.indexOf(lang2Term.nr) > -1){
	    let associatedTerm = leftPreannotations[j].term;
           let textLabel = $("<span></span>");
            textLabel.data("nr", leftPreannotations[j].nr);
            textLabel.data("associatedTerm", associatedTerm);
            textLabel.append(associatedTerm)
            
            let removeButton = $("<button type=\"button\" class=\"btn btn-default btn-xs lang-lang-remove-button \" aria-label=\"Remove text from theme\" title=\"Remove alignment\">"
                                 + "<span class=\"glyphicon glyphicon-remove remove-glyph\" aria-hidden=\"true\"  ></span>"
                                 + "</button>");
            textLabel.append(removeButton);
	   textLabel.addClass("badge");
        textLabel.addClass("label-badge");
	    textLabel.addClass("lang-lang-label")
            lang1Container.append(textLabel);
	}
    }
}



// Resets the links between the elements
function resetLinks() {
	$("#bgSvgContainer").empty();
}

d3.selection.prototype.moveToFront = function() {
    return this.each(function(){
                     this.parentNode.appendChild(this);
                     });
};


// Renders the links between the term/topic/text/theme elements
function renderLinks() {
	// Remove the highlighting just in case
	resetLinkHighlight();
	
	resetLinks();

    renderLangToLangLinks();
    
    if(showLeftNodes){
        renderNodeLeftLinks();
    }
    if(showRightNodes){
        renderNodeRightLinks();
    }
    
    
    // Fix to place the links behind the containers so that the user can scroll with mouse-drag
    /*
    d3.select("#bgSvgContainer").each(function(){
                               let parent = $(this).get(0).parentNode;
                                 parent.removeChild($(this).get(0));
                                parent.insertBefore($(this).get(0), parent.firstChild);

    })
    */
     }







// Renders alignment links
function renderLangToLangLinks() {
   
    // If any of the lists is empty, return
    if ($("#lang1List").children().length == 0
        || $("#lang2List").children().length == 0)
        return;
    
     
    // Prepare the scales to map the score of the link
    var maxScore = 1;
    let opacityScale = getOpacityScale(maxScore);
    let strokeWidthScale = getStrokeWidthScale(maxScore, LINK_WIDTHS)
    
    
    // Get the position of the first topic element and the first theme element
    let firstLang1Element = $("#lang1List > li.term-element:not(.not-displayed):first");
    let firstLang2Element = $("#lang2List > li.term-element:not(.not-displayed):first");
    
    let svgId = "themeLinksSvg"
    let links = prepareCanvasForLinks(firstLang1Element, firstLang2Element, svgId, "langLinksHighlight")
    
    d3.select("#lang2List").selectAll("li:not(.not-displayed)")
    .each(function(d, i){
        let lang2Element = $(this);

          d3.select("#lang1List").selectAll("li:not(.not-displayed)")
          .filter(function(e) {
                  return d.alignments.indexOf(parseInt(e.nr)) > -1;})
          .each(function(e, j){
                let lang1Element = $(this);
                
                drawLinks(lang1Element, lang2Element, 1,
                          opacityScale, strokeWidthScale, links,
                          { lang1: e.nr, lang2: d.nr }, "Theme #" + d.nr + "\n"
                          + "Text #" + e.nr, "lang-to-lang", svgId);
                });
	
            });
}

// Renders node links
function renderNodeLeftLinks() {
   
    // If any of the lists is empty, return
    if ($("#nodes1List").children().length == 0
        || $("#lang1List").children().length == 0)
        return;
    
    // Prepare the scales to map the score of the link
    var maxScore = 1;
    let opacityScale = getOpacityScale(maxScore);
    let strokeWidthScale = getStrokeWidthScale(maxScore, LINK_WIDTHS)
    
    
    // Get the position of the first topic element and the first theme element
    let firstNode1Element = $("#nodes1List > li.term-element:not(.not-displayed):first");
    let firstLang1Element = $("#lang1List > li.term-element:not(.not-displayed):first");
    
    let svgId = "node1Lang1"
    let links = prepareCanvasForLinks(firstNode1Element, firstLang1Element, svgId, "nodeLeftLinksHighlight")
    
    d3.select("#lang1List").selectAll("li:not(.not-displayed)")
    .each(function(d, i){
        let lang1Element = $(this);
          d3.select("#nodes1List").selectAll("li:not(.not-displayed)")
          .filter(function(e) {
                  return e.alignments.indexOf(parseInt(d.nr)) > -1;})
          .each(function(e, j){
                let node1Element = $(this);
                
                drawLinks(node1Element, lang1Element, 1,
                          opacityScale, strokeWidthScale, links,
                          { node1: e.nr, lang1: d.nr }, "Theme #" + d.nr + "\n"
                          + "Text #" + e.nr, "node1-to-lang1", svgId);
                });
    
            });
}

// Renders node links
function renderNodeRightLinks() {
   
    // If any of the lists is empty, return
    if ($("#nodes2List").children().length == 0
        || $("#lang2List").children().length == 0)
        return;
    

    // Prepare the scales to map the score of the link
    var maxScore = 1;
    let opacityScale = getOpacityScale(maxScore);
    let strokeWidthScale = getStrokeWidthScale(maxScore, LINK_WIDTHS)
    
    
    // Get the position of the first topic element and the first theme element
    let firstLang2Element = $("#lang2List > li.term-element:not(.not-displayed):first");
    let firstNode2Element = $("#nodes2List > li.term-element:not(.not-displayed):first");
    
    let svgId = "node2Lang2"
    let links = prepareCanvasForLinks(firstLang2Element, firstNode2Element, svgId, "nodeRightLinksHighlight")
    
    d3.select("#nodes2List").selectAll("li:not(.not-displayed)")
    .each(function(d, i){
        let node2Element = $(this);
          d3.select("#lang2List").selectAll("li:not(.not-displayed)")
          .filter(function(e) {
                  return d.alignments.indexOf(parseInt(e.nr)) > -1;})
          .each(function(e, j){
                let lang2Element = $(this);
                //alert(lang2Element.context.__data__.term);
                drawLinks(lang2Element, node2Element, 1,
                          opacityScale, strokeWidthScale, links,
                          { lang2: e.nr, node2: d.nr }, "Theme #" + d.nr + "\n"
                          + "Text #" + e.nr, "node2-to-lang2", svgId);
                });
    
            });
}

//////
// Help functions for drawing the links
///////////


// Prepare the canvas and get the links
///

function getOpacityScale(maxScore){
    return d3.scale.linear().domain([0, maxScore]).range([0, 1]);
}

function getStrokeWidthScale(maxScore, linkWidths){
    return d3.scale.linear().domain([0, maxScore]).range(linkWidths);

}
function prepareCanvasForLinks(firstLeftElement, firstRightElement, svgId, linksHighlightId){

    // Get the offset of the SVG element with regard to its parent container
	let svgLeft = Math.ceil(firstLeftElement.offset().left
				+ firstLeftElement.parent().scrollLeft()
		 		- $("#bgSvgContainer").offset().left
				+ firstLeftElement.outerWidth());
	let svgTop = Math.ceil(firstLeftElement.offset().top
				+ firstLeftElement.parent().scrollTop()
				- $("#bgSvgContainer").offset().top);
		
	let svgWidth = Math.ceil(firstRightElement.offset().left
				- (firstLeftElement.offset().left + firstLeftElement.outerWidth())
		 		- 1);
	let svgHeight = Math.ceil($("#mainPanelUpper").height() - svgTop);
	
	let svg = d3.select("#bgSvgContainer").append("svg:svg")
				.classed("svg-vis", true)
				.attr("id", svgId)
				.style("top", svgTop + "px")
				.style("left", svgLeft + "px")
				.attr("height", svgHeight + "px")
				.attr("width", svgWidth + "px")
				.attr("clip", [0, svgWidth, svgHeight, 0].join(" "));
	
	// Prepare the clipping path for inner canvas
	svg.append("clipPath")
		.attr("id", "canvasClip")
	.append("rect")
	    .attr("x", 0)
	    .attr("y", 0)
	    .attr("width", svgWidth)
	    .attr("height", svgHeight);
	
	let canvas = svg.append("g")
		.classed("canvas-vis", true)
		.attr("clip-path", "url(#canvasClip)");
    
  		
    let links = canvas.append("g")
    .attr("id", "termLinks");
    
    // Add an overlay for highlighting
    canvas.append("g")
    .attr("id", linksHighlightId);
    
     //for debugging
    /*
     canvas.append("rect")
	    .attr("x", 0)
	    .attr("y", 0)
	    .attr("width", svgWidth)
	    .attr("height", svgHeight)
     .style("fill", "lightgreen");
      */
    
    
    return links;
}

// Draw the actual lines
function drawLinks(leftElement, rightElement, termScore,
                opacityScale, strokeWidthScale, links,
                   datum, text, className, svgId){
    
    // Draw the links from terms to topics
    let offsetLeft = $("#" + svgId).offset().left;
    let offsetTop = $("#" + svgId).offset().top;
    
    let scrollbarWidth = 8;
    // Get the port position (this is only needed  to be calculated once, so if things get slow, do earlier)
    let leftPortX = leftElement.offset().left - offsetLeft + leftElement.outerWidth() + scrollbarWidth;
    let leftPortY = leftElement.offset().top - offsetTop + Math.floor(leftElement.outerHeight()/2);
              
    // Get the port position
    let rightPortX = rightElement.offset().left - offsetLeft;
    let rightPortY = rightElement.offset().top - offsetTop + Math.floor(rightElement.outerHeight()/2);
		
    
    
    // Draw the link
    links.append("line")
            .classed(className, true)
            .datum(datum)
            .attr("x1", leftPortX)
            .attr("y1", leftPortY)
            .attr("x2", rightPortX)
            .attr("y2", rightPortY)
            .style("stroke-opacity", opacityScale(termScore))
            .style("stroke", strokeWidthScale(termScore))
            .style("stroke", "black")
            .append("svg:title")
            .text(text);
}


/////////
// Listener functions
//////////

// Updates the links on list scroll
// Set a timer so that the links will not always be updated when scrolling, as this slows down the scrolling
var timer = null;
function onListScroll() {
	//renderLinks();
    if(timer !== null) {
        clearTimeout(timer);
    }
    timer = setTimeout(function() {
        renderLinks();
    }, 200);
}


// Drag terms
// Handles the text element drag start event
function onLangElementDragStart(event) {

    if (modelCurrentAction != ANNOTATE){
	alert("You can't do annotations in browse mode");
	return;
    }

    let originalEvent = event.originalEvent;
    let termElement = $(event.target).parentsUntil("#lang1List", ".term-element");

    let eventNr  = d3.select(termElement["context"]).datum().nr;
    
    modelCurrentDragLang1Nr = eventNr

    // Mark the element as the source of dragged data
    // (used for filtering in dragover handlers, since there is no way to access the data)

    /*
    termElement.addClass("dragged");
    let transferData = {
        //textId: d3.select(event.target).datum().id
        textNr: eventNr
    };
    
    originalEvent.dataTransfer.setData("term-element", JSON.stringify(transferData));
*/
    originalEvent.dataTransfer.effectAllowed = "copy";
    originalEvent.dataTransfer.dropEffect = "copy";
}

function onNodeElementDragStart(event) {

    if (modelCurrentAction != ANNOTATE){
	alert("You can't do annotations in browse mode");
	return;
    }

    let originalEvent = event.originalEvent;
    let termElement = $(event.target).parentsUntil("#nodes1List", ".term-element");

     modelCurrentDragNode1Alignments = d3.select(termElement["context"]).datum().alignments;
    
    // Mark the element as the source of dragged data
    // (used for filtering in dragover handlers, since there is no way to access the data)

    originalEvent.dataTransfer.effectAllowed = "copy";
    originalEvent.dataTransfer.dropEffect = "copy";
}


// Handles the  element drag end event
function onLangElementDragEnd(event) {
    let originalEvent = event.originalEvent;
    let termElement = $(event.target);
    
    //originalEvent.dataTransfer.clearData();
    modelCurrentDragLang1Nr = null;
    
    // Unmark the element as the source of dragged data
    termElement.removeClass("dragged");
}

function onNodeElementDragEnd(event) {
    let originalEvent = event.originalEvent;
    let termElement = $(event.target);
    
    modelCurrentDragNode1Alignments = null;
   
    // Unmark the element as the source of dragged data
    termElement.removeClass("dragged");
}

function onLangElementDragEnterOver(event) {
  
    let originalEvent = event.originalEvent;
    let lang2Element = $(event.currentTarget);
    lang2Element.addClass("drop-feedback");
    
    let currentLang2Element = d3.select(lang2Element.get(0)).datum();
    originalEvent.dataTransfer.dropEffect = "copy";
    originalEvent.preventDefault();
        
    return false;
}

function onLangElementDragLeave(event){
    let lang2Element = $(event.currentTarget);
    lang2Element.removeClass("drop-feedback");
}

function onLangElementDrop(event){
    if (modelCurrentDragLang1Nr == null && modelCurrentDragNode1Alignments == null){
	return;
    }
    let toAdd = null;
	
    if(modelCurrentDragNode1Alignments){
	toAdd = modelCurrentDragNode1Alignments;
    }
    else{
	toAdd = [modelCurrentDragLang1Nr];
    }
    
    event.preventDefault();
    let originalEvent = event.originalEvent;
    originalEvent.stopPropagation();
    let termElement = $(event.currentTarget);
    let lang2Nr  = d3.select(termElement["context"]).datum().nr;

    for (let i = 0; i < toAdd.length; i++) {
	modelAddLangLangLink(toAdd[i], lang2Nr);
    }
    
    //modelAddLangLangLink(modelCurrentDragLang1Nr, lang2Nr);
    
    let lang2Element = $(event.currentTarget);
    lang2Element.removeClass("drop-feedback");

    modelCurrentDragLang1Nr = null;
    modelCurrentDragNode1Alignments = null;
    
    disableAfterStartingAnnotate();
}

function onNodeElementDrop(event){
    if (modelCurrentDragLang1Nr == null && modelCurrentDragNode1Alignments == null){
	return;
    }
    let toAdd = null;
	
    if(modelCurrentDragNode1Alignments){
	toAdd = modelCurrentDragNode1Alignments;
    }
    else{
	toAdd = [modelCurrentDragLang1Nr];
    }
    
    event.preventDefault();
    let originalEvent = event.originalEvent;
    originalEvent.stopPropagation();
    let termElement = $(event.currentTarget);
    let lang2Alignments  = d3.select(termElement["context"]).datum().alignments;

    for (let i = 0; i < toAdd.length; i++) {
	for (let j = 0; j < lang2Alignments.length; j++){
	    modelAddLangLangLink(toAdd[i], lang2Alignments[j]);
	}
    }
       
    let lang2Element = $(event.currentTarget);
    lang2Element.removeClass("drop-feedback");

    modelCurrentDragLang1Nr = null;
    modelCurrentDragNode1Alignments = null;
    
    disableAfterStartingAnnotate();
}

// Removes a text from a theme
function onAlignRemove(){
    let termElement = $(this).parentsUntil("#lang2List", ".term-element");
	
    let term = d3.select(termElement.get(0)).datum();
    let alignLabel = $(this).parent(".lang-lang-label");
    let lang1TermNr = alignLabel.data("nr")
    let lang2TermNr = term.nr
    
    modelremoveLangLangLink(lang1TermNr, lang2TermNr);
  
    disableAfterStartingAnnotate();
}



// Resets highlighting
function resetHighlight() {
    
    d3.selectAll("." + HIGHLIGHT)
     .classed(HIGHLIGHT, false);
    
    d3.selectAll("." + DIRECTHIGHLIGHT)
    .classed(DIRECTHIGHLIGHT, false);

    
    resetLinkHighlight();
}



function resetLinkHighlight() {
    d3.selectAll(".link-highlight, .link-direct-highlight")
    .classed("link-highlight", false)
    .classed("link-direct-highlight", false);
    
    d3.selectAll(".link-overlay-highlight, .link-overlay-direct-highlight, " +
                 ".link-overlay-highlight-bg, .link-overlay-direct-highlight-bg")
    .remove();
}


// Handles hovering for a document element
function onLang1ElementMouseEnter() {
    resetHighlight();
    highlightLang1Element($(this), DIRECTHIGHLIGHT, HIGHLIGHT);
}

// Handles hovering for a document element
function onLang1ElementMouseLeave() {
	resetHighlight();
}

// Handles hovering for a term element
function onLang2ElementMouseEnter() {
    resetHighlight();
    highlightLang2Element($(this), DIRECTHIGHLIGHT, HIGHLIGHT);
}

// Handles hovering for a term element
function onLang2ElementMouseLeave() {
    resetHighlight();
}

function nodes1ListElementMouseEnter(){
    resetHighlight();
    highlightNode1Element($(this), DIRECTHIGHLIGHT, HIGHLIGHT);
}

function nodes2ListElementMouseEnter(){
    resetHighlight();
    highlightNode2Element($(this), DIRECTHIGHLIGHT, HIGHLIGHT);                           
}

function nodes1ListElementMouseLeave(){
    resetHighlight();
}

function nodes2ListElementMouseLeave(){
    resetHighlight();
}

////
// Render link highlights
//////////

// Help function for rendering link highlighting
function renderLinksHighlight(name, link){
    d3.select(name).append("line")
    .classed("link-overlay-highlight-bg", true)
    .attr("x1", parseFloat(link.attr("x1")))
    .attr("y1", parseFloat(link.attr("y1")))
    .attr("x2", parseFloat(link.attr("x2")))
    .attr("y2", parseFloat(link.attr("y2")));
    
    d3.select(name).append("line")
    .classed("link-overlay-highlight", true)
    .attr("x1", parseFloat(link.attr("x1")))
    .attr("y1", parseFloat(link.attr("y1")))
    .attr("x2", parseFloat(link.attr("x2")))
    .attr("y2", parseFloat(link.attr("y2")));
    
}

// Renders highlighting for a lang2 to lang2 link
function renderLangToLangLinkHighlight() {
    var link = d3.select(this);
    renderLinksHighlight("#langLinksHighlight", link);
}

function renderNodeLeftLinksHighlight() {
    var link = d3.select(this);
    renderLinksHighlight("#nodeLeftLinksHighlight", link);
}

function renderNodeRightLinksHighlight() {
    var link = d3.select(this);
    renderLinksHighlight("#nodeRightLinksHighlight", link);
}





//////
// Functions for direct highligting
/////

// Highlights the given term element and related items
function highlightLang2Element(termElement, direct, indirect) {
	
    // First of all, highlight the element under cursor
    termElement.addClass(direct);

    // Get the term datum
    let term = d3.select(termElement.get(0)).datum();
	
    highlightLang2Links(term.nr);
    highlightNode2Links(term.nr);

    secondaryHighlightLang1(indirect, term.nr, "#lang1List",  "#lang2List", "#nodes1List");
    secondaryHighlightNode(indirect, term.nr, "#nodes2List");
}

// Highlights the given term element and related items
function highlightLang1Element(termElement, direct, indirect) {
	
    // First of all, highlight the element under cursor
    termElement.addClass(direct);

    // Get the term datum
    let term = d3.select(termElement.get(0)).datum();
	
    highlightLang1Links(term.nr);
    highlightNode1Links(term.nr);
    
    secondaryHighlightLang2(indirect, term.nr, "#lang2List", "#lang1List", "#nodes2List");
    secondaryHighlightNode(indirect, term.nr, "#nodes1List");   	
}

function highlightNode1Element(termElement, direct, indirect){
    
    // First of all, highlight the element under cursor
    termElement.addClass(direct);

    // Get the datum
    let datum = d3.select(termElement.get(0)).datum();
    
    for (let j = 0; j < datum.alignments.length; j++){
	let nr = datum.alignments[j];
	
	d3.select("#lang1List").selectAll("li")
	    .filter(function(d, i){
            return d.nr == nr;
	    })
	    .each(function(d, i){
		 highlightLang1Element($(this), indirect, indirect)});
    } 
}

function highlightNode2Element(termElement, direct, indirect){
    
    // First of all, highlight the element under cursor
    termElement.addClass(direct);

    // Get the datum
    let datum = d3.select(termElement.get(0)).datum();

    for (let j = 0; j < datum.alignments.length; j++){
	let nr = datum.alignments[j];
	
	d3.select("#lang2List").selectAll("li")
	    .filter(function(d, i){
            return d.nr == nr;
	    })
	    .each(function(d, i){
		 highlightLang2Element($(this), indirect, indirect)});
    } 
}


function secondaryHighlightLang1(highlightClass, nr, listName, otherListName, secondaryNodesList){
        d3.select(listName).selectAll("li")
    .filter(function(d, i){
            return d.alignments.indexOf(nr) != -1;
            })
    .classed(highlightClass, true)
    .each(function(d, i){
        secondaryHighlightNode(highlightClass, d.nr, secondaryNodesList);
	highlightNode1Links(d.nr);
    })
    .each(function(d, i){
	thirdlyHighlightLang1(otherListName, d.nr, highlightClass);
    })
}

function secondaryHighlightLang2(highlightClass, nr, listName, otherListName, secondaryNodesList){
        d3.select(listName).selectAll("li")
    .filter(function(d, i){
            return d.alignments.indexOf(nr) != -1;
            })
    .classed(highlightClass, true)
    .each(function(d, i){
        secondaryHighlightNode(highlightClass, d.nr, secondaryNodesList);
	highlightNode2Links(d.nr);
    })
    .each(function(d, i){
	thirdlyHighlightLang2(otherListName, d.nr, highlightClass);
    })
	 }

function thirdlyHighlightLang1(otherListName, nr, highlightClass){
    d3.select(otherListName).selectAll("li")
	.filter(function(d, i){
            return d.alignments.indexOf(nr) != -1;
	})
	.classed(highlightClass, true)
	.each(function(d, i){
	highlightNode2Links(d.nr);
    })
}

function thirdlyHighlightLang2(otherListName, nr, highlightClass){
     d3.select(otherListName).selectAll("li")
    .filter(function(d, i){
            return d.alignments.indexOf(nr) != -1;
            })
	.classed(highlightClass, true)
    	.each(function(d, i){
	highlightNode1Links(d.nr);
    })
	  }

function secondaryHighlightNode(highlightClass, nr, listName){
        d3.select(listName).selectAll("li")
        .filter(function(d, i){
                return d.alignments.indexOf(nr) != -1;
                })
        .classed(highlightClass, true)
}
                                                                        
///////
// Higlight links
//////

function highlightLang2Links(term2Nr){
    // Get the related term-to-topic links and mark them
    d3.selectAll(".lang-to-lang")
    .filter(function(f, i){
            return term2Nr == f.lang2;
            })
    .classed("link-highlight", true)
    .each(renderLangToLangLinkHighlight);
}

function highlightLang1Links(term1Nr){
    // Get the related term-to-topic links and mark them
    d3.selectAll(".lang-to-lang")
    .filter(function(f, i){
            return term1Nr == f.lang1;
            })
    .classed("link-highlight", true)
    .each(renderLangToLangLinkHighlight);
}

function highlightNode1Links(termNr){
    d3.selectAll(".node1-to-lang1")
	.filter(function(f, i){
            return termNr == f.lang1;
        })
	.classed("link-highlight", true)
	.each(renderNodeLeftLinksHighlight);
}

function highlightNode2Links(termNr){
    d3.selectAll(".node2-to-lang2")
	.filter(function(f, i){
            return termNr == f.lang2;
        })	    
	.classed("link-highlight", true)
	.each(renderNodeRightLinksHighlight);
}

//////////
// Button clicks
//////////

// TODO: Now, it is only checked in the gui that the user doesn't save when not in annotation mode.
// Should perhaps be checked in the back-end as well
function onSave(){
    
	if (modelCurrentAction == ANNOTATE){
	    modelUndoClicked = false;
	    modelSaveDataLoadNext();
	}

	if (modelCurrentAction == BROWSEANNOTATED){
            modelLoadNextAnnotatedAlignment();
	}
    

    /*
    // if in searchWriteMode, the save-button (which is a next-button in this case), should load next to annotate
    else{ // First, data must be loaded according to the content of the serach string. Only thereafter will the save button
	// function as a standard save button
	modelCurrentFilterStr = $("#textinput").val();
	setButtonsInAnnotationModeAndLoadNextAlignment();
    }
     */
}

function onStepBack(){
    if (modelCurrentAction == BROWSEANNOTATED){
	modelLoadPreviousAnnotatedAlignment();
    }
    if (modelCurrentAction == ANNOTATE){
	modelLoadPreviousAnnotatedAlignment();
	modelUndoClicked = true;
    }
}

function onDelete(){

    if (modelCurrentAction == ANNOTATE){
    modelUndoClicked = false;
	modelDeleteDataLoadNext();
    }

    else{
	alert("Not possible to delete in browse mode");
    }
}

function onChangeOrder(){

    if(modelReverseLang){
        modelReverseLang = false;
    }
    else{
        modelReverseLang = true;
    }
                                                                        
    showPreannotation();   
}

                                                                        
function onClickLeft(){
    var leftNodes = null;
    if (!modelReverseLang){
        leftNodes = modelNodesLang1;
    }
    else{
        leftNodes = modelNodesLang2;
    }
                                                                        
    if(showLeftNodes){
        showLeftNodes = false;
        $("#nodes1").removeClass("show-nodes-button-selected");
    }
    else{
        showLeftNodes = true;
        $("#nodes1").addClass("show-nodes-button-selected");
    }
                                                                        
    
    showNodes("#nodes1List", showLeftNodes, leftNodes, true);
    renderLinks();
                                                                        
}

function onClickRight(){
    var rightNodes = null;
    if (!modelReverseLang){
        rightNodes = modelNodesLang2;
    }
    else{
        rightNodes = modelNodesLang1;
    }
                                                                        
    if(showRightNodes){
        showRightNodes = false;
        $("#nodes2").removeClass("show-nodes-button-selected");
    }
    else{
        showRightNodes = true;
        $("#nodes2").addClass("show-nodes-button-selected");
    }

    showNodes("#nodes2List", showRightNodes, rightNodes, false);
    renderLinks();
}
