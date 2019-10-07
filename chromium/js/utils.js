var defaults = {
	definitionURLs: "https://factchecker.github.io/definitions.json"
};

function getOption(option, callback) {
	chrome.storage.sync.get({[option]: defaults[option]}, callback);
}

function updateDefinitions(callback) {
	if (typeof callback !== "function") {
		callback = function() {};
	}

	getOption("definitionURLs", function(items) {
		try {
			let definitions = {};

			for (const url of items.definitionURLs.split("\n")) {
				request = new XMLHttpRequest();
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
