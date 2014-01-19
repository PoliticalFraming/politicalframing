// http://docs.angularjs.org/error/$rootScope:inprog

// angular.module('framingApp')
// 	.directive("selectallstates", function() {
// 	  return function(scope, element, attrs) {
// 	  	// console.log(scope);
// 	  	console.log($(element).children('> option'));
// 	  	$(element).children('> option').prop("selected", "selected");
// 	  	// $(element).trigger("change");
// 	  	// console.log(attrs);

// 		// scope.$apply(function() {
// 			// $("#states > option").prop("selected","selected");
// 			// $("#states").trigger("change");
//         // });
// 	  }
// 	});

angular.module('framingApp').directive('whenScrolled', function() {
    return function(scope, elm, attr) {
        var raw = elm[0];

        var percentage = .15;

        elm.bind('scroll', function() {
        	console.log(raw.scrollTop);
        	console.log(raw.offsetHeight);
        	console.log(raw.scrollHeight);
            if (raw.scrollTop + raw.offsetHeight + percentage * (raw.offsetHeight) >= raw.scrollHeight) {
                scope.$apply(attr.whenScrolled);
            }
        });
    };
});
