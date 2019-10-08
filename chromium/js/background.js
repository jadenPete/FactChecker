function createAlarm() {
	chrome.alarms.create({when: Date.now() + 1000 * 60 * 60 * 24 * 2});
}

function updateDefinitions(callback) {
	if (typeof callback !== "function") {
		callback = function() {};
	}

	getOption("definitionURLs", function(items) {
		try {
			let definitions = {};

			for (const url of items.definitionURLs.split("\n")) {
				let request = new XMLHttpRequest();
				request.open("GET", urls[i], false);
				request.send(null);

				Object.assign(definitions, JSON.parse(request.responseText));
			}

			// Add selector prefix and convert arrays
			for (const [key, value] in definitions) {
				delete definitions[key];
				definitions["selector-" + key] = value instanceof Array ? value.join("") : value;
			}

			chrome.storage.local.set(definitions, callback);
		} catch {
			callback();
		}
	});
}

chrome.alarms.onAlarm.addListener(function() {
	updateDefinitions();
	createAlarm();
});

chrome.runtime.onInstalled.addListener(updateDefinitions);

chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
	if (message === "updateDefinitions") {
		updateDefinitions(sendResponse);
	}
});
