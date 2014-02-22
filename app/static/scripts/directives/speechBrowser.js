'use strict';

angular.module('framingApp').directive('speechBrowser', function() {
  return {
    restrict: 'E',
    transclude: true,
    controller: function ($scope) {
      $scope.headers = ['ID', 'Title', 'Date', 'Speaker', 'State'];
    },
    scope: {
      speeches: '=',
      filters: '=',
      count: '='
    },
    templateUrl: '/partials/speech-browser.html',
    link: function(scope, element, attrs) {
      
      // console.log($table);
      // console.log($table.closest('.table-wrapper'));

    }
  };
});