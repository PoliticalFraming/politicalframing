'use strict';

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
      frame: 1,
      phrase: '',
      start_date: null,
      end_date: null,
    }
  };
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
  $scope.dateOptions = { changeYear: true, changeMonth: true, yearRange: '1900:-0' };
  $scope.navType = 'pills';

  /* ==================== TABBING SHIT ==================== */

  $scope.currentTab = 0;
  $scope.tabs = [
    {heading: 'Select Topic', active: true},
    {heading: 'Apply Filters', active: false},
    {heading: 'Select Frame', active: false},
    {heading: 'Analyze', active: false}
  ];
  $scope.percentTabs = ($scope.currentTab+1)/$scope.tabs.length * 100;
  $scope.nextTab = function() {
    if ($scope.currentTab === ($scope.tabs.length - 1)) { return; }
    $scope.currentTab++;
    $scope.tabs[$scope.currentTab].active = true;
  };
  $scope.prevTab = function() {
    if ($scope.currentTab === 0) { return; }
    $scope.currentTab--;
    $scope.tabs[$scope.currentTab].active = true;
  };
  $scope.updatePercentTab = function(tab) {
    // console.log(tab);
    $scope.currentTab = tab;
    $scope.percentTabs = ($scope.currentTab+1)/$scope.tabs.length * 100;
  };

  $scope.analyzeData = null;
  $scope.percentAnalyzed = {};

  /* ==================== GRAPHING SHIT ==================== */
  
  // $scope.graphShit = function(response) {
  //   if (response.data.meta.state === 'SUCCESS') {
  //   }
  //   else {
  //     if (response.data.state=="PROGRESS"){
  //       $scope.percentAnalyzed = response.data.meta;
  //       console.log("pooooooooooohyooooooooo");
  //       console.log($scope.percentAnalyzed);
  //     }
  //     console.log(response.data);
  //     setTimeout(pollforAnalyzeData, 5000);
  //   }
  // }

  /* ==================== ANALYZING SHIT ==================== */

  $scope.analyzeSpeeches = function () {

    var analysis = Analysis.new($scope.current.filters);
    analysis.$save().then(function(response) {

      var id = analysis.id;

      function pollData(id) {
        $http.get('/api/analyses/' + id + '/').then(function(response) {
          console.log(response.data.meta);
          if (response.data.meta.state === 'SUCCESS') {
            console.log("success");
            $scope.analysisUpdated = response.data.data;

            console.log(response.data.data);
            var thedata = response.data.data;
            var limit = 100000;
            var y = 0;
            var data = [];
            var dataSeries1 = { type: 'line' };
            var dataSeries2 = { type: 'line' };
            var dataPoints = [];
            var theOnes = [];
            for (var i = 0; i < thedata.frame_plot.end_dates.length; i++ ) {
              var dateTime = new Date(thedata.frame_plot.end_dates[i]);
              console.log(thedata.frame_plot.end_dates[i]);
              console.log(dateTime);
              dataPoints.push({
                x: dateTime,
                y: thedata.frame_plot.ratios[i]
              });
              if (i==0 || i==thedata.frame_plot.end_dates.length-1){
                theOnes.push({
                  x: dateTime,
                  y: 1
                });
              }
            }
            dataSeries1.dataPoints = dataPoints;
            dataSeries2.dataPoints = theOnes;
            data.push(dataSeries1);
            data.push(dataSeries2);
            console.log(data);
            var chart = new CanvasJS.Chart('chartContainer',
            {
              zoomEnabled: true,
              title:{ text: thedata.frame_plot.title },
              axisX :{ labelAngle: -30 },
              axisY :{ includeZero:false, title: thedata.frame_plot.ylabel},
              data: data
            });
            chart.render();
            $scope.analyzeData = data;
            var limit = 100000;
            var y = 0;
            var data = [];
            var dataSeries1 = { type: 'line', showInLegend: true, legendText: 'Dem Counts' };
            var dataSeries2 = { type: 'line', showInLegend: true, legendText: 'Repub Counts'  };
            var dataSeries3 = { type: 'line', showInLegend: true, legendText: 'Total Counts'  };
            var dataPoints1 = [];
            var dataPoints2 = [];
            var dataPoints3 = [];
            for (var i = 0; i < thedata.topic_plot.end_dates.length; i++ ) {
              var dateTime = new Date(thedata.topic_plot.end_dates[i]);
              dataPoints1.push({ x: dateTime, y: thedata.topic_plot.dem_counts[i] });
              dataPoints2.push({ x: dateTime, y: thedata.topic_plot.rep_counts[i] });
              dataPoints3.push({ x: dateTime, y: thedata.topic_plot.total_counts[i] });
            }
            dataSeries1.dataPoints = dataPoints1;
            dataSeries2.dataPoints = dataPoints2;
            dataSeries3.dataPoints = dataPoints3;
            data.push(dataSeries1);
            data.push(dataSeries2);
            data.push(dataSeries3);
            var chart = new CanvasJS.Chart("chartContainer2",
            {
              zoomEnabled: true,
              title:{ text: thedata.topic_plot.title },
              axisX :{ labelAngle: -30 },
              axisY :{ includeZero:false, title: thedata.topic_plot.ylabel},
              data: data
            });
            chart.render();
            $scope.analyzeData = data;

            return;
          }
          else if (response.data.meta.state === 'FAILURE') {
            console.log("failed");
            return;
          }
          else {

            if (response.data.meta.state === "PROGRESS") {
              $scope.percentAnalyzed = response.data.meta;
              console.log("pooooooooooohyooooooooo");
              console.log($scope.percentAnalyzed);
            }

            setTimeout( function() { pollData(id) }, 2000);
          }
        });
      }

      setTimeout( function() { pollData(id); }, 1000);

    });

  };


});




