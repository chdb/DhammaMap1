(function() {
    'use strict';

    var module = angular.module('admin');
    module.config(function($stateProvider) {
        $stateProvider
            .state('admin', {
                url         : '/admin',
                abstract    : true,
                controller  : 'AdminController',
                templateUrl : '/p/modules/admin/layout/admin.html'
            })
            .state('admin.appConfig', {
                url         : '/config',
                controller  : 'AdminAppConfigController',
                templateUrl : '/p/modules/admin/app-config/app-config.html'
            })
            .state('admin.users', {
                url         : '/users',
                controller  : 'UsersController',
 //               controllerAs: 'UserLister',
                templateUrl : '/p/modules/users/users-list/users.html'
			});
    });
}());
