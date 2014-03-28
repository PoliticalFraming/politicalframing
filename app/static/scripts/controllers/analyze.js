// 'use strict';
// // http://stackoverflow.com/questions/11172269/select-all-and-remove-all-with-chosen-js/11172403#11172403

angular.module('framingApp').controller('AnalyzeCtrl', function ($scope, $http, Frame, Speech, State, Analysis) {

  /* ==================== COPY OF BROWSE CONTROLLER ==================== */
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
      phrase: '',
      start_date: null,
      end_date: null,
      highlight: 'true'
    }
  };
  $scope.dateOptions = { changeYear: true, changeMonth: true, yearRange: '1900:-0' };
  $scope.navType = 'pills';

  /* ==================== ANALYZING SHIT ==================== */
  $scope.analyzeSpeeches = function () {
    $http.post('api/analyses/', $scope.current.filters).then(function(response) {
      console.log(response);
      var id = response.data.data.id;
      function pollData(id) {
        console.log('/api/analyses/' + id + '/');
        $http.get('/api/analyses/' + id + '/').then(function(response) {
          console.log(response);
          console.log(response.data.meta.state);
          if (response.data.meta.state === 'SUCCESS') {
            console.log("success");
            $scope.id = id;
            return;
          }
          else if (response.data.meta.state === 'FAILURE') {
            console.log("failed");
            return;
          }
          else {
            if (response.data.meta.state === "PROGRESS") {
              $scope.percentAnalyzed = response.data.meta.percent_complete;
              console.log(response.data.meta.percent_complete.stage);
              console.log(response.data.meta.percent_complete.current + " out of " + response.data.meta.percent_complete.total);
              console.log(response.data.meta.percent_complete.current / response.data.meta.percent_complete.total * 100 + "%");
            }
            setTimeout( function() { pollData(id) }, 2000);
          }
        });
      }
      setTimeout( function() { pollData(id); }, 1000);
    });
  };


});

