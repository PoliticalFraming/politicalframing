'use strict';

angular.module('framingApp').directive('speechBrowser', function() {
  return {
    restrict: 'E',
    transclude: true,
    controller: function ($scope) {
      $scope.headers = ['speech_id', 'title', 'speaker_raw'];
    },
    scope: {
      speeches: '=',
      filters: '=',
      count: '='
    },
    templateUrl: '/partials/speech-browser.html'
  };
});