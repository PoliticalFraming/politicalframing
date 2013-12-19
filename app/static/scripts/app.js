'use strict';

var app = angular.module('framingApp', [
  'ui.select2',
  'ui.date',
  'ui.bootstrap',
  'ngRoute',
  'ngGrid',
  'ngResource',
  'framingServices',
  'framingFilters'
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
    // $locationProvider.html5Mode(true);
  });