(function() {
    'use strict';
    var module = angular.module('users');

    module.controller('SigninController', function($scope, Restangular, gaAppConfig, gaAuth, gaBrowserHistory,
                                                   gaToast, gaTracking) {

        if (gaAuth.loggedIn()) {
            gaBrowserHistory.back();
        }

        var ctrl = this;
        $scope.cfg = gaAppConfig;
        $scope.captchaControl = {};

        $scope.signin = function() {
            Restangular.all('auth/signin').post($scope.credentials).then(function(user) {
                var category;
                if (!user.isVerified_) {
                    gaToast.show('Your email isn\'t verified yet.', {
                        action : 'Resend Email',
                        delay  : 5000
                    }).then(ctrl.resendEmail);
                    category = 'unverified';
                } else if (!user.isActive_) {
                    gaToast.show('Your account has been blocked. Please contact administrators to find out why.');
                    category = 'blocked';
                } else {
                    gaAuth.setUser(user);
                    gaBrowserHistory.back();
                    category = 'success';
                }
                gaTracking.eventTrack('Signin', $scope.credentials.login, category);
            }).finally(function() {
                _.attempt($scope.captchaControl.reset);
            });
        };

        ctrl.resendEmail = function() {
            Restangular.all('auth/resend-verification').post($scope.credentials).then(function() {
                gaToast.show('Another activation email has been sent to you. Please open the email and click the link');
            });
        };

    });

}());
