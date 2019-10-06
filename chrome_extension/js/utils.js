var defaults = {
	definitionURLs: "https://factchecker.github.io/definitions.json"
};

function getOption(option, callback) {
	keys = {}
	keys[option] = defaults[option];

	chrome.storage.sync.get(keys, callback);
}

function updateDefinitions(callback) {
	if (typeof callback !== "function") {
		callback = function() {}
	}

	getOption("definitionURLs", function(items) {
		try {
			var urls = items.definitionURLs.split("\n");
			var definitions = {};

			for (var i = 0; i < urls.length; i++) {
				request = new XMLHttpRequest();
				request.open("GET", urls[i], false);
				request.send(null);

				Object.assign(definitions, JSON.parse(request.responseText));
			}

			// Add selector prefix and convert arrays
			for (var host in definitions) {
				var value = definitions[host];
				var selector = value instanceof Array ? value.join("") : value;

				delete definitions[host];
				definitions["selector-" + host] = selector;
			}

			chrome.storage.local.set(definitions, callback);
		} catch {
			callback();
		}
	});
}
