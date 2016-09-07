(function() {
    'use strict';
    var module = angular.module('users');

    module.controller('ResetController', function($scope, Restangular, gaAuth, $stateParams, gaToast,
                                                  $state, gaTracking) {

        if (gaAuth.loggedIn()) {
            $state.go('home');
        }

        $scope.credentials = {
            token : $stateParams.token
        };

        $scope.resetPassword = function() {
            Restangular.all('auth/reset').post($scope.credentials).then(function(user) {
                gaAuth.user = gaAuth.setUser(user);
                gaToast.show('Your password has been successfully updated, you are now logged in');
                gaTracking.eventTrack('Password reset', $scope.credentials.email);
                $state.go('home');
            });
        };
    });

}());
