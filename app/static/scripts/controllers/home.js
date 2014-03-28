'use strict';

// http://stackoverflow.com/questions/11172269/select-all-and-remove-all-with-chosen-js/11172403#11172403

angular.module('framingApp').controller('HomeCtrl', function ($scope, $window, $location, Frame, Analysis) {

  Frame.all().then(function(response) { $scope.frames = response.data; });
  Analysis.all().then(function(response) { $scope.analyses = response.data; });

  $scope.showAnalysis = function(analysis) {
  	console.log(analysis);
	$location.path('/analysis/' + analysis.id);
  }

});
