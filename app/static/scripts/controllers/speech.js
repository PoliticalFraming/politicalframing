'use strict';

// Please remember the distinction between a service and a factory in AngularJS.
// http://stackoverflow.com/questions/15666048/angular-js-service-vs-provider-vs-factory

// Service: you will be provided with an instance of the function, i.e. new FunctionYouPassedToService()
// Factory: you will be provided the value that is returned by invoking the function reference

angular.module('framingApp').controller('SpeechCtrl', function ($scope, SpeechModel) {
	$scope.SpeechModel = SpeechModel;
	$scope.fetch = function() {
		SpeechModel.fetch();
	};
	$scope.fetch();
});

angular.module('framingApp').controller('FrameCtrl', function ($scope, SpeechModel) {
	$scope.SpeechModel = SpeechModel;

});

angular.module('framingApp').service('SpeechModel', function(SpeechResource) {
	var Speech = function() {
		this.data = { id: null, token: 'token_default_value' };
	};
	Speech.prototype.fetch = function(page){
		var self = this;
		SpeechResource.query(function(result){
			self.data = result.data;
		});
	};
	return new Speech();
});

angular.module('framingApp').factory('SpeechResource', function($resource){
	var url = '/api/speechtopics';
	var params = {
		output: 'json',
		callback: 'JSON_CALLBACK'
	};
	var options = {
		query: { method: 'JSONP' }
	};
	return $resource(url, params, options);
});