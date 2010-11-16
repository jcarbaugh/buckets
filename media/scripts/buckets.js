var Buckets = {
	
}

var bindUpload = function() {
	
	var targets = $("ol#directories li, ol#files");
	
	targets.bind("dragenter", function(e) {
		e.preventDefault();
	});
	
	targets.bind("dragover", function(e) {
		$(this).addClass('hovered');
		e.preventDefault();
		
	});
	
	targets.bind("dragleave", function(e) {
		$(this).removeClass('hovered');
	});
	
	targets.bind("drop", function(e) {
		
		var target = $(this);
		target.removeClass('hovered');
		
		var bucket = target.attr('data-bucket');
		var keyPrefix = target.attr('data-keyprefix');
		
		var dir;
		if (target.hasClass('new-directory')) {
			dir = prompt('Directory name');
		}
		
		var data = e.originalEvent.dataTransfer;
		
		if (data.files.length == 1) {
			
			var file = data.files[0];
			var path = bucket + keyPrefix;
			if (dir) {
				path += dir + '/';
			}
			
			var node = $('<li><h3>' + file.fileName + '</h3><p>' + path  + '</p></li>');
			$('#uploads').append(node);
						
			var reader = new FileReader(file);
			reader.onload = function(e) {
				
				var onSuccess = function(resp, status, req) {
					$('nav#ls').load(window.location.pathname + '?partial', function(){
						bindUpload();
						node.addClass('done');
						setTimeout(function() { node.fadeOut(); }, 5000);
					});
				};
				
				var uploadData = {
					bucket: bucket,
					key_prefix: keyPrefix,
					filename: file.fileName,
					data: window.btoa(e.target.result)
				};
				
				$.ajax({
					type: 'POST',
					url: '/s3/' + path,
					data: uploadData,
					dataType: 'json',
					success: onSuccess,
					error: function(req, status, err) {
						if (confirm('File exists, overwrite?')) {
							$.ajax({
								type: 'POST',
								url: '/s3/' + path + '?force',
								data: uploadData,
								dataType: 'json',
								success: onSuccess,
								error: function(req, status, err) {
									node.addClass('error');
								}
							});
						} else {
							node.fadeOut();
						}
					}
				});
				
			};
			reader.readAsBinaryString(file);
			
		} else {
			alert('Sorry, only single file uploads are allowed. Multiple file support is on the to-do list.');
		}
		
		e.preventDefault();
		
	});
	
}

$().ready(function() {
	
	/*
	 * bucket switcher select box
	 */
	
	$("#bucket_switcher input[type=submit]").hide();
	
	$("#bucket_switcher select").bind('change', function() {
		window.location = '/s3/' + this.value;
	});
	
	/*
	 * file/directory actions popup
	 */
	
	$("a.actions").bind('click', function() {
		// var parent = $(this).parent();
		// var type = parent.hasClass('directory') ? 'directory' : 'file';
		return false;
	}).fancybox({
		'speedIn'		:	600, 
		'speedOut'		:	200, 
		'overlayShow'	:	true
	});
	
	/*
	 * bind upload handlers
	 */
	
	bindUpload();
	
});