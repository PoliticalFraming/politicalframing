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
      $scope.headers = ['ID', 'Title', 'Date', 'Speaker', 'State', 'Party', 'Frame', 'TfIdf', 'Tf', 'TermFreq'];

      $scope.$on('phraseSearched', function(event, args) {
        $scope.current.filters.page = 1;
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

      // This may be inefficient because its watching for all changes to
      // current.filters and then ignoring changes to current.filters.phrase
      // --------------------------------------------------------------------
      // Not sure about the implementation details of watchCollection
      // However, if its possible to have two changes occurr simultaneously
      // Specifically, if the phrase changes and any other filter changes
      // simultaneously -- this won't work.
      $scope.$watchCollection('current.filters', function (newVal, oldVal) {
        if (oldVal === newVal) { return; }
        if (oldVal.phrase !== newVal.phrase) { return; } // phrase must remain the same
        if (newVal.phrase == undefined || newVal.phrase == "" ) { return; } // phrase must exist
        console.log($scope.current.filters.page);
        $scope.loadSpeeches();
      });

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