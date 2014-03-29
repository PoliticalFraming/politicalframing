'use strict';

angular.module('framingApp').controller('BrowseSpeechesCtrl', function ($scope, $window, Speech, Frame, State) {

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

  $scope.phraseSearched = function() {
    $scope.$broadcast('phraseSearched');
  }

});
