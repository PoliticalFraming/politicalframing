// 'use strict';

// // Please remember the distinction between a service and a factory in AngularJS.
// // http://stackoverflow.com/questions/15666048/angular-js-service-vs-provider-vs-factory

// // Service: you will be provided with an instance of the function, i.e. new FunctionYouPassedToService()
// // Factory: you will be provided the value that is returned by invoking the function reference

// angular.module('framingApp').controller('SpeechCtrl', function ($scope, SpeechModel) {
// 	$scope.SpeechModel = SpeechModel;
// 	$scope.fetch = function() {
// 		SpeechModel.fetch();
// 	};
// 	$scope.fetch();
// });

// angular.module('framingApp').controller('FrameCtrl', function ($scope, SpeechModel) {
// 	$scope.SpeechModel = SpeechModel;

// });

// angular.module('framingApp').service('SpeechModel', function(SpeechResource) {
// 	var Speech = function() {
// 		this.data = { id: null, token: 'token_default_value' };
// 	};
// 	Speech.prototype.fetch = function(page){
// 		var self = this;
// 		SpeechResource.query(function(result){
// 			self.data = result.data;
// 		});
// 	};
// 	return new Speech();
// });

// angular.module('framingApp').factory('SpeechResource', function($resource){
// 	var url = '/api/speechtopics';
// 	var params = {
// 		output: 'json',
// 		callback: 'JSON_CALLBACK'
// 	};
// 	var options = {
// 		query: { method: 'JSONP' }
// 	};
// 	return $resource(url, params, options);
// });


  // $scope.filterOptions = { filterText: '', useExternalFilter: true };
  // $scope.pagingOptions = { pageSizes: [20], pageSize: 20, currentPage: 1 };
  // $scope.sortInfo = { fields: ['date'], directions: ['asc'] };
  // $scope.selectedSpeeches = [];
  // $scope.gridOptions = {
  //   data: 'speeches',
  //   columnDefs: [
  //     {field: 'id', displayName: 'ID', width: '10%'},
  //     {field: 'title', displayName: 'Title', width: '61%'},
  //     {field: 'speaker_state', displayName: 'State', width: '7%'},
  //     {field: 'speaker_party', displayName: 'Party', width: '7%'},
  //     {field: 'date', displayName: 'Date', width: '15%'}
  //   ],
  //   enablePaging: true,
  //   pagingOptions: $scope.pagingOptions,
  //   filterOptions: $scope.filterOptions,
  //   totalServerItems: 'total',
  //   useExternalSorting: true,
  //   keepLastSelected: false,
  //   multiSelect: false,
  //   i18n: 'en',
  //   jqueryUITheme: false,
  //   sortInfo: $scope.sortInfo,
  //   showFooter: true,
  //   selectedItems: $scope.selectedSpeeches
  // };

  // // http://stackoverflow.com/a/17864150
  // $scope.$watch('sortInfo', function (newVal, oldVal) {
  //   console.log(oldVal);
  //   console.log(newVal);
  //   // for (var col in $scope.sortInfo.columns) {
  //   //   var descending = '';
  //   //   if ($scope.sortInfo.directions[col] === 'desc') { descending = '-'; }
  //   //   $scope.currentFilter.ordering = descending + $scope.sortInfo.columns[col].field;
  //   //   $scope.page = 1;
  //   //   $scope.loadSpeeches($scope.currentFilter);
  //   //   if (!$scope.$$phase) { $scope.$apply(); }
  //   // }
  // }, true);

  // $scope.$watch('pagingOptions', function (newVal, oldVal) {
  //   if (newVal !== oldVal && newVal.currentPage !== oldVal.currentPage) {
  //     console.log("page" + newVal.currentPage);
  //     $scope.currentFilter.page = newVal.currentPage;
  //     $scope.loadSpeeches();
  //     // if (!$scope.$$phase) { $scope.$apply(); }
  //   }
  // }, true);