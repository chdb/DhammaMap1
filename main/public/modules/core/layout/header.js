(function() {
    'use strict';
    var module = angular.module('core');

    module.controller('HeaderController', function($scope, gaAppConfig, gaAuth, $mdSidenav) {
        $scope.cfg = gaAppConfig;
        $scope.auth = gaAuth;
        $scope.user = gaAuth.user;

        $scope.toggleSidenav = function() {
            $mdSidenav('leftSidenav').toggle();
        };
    });

}());
