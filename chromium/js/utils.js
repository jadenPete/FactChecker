var defaults = {
	definitionURLs: "https://factchecker.github.io/selectors.json"
};

function getOption(option, callback) {
	chrome.storage.sync.get({[option]: defaults[option]}, callback);
}

function sendUpdateMessage(callback) {
	chrome.runtime.sendMessage("updateDefinitions", callback);
}
