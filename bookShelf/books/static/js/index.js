$(document).ready(function() {
	$('.promos').hide();
	$('.promos').fadeIn(1000);
	
	$('.sidebar').css('width','0%');
	$('.sidebar').animate({width:'25%'},300);

	// $('.sidebar').hide();
	// $('.sidebar').slideDown(1000);
	// $('.sidebar').css('width','0%');

	$('.navbar').hide();
	$('.navbar').slideDown(300);
	$('.nav').hide();
	$('.nav').slideDown(300);

	
	/*$('.navbar').css('right','100%');	
	$('.navbar').css('left','');	
	$('.navbar').animate({right:'',left:'29%'},1000);*/
});
