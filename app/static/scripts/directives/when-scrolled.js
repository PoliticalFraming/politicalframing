'use strict';
// http://docs.angularjs.org/error/$rootScope:inprog

angular.module('framingApp').directive('whenScrolled', function() {
  return function(scope, element, attr) {
    var raw = element[0];
    var percentage = 0.15;
    element.bind('scroll', function() {
        console.log(raw.scrollTop);
        console.log(raw.offsetHeight);
        console.log(raw.scrollHeight);
        if (raw.scrollTop + raw.offsetHeight + percentage * (raw.offsetHeight) >= raw.scrollHeight) {
          scope.$apply(attr.whenScrolled);
        }
    });
  };

});
