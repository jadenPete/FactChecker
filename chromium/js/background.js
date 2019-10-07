function createAlarm() {
	chrome.alarms.create({
		when: Date.now() + 1000 * 60 * 60 * 24 * 2
	});
}

chrome.alarms.onAlarm.addListener(function() {
	updateDefinitions();
	createAlarm();
});

chrome.runtime.onInstalled.addListener(updateDefinitions);
