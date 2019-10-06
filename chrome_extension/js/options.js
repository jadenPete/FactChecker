var update = document.getElementById("update");
var reset = document.getElementById("reset");
var textarea = document.getElementsByTagName("textarea")[0];

function setDefinitionURLs(items) {
	textarea.value = items.definitionURLs;
}

// Load the URLs in to the textarea
getOption("definitionURLs", setDefinitionURLs);

textarea.onchange = function() {
	chrome.storage.sync.set({
		definitionURLs: textarea.value
	});
}

update.onclick = function() {
	update.disabled = true;

	updateDefinitions(function() {
		update.disabled = false;
	});
}

reset.onclick = function() {
	chrome.storage.sync.set({
		definitionURLs: defaults.definitionURLs
	}, setDefinitionURLs);
}
