'use strict';

// http://stackoverflow.com/questions/11172269/select-all-and-remove-all-with-chosen-js/11172403#11172403

angular.module('framingApp').controller('MainCtrl', function ($scope, $window, Speech, Frame, State) {

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
      phrase: null,
      start_date: null,
      end_date: null,
    }
  };

  // COPY OF FUNCTION IN DIRECTIVE =(
  $scope.loadSpeeches = function () {
    if ($scope.current.filters.phrase === null) { return; }
    Speech.where($scope.current.filters).then(function (response) {
      $scope.speeches = response.data;
      $scope.current.count = response.meta.count;
      $scope.current.pages = response.meta.pages;
      console.log($scope.current);
    });
  }; 

  $scope.dateOptions = { changeYear: true, changeMonth: true, yearRange: '1900:-0' };
  $scope.navType = 'pills';
});
