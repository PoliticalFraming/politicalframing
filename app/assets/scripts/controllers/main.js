'use strict';

// http://stackoverflow.com/questions/11172269/select-all-and-remove-all-with-chosen-js/11172403#11172403

angular.module('framingApp').controller('MainCtrl', function ($scope, $filter, $templateCache, Speech, State, Analyze, AnalyzeData, Frame) {
    var REMOTE_SERVER = "";
    var LOCAL_SERVER = ""

    var CURRENT_SERVER = LOCAL_SERVER;

    $scope.status_bar = "";
    $scope.page = 1;
    $scope.total = 0;

    // var layoutPlugin = new ngGridLayoutPlugin();

    $scope.currentFilter = {}
    $scope.setCurrentSpeech = function (id) { $scope.currentSpeech = $scope.speeches[id]; };

    $scope.loadSpeeches = function (parameters) {
        if ($scope.selectedTopic == null) return;
        var url = CURRENT_SERVER + '/api/speechtopics/?page=' + $scope.page;
        for (var param in parameters) {
            url += "&" + param + "=" + parameters[param];
        }
        console.log(url);
        Speech.getSpeeches(url).then(function (response) {
            $scope.next = response.data.meta.next;
            $scope.speeches = response.data.objects;
            $scope.total = $filter('number')(response.data.meta.count);
            $scope.status_bar = "Showing " + ($scope.speeches.length === 0 ? "0" : "1") + " to " + $filter('number')($scope.speeches.length) + " of " + $scope.total + " entries";
        });
    }

    $scope.selectedTopic = null;
    $scope.topicsSelectOptions = {
        ajax: {
        url: CURRENT_SERVER + "/api/topics/",
            data: function () {
                return {}; // query params go here
            },
            cache: true,
            results: function (data) { 
                var response = data.objects;
                var newResponse = [];
                for(var i = 0; i < response.length; i++) {
                    newResponse.push({'id': response[i].topic_id, 'text': response[i].phrase});
                }
                return {results: newResponse};
            }
        }
    }

    // Frame.getData("http://localhost:5000/api/frames").then(function (resp) {
    //     var response = resp.data.objects;
    //     var newResponse = [];
    //     for(var i = 0; i < response.length; i++) {
    //         newResponse.push({'id': response[i].frame_id, 'text': response[i].name, 'data': response[i].word_string });
    //     }
    //     $scope.framez = {results: newResponse};
    //     console.log($scope.framez);
    // });

    $scope.selectedFrame = null;
    $scope.frameSelectOptions = {
        ajax: {
            url: CURRENT_SERVER + "/api/frames/",
            data: function () {
                return {}; // query params go here
            },
            cache: true,
            results: function (data) { 
                var response = data.objects;
                var newResponse = [];
                for(var i = 0; i < response.length; i++) {
                    newResponse.push({'id': response[i].frame_id, 'text': response[i].name, 'data': response[i].word_string });
                }
                return {results: newResponse};
            }
        }
    }

    $scope.$watch('selectedFrame', function (newVal, oldVal) {
        if (oldVal == newVal) return;
        $scope.currentFilter.frame = newVal.id;
        $scope.loadSpeeches($scope.currentFilter);
    }, true);    

    // $scope.loadTopics();

    $scope.show_more = function () { $scope.page += 1; $scope.loadSpeeches($scope.currentFilter); }
    $scope.has_more = function () { if ($scope.next != "") return true; }

    $scope.USStateList = State.getStates();

    $scope.selectedStates = [];

    $scope.$watch('selectedStates', function (newVal, oldVal) {
        if (newVal == 0 && oldVal == 0) return;
        if ($scope.selectedStates.length != $scope.USStateList.length && $scope.selectedStates.length != 0) {
            $scope.page = 1;
            angular.extend($scope.currentFilter, {speech__speaker_state__in: newVal.join(",")});
            $scope.loadSpeeches($scope.currentFilter);
        }
        // check to see if this is starting at 0 or becomes 0?
        if ($scope.selectedStates.length == 0) {
            $scope.page = 1;
            delete $scope.currentFilter['speech__speaker_state__in'];
            $scope.loadSpeeches($scope.currentFilter);
        }
    }, true);

    $scope.$watch('selectedTopic', function (newVal, oldVal) {
        if (oldVal == newVal) return;
        $scope.currentFilter.topic = newVal.id;
        $scope.page = 1;
        $scope.loadSpeeches($scope.currentFilter);
        if (!$scope.$$phase) { $scope.$apply(); }
    }, true);

    $scope.selectAllStates = function() {
        $scope.selectedStates = [];
    }

    $scope.filterOptions = {
        filterText: "",
        useExternalFilter: true
    };

    $scope.pagingOptions = {
        pageSizes: [30],
        pageSize: 30,
        currentPage: 1
    };

    $scope.sortInfo = { fields: ['date'], directions: ['asc'] };

    $scope.dateOptions = {
        changeYear: true,
        changeMonth: true,
        yearRange: '1900:-0'
    };

    $scope.mySelections = [];
    $scope.gridOptions = { 
        data: 'speeches',
        columnDefs: [
                {field: 'relevance', displayName: 'ID', width: '10%'}, 
                {field: 'title', displayName: 'Title', width: '61%'}, 
                {field: 'speaker_state', displayName: 'State', width: '7%'},
                {field: 'speaker_party', displayName: 'Party', width: '7%'},
                {field: 'date', displayName: 'Date', width: '15%'}
            ],
        enablePaging: true,
        pagingOptions: $scope.pagingOptions,        
        filterOptions: $scope.filterOptions,
        totalServerItems: 'total',
        useExternalSorting: true,
        keepLastSelected: false,
        multiSelect: false,
        i18n: "en",
        jqueryUITheme: false,
        sortInfo: $scope.sortInfo,
        showFooter: true,
        selectedItems: $scope.mySelections
    };

    $scope.$watch('sortInfo', function (newVal, oldVal) {
        
        for (var col in $scope.sortInfo.columns) {
            var descending = '';
            if ($scope.sortInfo.directions[col] == 'desc')
                descending = '-';
            $scope.currentFilter.ordering = descending + $scope.sortInfo.columns[col].field;
            $scope.page = 1;
            $scope.loadSpeeches($scope.currentFilter);
            if (!$scope.$$phase) { $scope.$apply(); }
        }
    }, true);

    $scope.$watch('pagingOptions', function (newVal, oldVal) {
        if (newVal !== oldVal && newVal.currentPage !== oldVal.currentPage) {
            $scope.page = newVal.currentPage;
            $scope.loadSpeeches($scope.currentFilter);
            if (!$scope.$$phase) { $scope.$apply(); }
        }
    }, true);

    $scope.currentSpeech = null;
    $scope.$watch('mySelections', function (newVal, oldVal) {
        $scope.currentSpeech=newVal[0];
    }, true);

    $scope.$watch('startDateFilter', function (newVal,oldVal){
        if(newVal==null) return;
        $scope.page = 1; 
        // Mon Nov 11 2013 00:00:00 GMT-0800 (PST) 
        var d = new Date(newVal);
        angular.extend($scope.currentFilter, {speech__date__gte: d.getFullYear()+'-'+(d.getMonth()+1)+'-'+d.getDate()});
        $scope.loadSpeeches($scope.currentFilter);

    }, true);

    $scope.$watch('endDateFilter', function (newVal,oldVal){
        if(newVal==null) return;
        $scope.page = 1; 
        // Mon Nov 11 2013 00:00:00 GMT-0800 (PST) 
        var d = new Date(newVal);
        angular.extend($scope.currentFilter, {speech__date__lte: d.getFullYear()+'-'+(d.getMonth()+1)+'-'+d.getDate()});
        $scope.loadSpeeches($scope.currentFilter);

    }, true);

    $scope.analyzeData = null;
    $scope.percentAnalyzed = {};
    
    $scope.analyzeSpeeches = function (parameters, fine) {

        $scope.analyzing = true;
        if ($scope.selectedTopic == null) return;
        
        var url = CURRENT_SERVER + '/analyze?dummy=dummy';
        if (fine == true) url = CURRENT_SERVER + '/analyze2?dummy=dummy';

        for (var param in parameters) {
            url += "&" + param + "=" + parameters[param];
        }
        
        console.log(url);

        Analyze.getData(url).then(function (resp) {
            console.log(CURRENT_SERVER + '/check?task_id=' + resp.data);

            (function pollforAnalyzeData() {
              AnalyzeData.getData(CURRENT_SERVER + '/check?task_id=' + resp.data).then(function (response) {
                if (response.data.state == "SUCCESS") {
                    console.log(response.data);

                    var thedata = response.data;

                    var limit = 100000;    
                    var y = 0;
                    var data = [];
                    var dataSeries1 = { type: "line" };
                    var dataSeries2 = { type: "line" };

                    var dataPoints = [];
                    var theOnes = [];
                    for (var i = 0; i < thedata.frame_plot.dates.length; i++ ) {
                        var dateTime = new Date(thedata.frame_plot.dates[i]);
                        console.log(thedata.frame_plot.dates[i]);
                        console.log(dateTime);
                        dataPoints.push({
                            x: dateTime,
                            y: thedata.frame_plot.ratios[i]
                        });
                        if (i==0 || i==thedata.frame_plot.dates.length-1){
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


                    var chart = new CanvasJS.Chart("chartContainer",
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
                    var dataSeries1 = { type: "line", showInLegend: true, legendText: "Dem Counts" };
                    var dataSeries2 = { type: "line", showInLegend: true, legendText: "Repub Counts"  };
                    var dataSeries3 = { type: "line", showInLegend: true, legendText: "Total Counts"  };

                    var dataPoints1 = [];
                    var dataPoints2 = [];
                    var dataPoints3 = [];
                    for (var i = 0; i < thedata.topic_plot.start_dates.length; i++ ) {
                        var dateTime = new Date(thedata.topic_plot.start_dates[i]);
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

                }
                else {
                    if (response.data.state=="PROGRESS"){
                        $scope.percentAnalyzed = response.data.meta;
                        console.log("pooooooooooohyooooooooo");
                        console.log($scope.percentAnalyzed);
                    }
                
                    console.log(response.data);
                    setTimeout(pollforAnalyzeData, 5000);
                }

              });
            }());

        });

    }

    $scope.navType = 'pills';
    $scope.currentTab = 0;
    $scope.tabs = [
        {heading: "Select Topic", active: true},
        {heading: "Apply Filters", active: false},
        {heading: "Select Frame", active: false},
        {heading: "Analyze", active: false}
    ]

    $scope.percentTabs = ($scope.currentTab+1)/$scope.tabs.length * 100;
    $scope.nextTab = function() {
        if ($scope.currentTab == ($scope.tabs.length - 1)) return;
        $scope.currentTab++;
        $scope.tabs[$scope.currentTab].active = true;
    }
    $scope.prevTab = function() {
        if ($scope.currentTab == 0) return;
        $scope.currentTab--;
        $scope.tabs[$scope.currentTab].active = true;
    }
    
    $scope.updatePercentTab = function(tab) {
        console.log(tab);
        $scope.currentTab = tab;
        $scope.percentTabs = ($scope.currentTab+1)/$scope.tabs.length * 100;

        window.setTimeout(function(){
            $(window).resize();
            $(window).resize();
        }, 1000);

    };

  });
