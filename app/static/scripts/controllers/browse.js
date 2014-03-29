'use strict';

angular.module('framingApp').controller('BrowseCtrl', function ($scope, $window, Speech, Frame, State) {

  Frame.all().then(function(response) { $scope.frames = response.data; });

});

// http://stackoverflow.com/questions/11172269/select-all-and-remove-all-with-chosen-js/11172403#11172403
