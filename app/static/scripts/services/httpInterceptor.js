'use strict';

angular.module('framingApp').factory('myHttpInterceptor', function($q) {
  return {
    'response': function(response) {
      if (response.config.url.search('/api/') !== -1) {
        console.log(response.config.url);
        // console.log(response.data);
        // console.log(response.headers());
      }
      return response || $q.when(response);
    },

    'responseError': function(rejection) {
      if (canRecover(rejection)) { return responseOrNewPromise; }
      return $q.reject(rejection);
    }
  };
});

angular.module('framingApp').config(['$httpProvider',function($httpProvider) {
  $httpProvider.interceptors.push('myHttpInterceptor');
}]);
