/**
 * Copy to CLipboard JS Init
 *
 * @author We Both
 * @version 1.0
 * @requires
 *
 */


  // Get the elements.
	// - the 'pre' element.
	// - the 'div' with the 'paste-content' id.

	var pre = document.getElementsByTagName('pre');

	// Add a copy button in the 'pre' element.
	// which only has the className of 'language-'.

	for (var i = 0; i < pre.length; i++) {
		var isLanguage = pre[i].children[0].className.indexOf('language-');

		if ( isLanguage === 0 ) {
			var button           = document.createElement('button');
					button.className = 'btn btn-sm btn-link color--white copy-button';
					button.textContent = 'Copy';

					pre[i].appendChild(button);
		}
	}

  // Run Clipboard

	var copyCode = new ClipboardJS('.copy-button', {
		target: function(trigger) {
			return trigger.previousElementSibling;
    }
	});

	// On success:
	// - Change the "Copy" text to "Copied".
	// - Swap it to "Copy" in 2s.
	// - Lead user to the "contenteditable" area with Velocity scroll.

	copyCode.on('success', function(event) {
		event.clearSelection();
    event.trigger.className = 'btn btn-sm btn-link color--white copy-button copied';
		event.trigger.textContent = 'Copied';
		window.setTimeout(function() {
      event.trigger.className = 'btn btn-sm btn-link color--white copy-button';
			event.trigger.textContent = 'Copy';
		}, 2000);
	});

	// On error (Safari):
	// - Change the  "Press Ctrl+C to copy"
	// - Swap it to "Copy" in 2s.

	copyCode.on('error', function(event) {
    event.trigger.className = 'btn btn-sm btn-link color--white copy-button not-copied';
		event.trigger.textContent = 'Press "Ctrl + C" to copy';
		window.setTimeout(function() {
      event.trigger.className = 'btn btn-sm btn-link color--white copy-button';
			event.trigger.textContent = 'Copy';
		}, 5000);
	});
