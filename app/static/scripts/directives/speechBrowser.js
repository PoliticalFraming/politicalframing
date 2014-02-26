'use strict';

angular.module('framingApp').directive('speechBrowser', function() {
  return {
    restrict: 'E',
    transclude: true,
    scope: {
      speeches: '=',
      current: '='
    },    
    controller: function ($scope, $modal, $log) {
      $scope.headers = ['ID', 'Title', 'Date', 'Speaker', 'State'];

      $scope.currentSpeech = null;
      
      $scope.open = function (index) {
        $scope.currentSpeech = $scope.speeches[index];
        var modalInstance = $modal.open({
          templateUrl: 'partials/speech-modal.html',
          controller: 'ModalInstanceCtrl',
          resolve: {
            currentSpeech: function () {
              return $scope.currentSpeech;
            }
          }
        });
      };

    },
    templateUrl: '/partials/speech-browser.html',
    link: function(scope, element, attrs) {
      
      // console.log($table);
      // console.log($table.closest('.table-wrapper'));

    }
  };
});