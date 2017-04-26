(function() 
{	'use strict';
    var module = angular.module('users');

    module.controller('SigninController'
					 , function($scope, $element, Restangular, gaAppConfig
							   , gaAuth, gaBrowserHistory, gaToast, gaTracking, gaBlockSpin ) 
	{  	if (gaAuth.loggedIn()) 
        {	gaBrowserHistory.back();
        }

        var ctrl = this;
        //$scope.cfg = gaAppConfig;
        $scope.captchaControl = {};

        $scope.signin = function() 
        {	Restangular
			.all('auth/log-in')
			.post($scope.credentials)
			.then( function(resp)
			{	if (!!resp)			
				{	if ('delay'in resp)//wait & try again 
					 	gaBlockSpin.start($scope.signin, resp.delay);
					else 
					{	gaBlockSpin.stop();// Unblock the user interface
						var category;
						if (resp.unVerified) 
						{	var loginId = $scope.credentials.loginId;
							if (loginId.indexOf('@') !== -1)
							{	$scope.unVerified = resp.unVerified;
								$scope.unVerified.ema = loginId;
								var params =  {	action :'Resend Email'
											  ,	delay  : 5000
											  };
								gaToast.show('Your email isn\'t verified yet.', params)
									   .then(ctrl.resendEmail);
							}
							category = 'unverified';
						}
						else if ('user'in resp)// redirect:	window.location = resp.nextUrl;	
						{	//console.log('user', user);
							if (! resp.user.isActive_) 
							{	gaToast.show('Your account has been blocked. Please contact administrators to find out why.');
								category = 'blocked';
							}
							else 
							{	gaAuth.setUser(resp.user);
								gaBrowserHistory.back();
								category = 'success';
							}
							gaTracking.eventTrack('Signin', $scope.credentials.loginId, category);
					}	}
				}
				else gaToast.show('Wrong email or wrong password.');
            })
			.finally( function() 
            {	_.attempt($scope.captchaControl.reset);
            });
        };

        ctrl.resendEmail = function() 
        {	Restangular
			.all('auth/resend-signup')
			.post($scope.unVerified)
			.then(function() 
            {	gaToast.show('Another activation email has been sent to you. Please open the email and click the link');
            });
        };
    });
}());
