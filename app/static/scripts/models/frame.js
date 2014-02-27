'use strict';

angular.module('framingApp').factory('Frame', ['ActiveResource', function(ActiveResource) {

  function Frame(data) {
    this.integer('id');
    this.string('name');
    this.string('description');
    this.integer('generation');
    this.string('seed_word');
    this.integer('word_count');
    this.string('word_string');
  }

  Frame.inherits(ActiveResource.Base);
  Frame.api.set('/api');
  Frame.api.indexURL  = '/api/frames/';
  Frame.api.createURL = '/api/frames/';
  Frame.api.showURL   = '/api/frames/:id/';
  Frame.api.updateURL = '/api/frames/:id/';
  Frame.api.deleteURL = '/api/frames/:id/';

  // Frame.primaryKey = 'frame_id';

  return Frame;
}]);