let scores = document.getElementById("scores")
let liberal = document.getElementById("liberal");
let conservative = document.getElementById("conservative");

function updateScore(message) {
	if (message instanceof Array && message.length == 2 && message[0] == "updateScore") {
		percent = Math.round(100 * message[1]);

		liberal.textContent = `${100 - percent}% Liberal`;
		conservative.textContent = `${percent}% Conservative`;
		scores.style.display = "block";
	}
}

chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
	updateScore(message);
});

chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
	chrome.tabs.sendMessage(tabs[0].id, "queryScore", function(response) {
		// If the content script has been injected
		if (typeof chrome.runtime.lastError === "undefined") {
			updateScore(response);
		}
	});
});

document.getElementById("options").onclick = function() {
	chrome.runtime.openOptionsPage();
};

document.getElementById("rescan").onclick = function() {
	// If the current tab doesn't begin with chrome://
	chrome.tabs.executeScript({"file": "js/contentScript.js"}, function() {
		void chrome.runtime.lastError;
	});
};
