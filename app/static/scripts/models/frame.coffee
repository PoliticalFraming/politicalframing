'use strict';

angular.module('framingApp').
  
  factory 'Frame', ['ActiveResource', (ActiveResource) -> 

    Frame = (data) ->
        this.integer 'id'
        this.string 'name'
        this.string 'description'
        this.integer 'generation'
        this.string 'weed_word'
        this.integer 'word_count'
        this.string 'word_string'
        this

    Frame.inherits ActiveResource.Base
    Frame.api.set '/api'
    Frame.api.indexURL = '/api/frames/'
    Frame.api.createURL = '/api/frames/'
    Frame.api.showURL = '/api/frames/'
    Frame.api.updateURL = '/api/frames/'
    Frame.api.deleteURL = '/api/frames/'
  ]