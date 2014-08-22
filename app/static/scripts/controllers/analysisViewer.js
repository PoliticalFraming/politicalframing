'use strict';

angular.module('framingApp').controller('AnalysisViewerCtrl', function ($scope, $window, $routeParams) {

  $scope.speeches = [];
  $scope.current = {
    count: 0,
    pages: 0,
    filters: {
      page: null,
      phrase: null,
      frame: null,
      id: $routeParams.id
    }
  };

});