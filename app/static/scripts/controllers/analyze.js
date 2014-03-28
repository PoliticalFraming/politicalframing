'use strict';

angular.module('framingApp').controller('AnalyzeCtrl', function ($scope, $http, Frame, Speech, State, Analysis) {

  Frame.all().then(function(response) { $scope.frames = response.data; });
  $scope.USStateList = State.getStates();
  $scope.speeches = [];
  $scope.current = {
    count: 0,
    pages: 0,
    filters: {
      page: 1,
      states: [],
      frame: null,
      phrase: '',
      start_date: null,
      end_date: null,
      highlight: 'true'
    }
  };
  $scope.dateOptions = { changeYear: true, changeMonth: true, yearRange: '1900:-0' };
  $scope.navType = 'pills';

  $scope.analysisRequested = function() {
    $scope.$broadcast('analysisRequested', {});
  }

});

