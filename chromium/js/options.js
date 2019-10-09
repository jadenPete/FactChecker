let update = document.getElementById("update");
let textarea = document.getElementsByTagName("textarea")[0];

// Load the URLs in to the textarea
getOption("definitionURLs", function(items) {
	textarea.value = items.definitionURLs;
});

textarea.onchange = function() {
	chrome.storage.sync.set({definitionURLs: textarea.value});
};

update.onclick = function() {
	update.disabled = true;

	sendUpdateMessage(function() {
		update.disabled = false;
	});
};

document.getElementById("reset").onclick = function() {
	chrome.storage.sync.set({definitionURLs: defaults.definitionURLs}, function() {
		textarea.value = defaults.definitionURLs;
	});
};
