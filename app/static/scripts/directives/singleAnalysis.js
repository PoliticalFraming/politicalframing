'use strict';

angular.module('framingApp').directive('singleAnalysis', function() {
  return {
    restrict: 'E',
    transclude: true,
    scope: {
      current: '='
    },    
    controller: function ($scope, $modal, $log, $http, Speech, Analysis) {

      // $scope.recomputeAnalysis = function(analysis) {
      //   id = analysis.id;
      //   analyzeSpeeches
      // }

      console.log("poop");

      $scope.$on('graphRequested', function(event, args) {

        console.log("blah");

        Analysis.find($scope.current.filters.id).then(function(data) {
          $scope.currentAnalysis = data;
          $scope.current.filters.phrase = $scope.currentAnalysis.phrase;
          $scope.current.filters.frame = $scope.currentAnalysis.frame;

          var response = {
            data: {
              data: data
            }
          };
          // console.log(data);
          $scope.graphFramePlot(response);
          $scope.graphTopicPlot(response);
        });
      });

      $scope.$on('analysisRequested', function(event, args) {
        $scope.analyzeSpeeches();
      });

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
                // $scope.id = id;
                $scope.currentAnalysis = response.data.data;
                $scope.graphFramePlot(response);
                $scope.graphTopicPlot(response);
                return;
              }
              else if (response.data.meta.state === 'FAILURE') {
                console.log("failed");
                return;
              }
              else {
                if (response.data.meta.state === "PROGRESS") {
                  $scope.current.progress_current = response.data.meta.percent_complete.current;
                  $scope.current.progress_total = response.data.meta.percent_complete.total;
                  $scope.current.progress_percent = response.data.meta.percent_complete.current / response.data.meta.percent_complete.total * 100;
                  $scope.current.stage = response.data.meta.percent_complete.stage;
                }
                setTimeout( function() { pollData(id) }, 2000);
              }
            });
          }
          setTimeout( function() { pollData(id); }, 1000);
        });
      };      
   

      $scope.graphFramePlot = function(response) {

        $scope.Math = window.Math;

        var frame_plot = response.data.data.frame_plot;
        var dataPoints = _.zip(frame_plot.end_dates, frame_plot.ratios, frame_plot.start_dates, frame_plot.end_dates).map(function(a) { return {x: new Date(a[0]), y: $scope.Math.log(a[1]), start_date: a[2], end_date: a[3] } });

        console.log(frame_plot.end_dates);

        var minDate = _.min(_.map(frame_plot.end_dates, function(x) { return new Date(x); }));
        var maxDate = _.max(_.map(frame_plot.end_dates, function(x) { return new Date(x); }));

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
                end_date: e.dataPoint.end_date,
                order: 'frame',
                highlight: 'true'
              }

              Speech.where(dataPointfilters).then(function (response) {
                console.log(response); // response.meta.count; response.meta.pages;
                $scope.speeches = response.data;
                $scope.current.filters.page = 1;
                $scope.current.count = response.meta.count;
              });

            },
            type: "line",
            color: "rgba(0,75,141,0.7)",
            dataPoints: dataPoints
          },
          {
            type: "line",
            color: "red",
            dataPoints: [
              {x: minDate, y: 0},
              {x: maxDate, y: 0}
            ]
          }
        
        ]
        });
        chart.render();
      }

      $scope.graphTopicPlot = function(response) {
        var topic_plot = response.data.data.topic_plot;
        var dataPointsDem = _.zip(topic_plot.end_dates, topic_plot.dem_counts, topic_plot.start_dates, topic_plot.end_dates).map(function(a) { return {x: new Date(a[0]), y: a[1], start_date: a[2], end_date: a[3] } });
        var dataPointsRep = _.zip(topic_plot.end_dates, topic_plot.rep_counts, topic_plot.start_dates, topic_plot.end_dates).map(function(a) { return {x: new Date(a[0]), y: a[1], start_date: a[2], end_date: a[3] } });

        var chart = new CanvasJS.Chart("chartContainer_topic",
        {
            zoomEnabled: true,
            title: { text: topic_plot.title
            },
            axisX:{      
                valueFormatString: "DD-MMM-YYYY",
                labelAngle: -50,
                title: topic_plot.ylabel,
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
                end_date: e.dataPoint.end_date,
                speaker_party: 'D',
                order: 'frame',
                highlight: 'true'
              }

              Speech.where(dataPointfilters).then(function (response) {
                console.log(response); // response.meta.count; response.meta.pages;
                $scope.currentSpeeches = response.data;
                $scope.current.filters.page = 1;
                $scope.current.count = response.meta.count;
              });

            },                
            type: "line",
            showInLegend: true, 
            legendText: "Dem Counts",        
            color: "blue",
            dataPoints: dataPointsDem
        },
          { 
            click: function(e) {

              var dataPointfilters = {
                phrase: $scope.current.filters.phrase,
                frame: $scope.current.filters.frame,
                start_date: e.dataPoint.start_date,
                end_date: e.dataPoint.end_date,
                speaker_party: 'R',
                order: 'frame',
                higlight: 'true'
              }

              Speech.where(dataPointfilters).then(function (response) {
                console.log(response); // response.meta.count; response.meta.pages;
                $scope.currentSpeeches = response.data; 
                $scope.current.filters.page = 1;
                $scope.current.count = response.meta.count;
              });

            },                
            type: "line",
            showInLegend: true, 
            legendText: "Rep Counts",
            color: "red",
            dataPoints: dataPointsRep
        }    
        
        ]
        });
        chart.render();
      }

    },
    templateUrl: '/partials/single-analysis.html',
    link: function(scope, element, attrs) {
      
      // console.log($table);
      // console.log($table.closest('.table-wrapper'));

    }
  };
});