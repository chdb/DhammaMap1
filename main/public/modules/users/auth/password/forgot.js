(function() {
    'use strict';
    var module = angular.module('users');

    module.controller('ForgotController', function($scope, Restangular, gaToast, gaBrowserHistory, gaTracking) {

        $scope.askForNewPassword = function() {
            Restangular.all('auth/forgot-password').post($scope.credentials)
			.then(function()
			{
                gaToast.show('Please check your email for instructions to reset your password.');
                gaTracking.eventTrack('Forgot password', $scope.credentials.email_);
                gaBrowserHistory.back();
            });
        };
    });

}());
