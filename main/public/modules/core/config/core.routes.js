(function() {
    'use strict';

    var module = angular.module('core');
    module.config(function($stateProvider, $urlRouterProvider) {
        $urlRouterProvider.otherwise('/');

        $stateProvider
            .state('home', {
                url         : '/',
                controller  : 'HomeController',
                templateUrl : '/p/modules/core/home/home.html'
            })
            .state('feedback', {
                url         : '/feedback',
                controller  : 'FeedbackController',
                templateUrl : '/p/modules/core/feedback/feedback.html'
            });
    });
}());
