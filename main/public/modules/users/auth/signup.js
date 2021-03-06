(function() {
    'use strict';
    var module = angular.module('users');

    module.controller('SignupController', function($scope, Restangular, gaAppConfig, gaToast, gaBrowserHistory,
                                                   gaAuth, _, gaTracking, $state, gaValidators) {
        if (gaAuth.loggedIn()) {
            gaBrowserHistory.back();
        }

        $scope.cfg = gaAppConfig;
		  
        $scope.captchaControl = {};
		  //console.log($scope.cfg);
		  //console.log(gaValidators);
		  //
		  var v = gaValidators.username_span;
		  //console.log(v)
        $scope.usernameMinLen = v ? v[0] : 0;
        $scope.usernameMaxLen = v ? v[1] : 0;
		  //console.log('uname: '+ $scope.usernameMinLen +' : '+ $scope.usernameMaxLen)

        $scope.signup = function() {
            $scope.loading = true;
            Restangular.all('auth/signup').post($scope.credentials).then(function(user) {
                if ($scope.cfg.verify_email) {//jscs:disable requireCamelCaseOrUpperCaseIdentifiers
                    gaToast.show('Your account has been created! Please verify your email');
                    $state.go('home');
                } else {
                    gaAuth.setUser(user);
                    gaBrowserHistory.back();
                }
                gaTracking.eventTrack('Signup', $scope.credentials.email);
            }, function() {
                _.attempt($scope.captchaControl.reset);
            });
        };
    });
}());
