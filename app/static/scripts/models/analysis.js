'use strict';

angular.module('framingApp').factory('Analysis', ['ActiveResource', function(ActiveResource) {

  function Analysis(data) {
    this.integer('id');
    this.integer('frame');
    // this.hasOne('frame', { provider: 'Frame', foreign_key: 'id'} );
    this.string('start_date');
    this.string('end_date');
    this.string('phrase');
    this.string('frame_plot');
    this.string('topic_plot');
  }

  Analysis.inherits(ActiveResource.Base);

  Analysis.api.set('/api/');

  Analysis.api.indexURL  = '/api/analyses/';
  Analysis.api.createURL = '/api/analyses/';
  Analysis.api.showURL   = '/api/analyses/:id/';
  Analysis.api.updateURL = '/api/analyses/:id/';
  Analysis.api.deleteURL = '/api/analyses/:id/';

  // Analysis.primaryKey = 'analysis_id';

  return Analysis;
}]);