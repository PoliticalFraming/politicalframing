angular.module('framingApp').controller('ModalInstanceCtrl', function ($scope, $modalInstance, currentSpeech) {

  $scope.currentSpeech = currentSpeech;

  $scope.ok = function () {
    $modalInstance.close();
  };

  $scope.cancel = function () {
    $modalInstance.dismiss('cancel');
  };
  
});