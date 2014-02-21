'use strict';

// // http://stackoverflow.com/questions/11172269/select-all-and-remove-all-with-chosen-js/11172403#11172403

angular.module('framingApp').controller('AnalyzeCtrl', function ($scope) {

  /* ==================== TABBING SHIT ==================== */

  $scope.navType = 'pills';
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
    console.log(tab);
    $scope.currentTab = tab;
    $scope.percentTabs = ($scope.currentTab+1)/$scope.tabs.length * 100;
  };

  $scope.analyzeData = null;
  $scope.percentAnalyzed = {};
  
  // $scope.analyzeSpeeches = function (parameters, fine) {
  //   $scope.analyzing = true;
  //   if ($scope.selectedTopic === null) { return; }
  //   var url = '/analyze?dummy=dummy';
  //   if (fine === true) { url = '/analyze2?dummy=dummy'; }
  //   for (var param in parameters) {
  //     url += '&' + param + '=' + parameters[param];
  //   }
  //   console.log(url);
  //   Analyze.getData(url).then(function (resp) {
  //     console.log( '/check?task_id=' + resp.data);
  //     (function pollforAnalyzeData() {
  //       AnalyzeData.getData( '/check?task_id=' + resp.data).then(function (response) {
  //         if (response.data.state === 'SUCCESS') {
  //           console.log(response.data);
  //           var thedata = response.data;
  //           var limit = 100000;    
  //           var y = 0;
  //           var data = [];
  //           var dataSeries1 = { type: 'line' };
  //           var dataSeries2 = { type: 'line' };
  //           var dataPoints = [];
  //           var theOnes = [];
  //           for (var i = 0; i < thedata.frame_plot.dates.length; i++ ) {
  //             var dateTime = new Date(thedata.frame_plot.dates[i]);
  //             console.log(thedata.frame_plot.dates[i]);
  //             console.log(dateTime);
  //             dataPoints.push({
  //               x: dateTime,
  //               y: thedata.frame_plot.ratios[i]
  //             });
  //             if (i==0 || i==thedata.frame_plot.dates.length-1){
  //               theOnes.push({
  //                 x: dateTime,
  //                 y: 1
  //               });
  //             }
  //           }
  //           dataSeries1.dataPoints = dataPoints;
  //           dataSeries2.dataPoints = theOnes;
  //           data.push(dataSeries1);
  //           data.push(dataSeries2);
  //           console.log(data);
  //           var chart = new CanvasJS.Chart('chartContainer',
  //           {
  //             zoomEnabled: true,
  //             title:{ text: thedata.frame_plot.title },
  //             axisX :{ labelAngle: -30 },
  //             axisY :{ includeZero:false, title: thedata.frame_plot.ylabel},
  //             data: data
  //           });
  //           chart.render();
  //           $scope.analyzeData = data;
  //           var limit = 100000;    
  //           var y = 0;
  //           var data = [];
  //           var dataSeries1 = { type: 'line', showInLegend: true, legendText: 'Dem Counts' };
  //           var dataSeries2 = { type: 'line', showInLegend: true, legendText: 'Repub Counts'  };
  //           var dataSeries3 = { type: 'line', showInLegend: true, legendText: 'Total Counts'  };
  //           var dataPoints1 = [];
  //           var dataPoints2 = [];
  //           var dataPoints3 = [];
  //           for (var i = 0; i < thedata.topic_plot.start_dates.length; i++ ) {
  //             var dateTime = new Date(thedata.topic_plot.start_dates[i]);
  //             dataPoints1.push({ x: dateTime, y: thedata.topic_plot.dem_counts[i] });
  //             dataPoints2.push({ x: dateTime, y: thedata.topic_plot.rep_counts[i] });
  //             dataPoints3.push({ x: dateTime, y: thedata.topic_plot.total_counts[i] });
  //           }
  //           dataSeries1.dataPoints = dataPoints1;
  //           dataSeries2.dataPoints = dataPoints2;
  //           dataSeries3.dataPoints = dataPoints3;
  //           data.push(dataSeries1);
  //           data.push(dataSeries2);
  //           data.push(dataSeries3);
  //           var chart = new CanvasJS.Chart("chartContainer2",
  //           {
  //             zoomEnabled: true,
  //             title:{ text: thedata.topic_plot.title },
  //             axisX :{ labelAngle: -30 },
  //             axisY :{ includeZero:false, title: thedata.topic_plot.ylabel},
  //             data: data
  //           });
  //           chart.render();
  //           $scope.analyzeData = data;
  //         }
  //         else {
  //           if (response.data.state=="PROGRESS"){
  //             $scope.percentAnalyzed = response.data.meta;
  //             console.log("pooooooooooohyooooooooo");
  //             console.log($scope.percentAnalyzed);
  //           }
  //           console.log(response.data);
  //           setTimeout(pollforAnalyzeData, 5000);
  //         }
  //       });
  //     }());
  //   });
  // };

});