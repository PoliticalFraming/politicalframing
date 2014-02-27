// 'use strict';
// // http://stackoverflow.com/questions/11172269/select-all-and-remove-all-with-chosen-js/11172403#11172403

angular.module('framingApp').controller('AnalyzeCtrl', function ($scope, $http, Frame, Speech, State, Analysis) {

    // var chart = new CanvasJS.Chart("chartContainer",
    // {
    //     title: {
    //         text: "Date Time Formatting"               
    //     },
    //     axisX:{      
    //         valueFormatString: "DD-MMM" ,
    //         labelAngle: -50
    //     },
    //     axisY: {
    //       valueFormatString: "#,###"
    //   },

    //   data: [
    //   {        
    //     type: "area",
    //     color: "rgba(0,75,141,0.7)",
    //     dataPoints: [

    //     { x: new Date(2012, 06, 23), y: 30 }, 
    //     { x: new Date(2012, 07, 1), y: 10}, 
    //     { x: new Date(2012, 07, 11), y: 21}, 
    //     { x: new Date(2012, 07, 23), y: 50} ,
    //     { x: new Date(2012, 07, 31), y: 75}, 
    //     { x: new Date(2012, 08, 04), y: 10},
    //     { x: new Date(2012, 08, 10), y: 12},
    //     { x: new Date(2012, 08, 13), y: 15}, 
    //     { x: new Date(2012, 08, 16), y: 17}, 
    //     { x: new Date(2012, 08, 18), y: 20}, 
    //     { x: new Date(2012, 08, 21), y: 22}, 
    //     { x: new Date(2012, 08, 24), y: 25}, 
    //     { x: new Date(2012, 08, 26), y: 27}, 
    //     { x: new Date(2012, 08, 28), y: 30} 
    //     ]
    // }
    
    // ]
    // });
    // chart.render();

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
            var frame_plot = response.data.data.frame_plot;
            var dataPoints = _.zip(frame_plot.end_dates, frame_plot.ratios).map(function(a) { return {x: new Date(a[0]), y: a[1]} });

            var chart1 = new CanvasJS.Chart('chartContainer_frame',
            {
              zoomEnabled: true,
              title:{ text: frame_plot.title },
              axisX :{ labelAngle: -30 },
              axisY :{ includeZero:false, title: frame_plot.ylabel},
              data: {
                type: "line",
                color: "rgba(0,75,141,0.7)",
                dataPoints: [
                  { x: new Date(2012, 06, 15), y: 0},       
                  { x: new Date(2012, 06, 18), y: 20 }
                ]
              }
            });
            chart1.render();

            console.log(dataPoints);
            console.log(chart1);

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




            // $scope.analysisUpdated = response.data.data;

            // console.log(response.data.data);

            // $scope.analyzeData = data;
            // var limit = 100000;
            // var y = 0;
            // var data = [];
            // var dataSeries1 = { type: 'line', showInLegend: true, legendText: 'Dem Counts' };
            // var dataSeries2 = { type: 'line', showInLegend: true, legendText: 'Repub Counts'  };
            // var dataSeries3 = { type: 'line', showInLegend: true, legendText: 'Total Counts'  };
            // var dataPoints1 = [];
            // var dataPoints2 = [];
            // var dataPoints3 = [];
            // for (var i = 0; i < thedata.topic_plot.end_dates.length; i++ ) {
            //   var dateTime = new Date(thedata.topic_plot.end_dates[i]);
            //   dataPoints1.push({ x: dateTime, y: thedata.topic_plot.dem_counts[i] });
            //   dataPoints2.push({ x: dateTime, y: thedata.topic_plot.rep_counts[i] });
            //   dataPoints3.push({ x: dateTime, y: thedata.topic_plot.total_counts[i] });
            // }
            // dataSeries1.dataPoints = dataPoints1;
            // dataSeries2.dataPoints = dataPoints2;
            // dataSeries3.dataPoints = dataPoints3;
            // data.push(dataSeries1);
            // data.push(dataSeries2);
            // data.push(dataSeries3);
            // var chart = new CanvasJS.Chart("chartContainer2",
            // {
            //   zoomEnabled: true,
            //   title:{ text: thedata.topic_plot.title },
            //   axisX :{ labelAngle: -30 },
            //   axisY :{ includeZero:false, title: thedata.topic_plot.ylabel},
            //   data: data
            // });
            // chart.render();
            // $scope.analyzeData = data;
            
