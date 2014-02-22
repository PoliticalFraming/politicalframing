'use strict';

angular.module('framingApp').directive('speechBrowser', function() {
  return {
    restrict: 'E',
    transclude: true,
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

        // modalInstance.result.then(function (selectedItem) {
        //   $scope.selected = selectedItem;
        // }, function () {
        //   $log.info('Modal dismissed at: ' + new Date());
        // });

      };

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