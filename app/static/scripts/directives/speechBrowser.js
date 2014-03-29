'use strict';

angular.module('framingApp').directive('speechBrowser', function() {
  return {
    restrict: 'E',
    transclude: true,
    scope: {
      speeches: '=',
      current: '='
    },
    controller: function ($scope, $modal, $log, Speech) {
      $scope.headers = ['ID', 'Title', 'Date', 'Speaker', 'State'];

      $scope.$on('phraseSearched', function(event, args) {
        $scope.loadSpeeches();
      });

      $scope.loadSpeeches = function () {
        if ($scope.current.filters.phrase === null) { return; }
        Speech.where($scope.current.filters).then(function (response) {
          $scope.speeches = response.data;
          $scope.current.count = response.meta.count;
          $scope.current.pages = response.meta.pages;
          console.log($scope.current);
        });
      };

      $scope.$watch('current.filters.page', function (newVal, oldVal) {
        if (oldVal === newVal) { return; }
          console.log($scope.current.page);
          $scope.loadSpeeches();
      }, true);      
      
      $scope.open = function (index) {
        // $scope.currentSpeech = $scope.speeches[index];
        var modalInstance = $modal.open({
          templateUrl: 'views/speech-modal.html',
          controller: 'ModalInstanceCtrl',
          resolve: {
            currentSpeech: function () {
              console.log($scope.speeches[index]);
              return $scope.speeches[index];
            }
          }
        });
      };

    },
    templateUrl: '/views/speech-browser.html',
    link: function(scope, element, attrs) {
      
      // console.log($table);
      // console.log($table.closest('.table-wrapper'));

    }
  };
});