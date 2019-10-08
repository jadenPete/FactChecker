let update = document.getElementById("update");
let textarea = document.getElementsByTagName("textarea")[0];

function setDefinitionURLs(items) {
	textarea.value = items.definitionURLs;
}

// Load the URLs in to the textarea
getOption("definitionURLs", setDefinitionURLs);

textarea.onchange = function() {
	chrome.storage.sync.set({definitionURLs: textarea.value});
};

update.onclick = function() {
	update.disabled = true;

	updateMessage(function() {
		update.disabled = false;
	});
};

document.getElementById("reset").onclick = function() {
	chrome.storage.sync.set({definitionURLs: defaults.definitionURLs}, setDefinitionURLs);
};
