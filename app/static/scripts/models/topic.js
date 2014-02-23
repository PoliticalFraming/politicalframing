'use strict';

angular.module('framingApp').factory('Topic', ['ActiveResource', function(ActiveResource) {

  function Topic(data) {
    this.integer('topic_id');
    this.string('phrase');

    // this.hasMany('speeches');
  }

  Topic.inherits(ActiveResource.Base);
  Topic.api.set('/api');

  return Topic;
}]);