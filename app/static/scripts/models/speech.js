'use strict';

angular.module('framingApp').factory('Speech', ['ActiveResource', function(ActiveResource) {

	function Speech(data) {
		this.string('id');
		this.string('bills');
		this.string('biouguide');
		this.string('capitolwords_url');
		this.string('chamber');
		this.string('congress');
		this.string('date');
		this.integer('number');
		this.integer('order');
		this.string('origin_url');
		this.string('pages');
		this.integer('session');
		this.string('speaker_firstname');
		this.string('speaker_lastname');
		this.string('speaker_party');
		this.string('speaker_raw');
		this.string('speaker_state');
		this.string('speaking');
		this.string('document_title');
		this.integer('volume');

		// this.hasMany('topics');
	}

	Speech.inherits(ActiveResource.Base);
	Speech.api.set('/api');
	Speech.api.indexURL  = '/api/speeches/';
	Speech.api.createURL = '/api/speeches/';
	Speech.api.showURL   = '/api/speeches/:id/';
	Speech.api.updateURL = '/api/speeches/:id/';
	Speech.api.deleteURL = '/api/speeches/:id/';

	// Speech.primaryKey = 'speech_id';

	return Speech;
}]);