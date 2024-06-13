//Loads the global header and footer
$(function() {
	/* Header Footer */
	AjaxManager.send({
		url: 'https://navigation.ancestry.com/ajax/header/standard?loginUrl=a&logoutUrl=b&source=' + window.location.hostname + window.location.pathname,
		success: function (){			$("a.navTrees").addClass("navLinkSelected");
		}
	});
	AjaxManager.send({
		url: 'https://footer.ajax.ancestry.com'
	});
	/* Page Specific JS */
	$( document ).ready(function() {
	});
});