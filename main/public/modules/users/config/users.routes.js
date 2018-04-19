(function() {
	'use strict';

	var module = angular.module('users');
	module.config(function($stateProvider)
	{	$stateProvider
		.state( 'signin'
			  , { url		  : '/login'
				, controller  : 'SigninController'
				, templateUrl : '/p/modules/users/auth/signin.html'
				, data		  : { signedOutOnly : true }
				})
		.state( 'signup'
			  , { url		  : '/signup'
				, controller  : 'SignupController'
				, templateUrl : '/p/modules/users/auth/signup.html'
				, data		  : { signedOutOnly : true }
				})
		.state( 'verify'
			  , { url		  : '/verify/:token'
				, controller  : 'Signup2Controller'
				, templateUrl : '/p/modules/users/auth/signup2.html'
				, data		  : { signedOutOnly : true }
				})
		.state( 'signup2'
			  , { url		  : '/signup2/:token'
				, controller  : 'Signup2Controller'
				, templateUrl : '/p/modules/users/auth/signup2.html'
				, data		  : { signedOutOnly : true }
				})
		.state( 'signout'
			  , { url		  : '/logout'
				, controller  : function(Restangular, gaAuth, $state,  gaAdminCfg)
							  {	Restangular.all('auth/log-out').post()
								.then(function()
								{	gaAuth.user = false;
									gaAdminCfg = {};
									//_.assignDelete(gaAppConfig, appConfig);
									$state.go('home');
								});}
				})
		.state( 'forgot'
			  , { url		  : '/password/forgot'
				, controller  : 'ForgotController'
				, templateUrl : '/p/modules/users/auth/password/forgot.html'
				, data		  : { signedOutOnly : true }
				})
		.state( 'reset'
			  , { url		  : '/password/reset/:token'
				, controller  : 'ResetController'
				, templateUrl : '/p/modules/users/auth/password/reset.html'
				, data		  : { signedOutOnly : true }
				})
		.state( 'profile'
			  , { abstract	: true
				, url		: '/user/:username'
				, views		: { '': { templateUrl : '/p/modules/users/profile/profile.html'
									, controller  : 'ProfileController'
				}}})
		.state( 'profile.view'
			  , { url		  : ''
				, templateUrl : '/p/modules/users/profile/profile-view.html'
				})
		.state( 'profile.edit'
			  , { url		  : '/edit'
				, controller  : 'ProfileEditController'
				, templateUrl : '/p/modules/users/profile/profile-edit.html'
				})
		.state( 'profile.password'
			  , { url		  : '/password'
				, controller  : 'ProfilePasswordController'
				, templateUrl : '/p/modules/users/profile/profile-password.html'
				});
	});
}());
