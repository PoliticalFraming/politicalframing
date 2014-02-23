'use strict';

angular.module('framingApp').factory('Frame', ['ActiveResource', function(ActiveResource) {

  function Frame(data) {
    this.integer('frame_id');
    this.string('name');
    this.string('description');
    this.integer('generation');
    this.string('seed_word');
    this.integer('word_count');
    this.string('word_string');
  }

  Frame.inherits(ActiveResource.Base);
  Frame.api.set('/api');

  return Frame;
}]);