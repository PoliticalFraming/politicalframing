'use strict';

// http://stackoverflow.com/questions/11172269/select-all-and-remove-all-with-chosen-js/11172403#11172403

angular.module('framingApp').controller('AnalysisViewerCtrl', function ($scope, $window, $routeParams, Frame, Analysis, Speech) {

  Analysis.find($routeParams.id).then(function(data) {
    $scope.currentAnalysis = data;
    // $scope.currentAnalysis
    console.log($scope.currentAnalysis);
    console.log($scope.currentAnalysis.frame);
  	var response = {
  		data: {
  			data: data
  		}
  	};
  	// console.log(data);
		$scope.graphFramePlot(response);
		$scope.graphTopicPlot(response);
  });  

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
            phrase: $scope.currentAnalysis.phrase,
            frame: $scope.currentAnalysis.frame,
            start_date: e.dataPoint.start_date,
            end_date: e.dataPoint.end_date,
            order: 'frame',
            highlight: 'true'
          }

          Speech.where(dataPointfilters).then(function (response) {
            console.log(response); // response.meta.count; response.meta.pages;
            $scope.currentSpeeches = response.data; 
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
            phrase: $scope.currentAnalysis.phrase,
            frame: $scope.currentAnalysis.frame,
            start_date: e.dataPoint.start_date,
            end_date: e.dataPoint.end_date,
            speaker_party: 'D',
            order: 'frame',
            highlight: 'true'
          }

          Speech.where(dataPointfilters).then(function (response) {
            console.log(response); // response.meta.count; response.meta.pages;
            $scope.currentSpeeches = response.data; 
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
            phrase: $scope.currentAnalysis.phrase,
            frame: $scope.currentAnalysis.frame,
            start_date: e.dataPoint.start_date,
            end_date: e.dataPoint.end_date,
            speaker_party: 'R',
            order: 'frame',
            higlight: 'true'
          }

          Speech.where(dataPointfilters).then(function (response) {
            console.log(response); // response.meta.count; response.meta.pages;
            $scope.currentSpeeches = response.data; 
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

  // Frame.all().then(function(response) { $scope.frames = response.data; });
  // Analysis.all().then(function(response) { $scope.analyses = response.data; });

  // $scope.updateAnalysis = function(id) {
  	
  // }

});