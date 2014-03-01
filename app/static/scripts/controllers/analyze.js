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
  
  $scope.graphFramePlot = function(response) {
    var frame_plot = response.data.data.frame_plot;
    var dataPoints = _.zip(frame_plot.end_dates, frame_plot.ratios, frame_plot.start_dates, frame_plot.end_dates).map(function(a) { return {x: new Date(a[0]), y: a[1], start_date: a[2], end_date: a[3] } });

    var chart = new CanvasJS.Chart("chartContainer_frame",
    {
        zoomEnabled: true,
        title: { text: frame_plot.title
        },
        axisX:{      
            valueFormatString: "DD-MMM-YYYY",
            labelAngle: -50,
            title: frame_plot.ylabel,
            includeZero: false
        },
        axisY: {
          // valueFormatString: "#,###"
      },
      data: [
      {
        click: function(e) {

          var dataPointfilters = {
            phrase: $scope.current.filters.phrase,
            frame: $scope.current.filters.frame,
            start_date: e.dataPoint.start_date,
            end_date: e.dataPoint.end_date
          }

          Speech.where(dataPointfilters).then(function (response) {
            console.log(response); // response.meta.count; response.meta.pages;
            $scope.currentSpeeches = response.data; 
          });

        },                
        type: "line",
        color: "rgba(0,75,141,0.7)",
        dataPoints: dataPoints
    }
    
    ]
    });
    chart.render();
  }

  $scope.graphFramePlot = function(response) {
    var frame_plot = response.data.data.frame_plot;
    var dataPoints = _.zip(frame_plot.end_dates, frame_plot.ratios, frame_plot.start_dates, frame_plot.end_dates).map(function(a) { return {x: new Date(a[0]), y: a[1], start_date: a[2], end_date: a[3] } });

    var chart = new CanvasJS.Chart("chartContainer_topic",
    {
        zoomEnabled: true,
        title: { text: frame_plot.title
        },
        axisX:{      
            valueFormatString: "DD-MMM-YYYY",
            labelAngle: -50,
            title: frame_plot.ylabel,
            includeZero: false
        },
        axisY: {
          // valueFormatString: "#,###"
      },
      data: [
      {
        click: function(e) {

          var dataPointfilters = {
            phrase: $scope.current.filters.phrase,
            frame: $scope.current.filters.frame,
            start_date: e.dataPoint.start_date,
            end_date: e.dataPoint.end_date
          }

          Speech.where(dataPointfilters).then(function (response) {
            console.log(response); // response.meta.count; response.meta.pages;
            $scope.currentSpeeches = response.data; 
          });

        },                
        type: "line",
        color: "rgba(0,75,141,0.7)",
        dataPoints: dataPoints
    }
    
    ]
    });
    chart.render();
  }

  /* ==================== ANALYZING SHIT ==================== */

  $scope.analyzeSpeeches = function () {

    // var analysis = Analysis.new($scope.current.filters);
    // analysis.$save();

    $http.post('api/analyses/', $scope.current.filters).then(function(response) {
      console.log(response);
      var id = response.data.data.id;

      function pollData(id) {
        console.log('/api/analyses/' + id + '/');
        $http.get('/api/analyses/' + id + '/').then(function(response) {
          console.log(response);
          console.log(response.data.meta);
          if (response.data.meta.state === 'SUCCESS') {

            console.log("success");
            $scope.analyses = response.data.data;
            $scope.graphFramePlot(response);
            $scope.graphTopicPlot(response);
            console.log(dataPoints);
            // console.log(chart1);

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

