(function() 
{   'use strict';
    var module = angular.module('users');
    module.controller('ResetController'
		, function( $scope
				  , Restangular
				  , gaAuth
				  , $stateParams
				  , gaToast
				  , $state
				  , gaTracking
				  ) 
		{ 	if (gaAuth.loggedIn())
				$state.go('home'); //todo: first we should logout()? But - why? Should we do it programatically? Shouldn't we tell user what is happenning?

			$scope.credentials = { token : $stateParams.token };

			$scope.resetPassword = function() 
			{	Restangular.all('auth/reset-password').post($scope.credentials)
				.then(function(user) 
				{	gaAuth.user = gaAuth.setUser(user);
					gaToast.show('Your password has been successfully updated, you are now logged in');
					gaTracking.eventTrack('Password reset', $scope.credentials.email_);
					$state.go('home');
				});
			};
		});
}());
