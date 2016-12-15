(function() 
{	'use strict';
    var module = angular.module('users');

    module.controller('SigninController'
					 , function($scope, $timeout, Restangular, gaAppConfig
							   , gaAuth, gaBrowserHistory, gaToast, gaTracking) 
	{  	if (gaAuth.loggedIn()) 
        {	gaBrowserHistory.back();
        }

        var ctrl = this;
        $scope.cfg = gaAppConfig;
        $scope.captchaControl = {};

        $scope.signin = function() 
        {	Restangular.all('auth/signin').post($scope.credentials)
			.then( function(resp)
			{				
				if (resp.delay)//wait & try again 
				/*todo 	move this block to response interceptor
							 Restangular.addResponseInterceptor(
								function(data, operation) 
								{	if (data.delay) 
									...
								} )
						add code to disable the app 
						and grey it out 
						and display wait cursor
						and? wait message 
				*/
				{	//logTS('wait: ' + resp.delay);
					$timeout ($scope.signin, resp.delay);	
				}
				else if (resp.user)// redirect:	window.location = resp.nextUrl;	
				{	var category;
					//console.log('user', user);
					if (! resp.user.isVerified_) 
					{	gaToast.show('Your email isn\'t verified yet.', 
						{	action : 'Resend Email',
							delay  : 5000
						}).then(ctrl.resendEmail);
						category = 'unverified';
					} else if (! resp.user.isActive_) 
					{	gaToast.show('Your account has been blocked. Please contact administrators to find out why.');
						category = 'blocked';
					} else 
					{	gaAuth.setUser(resp.user);
						gaBrowserHistory.back();
						category = 'success';
					}
					gaTracking.eventTrack('Signin', $scope.credentials.loginId, category);
				}
            }).finally(function() 
            {	_.attempt($scope.captchaControl.reset);
            });
        };

        ctrl.resendEmail = function() 
        {	Restangular.all('auth/resend-verification').post($scope.credentials).then(function() 
            {	gaToast.show('Another activation email has been sent to you. Please open the email and click the link');
            });
        };

    });

}());
