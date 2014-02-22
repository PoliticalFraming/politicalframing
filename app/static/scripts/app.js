'use strict';

var app = angular.module('framingApp', [
  'ui.date',
  'ui.bootstrap',
  'ngRoute',
  'ngResource',
  'framingServices',
  'framingFilters',
  'ActiveResource',
  'localytics.directives'
  ])
  .config(function ($routeProvider, $locationProvider, $httpProvider) {
    $routeProvider
      .when('/', {
        templateUrl: 'views/home.html',
      })
      .when('/analyze', {
        templateUrl: 'views/analyze.html',
        controller: 'MainCtrl'
      })
      .when('/browse', {
        templateUrl: 'views/browse.html',
        controller: 'MainCtrl'
      })
      .otherwise({
        redirectTo: '/'
      });
    $locationProvider.html5Mode(true);
  });

angular.module('framingApp').run(function($rootScope, $location) {
  $rootScope.location = $location;
});