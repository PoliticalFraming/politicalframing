'use strict';

// http://stackoverflow.com/questions/11172269/select-all-and-remove-all-with-chosen-js/11172403#11172403

angular.module('framingApp').controller('AnalysisViewerCtrl', function ($scope, $window, $routeParams) {

  $scope.current = {
    count: null,
    filters: {
      page: null,
      phrase: null,
      frame: null,
      id: $routeParams.id
    }
  };

  // console.log("before broadcast");

  // $scope.$broadcast('graphRequested');

  // console.log("after broadcast");

  // $scope.$apply(function () {
    
  // });

  // $scope.$apply();

  // setTimeout(function() {
  //   $scope.$broadcast('graphRequested');
  //   console.log("event emitted??");
  // }, 15);

  // $scope.graphRequested = function() {
  //   $scope.$broadcast('graphRequested');
  // }

  // $scope.graphRequested();


});