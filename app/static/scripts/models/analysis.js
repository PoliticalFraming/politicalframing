'use strict';

angular.module('framingApp').factory('Analysis', ['ActiveResource', function(ActiveResource) {

  function Analysis(data) {
    this.integer('analysis_id');
    this.string('frame_plot');
    this.string('topic_plot');
  }

  Analysis.inherits(ActiveResource.Base);
  Analysis.api.set('/api');

  return Analysis;
}]);