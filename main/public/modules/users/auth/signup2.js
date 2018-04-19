(function()
{	'use strict';
    var module = angular.module('users');

    module.controller('Signup2Controller'
	, function( $scope
			  , Restangular
			  , gaAppConfig
			  , gaToast
			  , gaBrowserHistory
			  , gaAuth
			  , _
			  , gaTracking
			  , $state
			  , $stateParams
			  , gaValidators
			  )
    {	if(gaAuth.loggedIn())
        	gaBrowserHistory.back();

		console.log($stateParams);
		Restangular.one('auth/verify', $stateParams.token).get()
		.then( function(data)
		{	var d = angular.fromJson(data);
			if(!!data &&('email_' in d) &&('username' in d))
			{	$scope.credentials.email_ = d.email_;
				$scope.credentials.username = d.username;

				gaToast.show('Please continue!');
			}
			else
			{	//todo blockUI
				gaToast.show('That link is invalid or has expired. Please try again.');
				$state.go('signup');
			}
		});

        $scope.captchaControl = {};
		  //console.log($scope.cfg);
		  //console.log(gaValidators);
		  //
		var v = gaValidators.username_span;
		  //console.log(v)
        $scope.usernameMinLen = v ? v[0] : 0;
        $scope.usernameMaxLen = v ? v[1] : 0;
		  //console.log('uname: '+ $scope.usernameMinLen +' : '+ $scope.usernameMaxLen)

        $scope.signup = function()
        {   $scope.loading = true;
			//console.log('credentials:-');
			//console.log($scope.credentials);
			$scope.credentials.token = $stateParams.token;
			delete $scope.credentials.repeatPwd;
			//console.log($scope.credentials);
            Restangular.all('auth/signup2').post($scope.credentials)
			.then( function()
				{	gaToast.show('Welcome! We have opened your account.');
					$state.go('home');
					// } else
					// {	gaAuth.setUser(user);
						// gaBrowserHistory.back();
					// }
					gaTracking.eventTrack('Signup', $scope.credentials.email_);
				}
			, function() // promise rejected
				{	console.log('signup promise rejected');
					_.attempt($scope.captchaControl.reset);
				}
			);
        };
    });
}());
