key = "selector-" + window.location.hostname;

function updateScore(score) {
	chrome.runtime.sendMessage(["updateScore", score]);
}

chrome.storage.sync.get(key, function(items) {
	let text = "";

	for (const node of document.querySelectorAll(items[key])) {
		text += node.innerText + " ";
	}

	let request = new XMLHttpRequest();

	request.onreadystatechange = function() {
		if (request.readyState === XMLHttpRequest.DONE && request.status === 200) {
			updateScore(score = JSON.parse(request.responseText));
		}
	}

	request.open("POST", "http://127.0.0.1:8080/predict");
	request.send(JSON.stringify(text));
});

chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
	updateScore(score);
	sendResponse();
});
