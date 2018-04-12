(function() 
{	'use strict';

    var module = angular.module('core');
    module.constant('_', _);

    module.config(function	( $locationProvider
							, RestangularProvider
							, $mdThemingProvider
							, blockUIConfig
							) 
    {	$locationProvider.html5Mode(false);
		//var authToken = localStorage.getItem('dwsession');
		
        RestangularProvider
            .setBaseUrl('/api/v1')
            .setRestangularFields({ id : 'uid' }) //used in calls to Restangular.one(...).get()
			.setDefaultHeaders({ Accept: 'application/json, text/plain'})
			;
		
		console.log('xzzzzzzzzzzzx');
        $mdThemingProvider.theme('default')
            .primaryPalette('indigo')
            .accentPalette('blue');
		
		blockUIConfig.template ='<div id="blockUIDiv"></div>';
    });
	module.value('gaAdminCfg', {});
	
	module.factory('gaBlockSpin', function($timeout, blockUI) 
	{	console.log('spinner = ');
	
		var spinOpts =  { lines		: 17		// The number of lines to draw
						, length	: 28		// The length of each line
						, width		: 38		// The line thickness
						, radius	: 36		// The radius of the inner circle
						, scale		: 1			// Scales overall size of the spinner
						, corners	: 1			// Corner roundness(0..1)
						, color		:'#0f0'		// #rgb or #rrggbb or array of colors
						, opacity	: 0			// Opacity of the lines
						, rotate	: 32		// The rotation offset
						, direction	: -1		// 1: clockwise, -1: counterclockwise
						, speed		: 0.5		// Rounds per second
						, trail		: 100		// Afterglow percentage
						, fps		: 20		// Frames per second when using setTimeout() as a fallback for CSS
						, zIndex	: 2e9		// The z-index(defaults to 2000000000)
						, className	:'spinner'	// The CSS class to assign to the spinner
						, top		:'54%'		// Top position relative to parent
						, left		:'47%'		// Left position relative to parent
						, shadow	: false		// Whether to render a shadow
						, hwaccel	: false		// Whether to use hardware acceleration
						, position	:'absolute'	// Element positioning
						};		
		var spinner = new Spinner(spinOpts);
		
		return { start	: function(caller, delay) 	
						{ 	console.log('wait: ' + delay);
							blockUI.start();
							var target = document.getElementById('blockUIDiv');
							spinner.spin(target);
							$timeout(caller, delay);	
						}
				, stop	: function(caller, delay) 	
						{ 	blockUI.stop();
							spinner.stop();
						}
				};
	});
		// { user 	  : gaAuthUser
		// , loggedIn: function() 	
					// { 	return !! u.user; 
					// }
		// , is_admin: function() 	
					// { 	if(! u.user)
							// return false;
						// if(u.user.isAdmin_ === undefined) 
							// console.log('unknown admin status!', u.user);
						//console.log(' admin status: ', u.user.isAdmin_);
						// return u.user.isAdmin_
					// }
		// , setUser : function(user) 
					// { 	u.user = Restangular.restangularizeElement(null, user, 'users');
						// u.user.avatarUrl = function(size)
						// {	console.log(u);
							// return '//gravatar.com/avatar/'+u.hash+'?d=identicon&r=x&s='+size;
						// }
						
						// localStorage.setItem('dwsession', authToken);
						
						// return u.user;
					// }
		// , authProviderName : function(authId)
					// {	if(authId[2] !== ':')
							// throw "invalid authId: missing colon"
						// var shortname = authId.substr(0, 3);
						// if(! shortname in gaAuthNames)
							// throw "missing shortname in authNames";
						// return gaAuthNames[shortname];
					// }
		// , avatarUrl : function(user, size)
					// {	return '//gravatar.com/avatar/'+user.hash+'?d=identicon&r=x&s='+size;
					// }
		// };
		// return u;  
    // });

	
    module.run(function(Restangular, gaToast, $state, $rootScope, $timeout, gaFlashMessages, _,
                       gaAppConfig, gaAuth, blockUI, gaBrowserHistory
					 ,  gaAuthUser	  
					  // gaAppConfig
					  , gaAuthNames
					  , gaValidators
					 //  gaFlashMessages
					   
					   ) 
    {	var loadingPromise;
        var endLoading = function() 
        {	$timeout.cancel(loadingPromise);
            $rootScope.isLoading = false;
			blockUI.stop();// Unblock the user interface
        };
		$rootScope.cfg = gaAppConfig;
		
        if(gaAuth.loggedIn()) 
        	gaAuth.user = Restangular.restangularizeElement(null, gaAuth.user, 'users');

        gaBrowserHistory.init();

        Restangular.setErrorInterceptor(function(res) 
        {	endLoading();
           /* if(res.status === 401) 
			{	gaToast.show('Please sign in first.');
				//$state.go('signin');
				// $location.path('/signin'); 
            } else 
			*/
			if(res.status === 403) 
            {	gaToast.show('No access to that page!');
                //$timeout(function() { $state.go('signin'); }, 1000)
				//$location.path('/signin'); 
			} else if(res.status === 404) 
            {	gaToast.show('Sorry, but that page does not exist.');
                gaBrowserHistory.back();
            } else 
			{	if(res.data)
				{	//console.log('error interceptor:');
					//console.log(res);
					if(res.data.message)
						gaToast.show(res.data.message);
					else
						gaToast.show(res.data);
				}
				else 
				{	gaToast.show('Sorry, I failed so badly I can\'t even describe it.  :(' );
					console.log('In the following item, check the structure of the error msg and accordingly adjust error handler at core.config.js');
					console.log(res);
				}
            }
            return true;
        });

        /* Restangular.addRequestInterceptor(
		    function(element, operation, path, url, headers, params, httpConfig) 
            {	var defer = $q.defer();
				defer.reject();
				Timeout is promise already rejected.
				httpConfig.timeout = defer;
				return 	{ element	: element
						, headers	: headers
						, params	: params
						, httpConfig: httpConfig
						};
            }
		 ); */
		
        Restangular.addRequestInterceptor(function(element, operation) 
        {	// This is just a loading indicator, so we don't have to do it in every controller.
            // It's mainly used to disable submit buttons, when request is sent with a little delay so disabling buttons looks more smoothly
            loadingPromise = $timeout(function() 
				{	$rootScope.isLoading = true;
				}
				, 500);

            // Flask responds with error, when DELETE method contains body, so we remove it
            if(operation === 'remove') 
            	return undefined;
            return element;
        });
		
        Restangular.addResponseInterceptor(function(data) 
        {	endLoading();
            return data;
        });

        /** This interceptor extracts meta data from list response
         *  meta data can be:
         *      cursor - ndb Cursor used for pagination
         *      totalCount - total count of items
         *      more - whether datastore contains more items, for pagination
         */
        Restangular.addResponseInterceptor(function(data, operation) 
        {	if(operation === 'getList') 
			{	var d = data.list;
				d.meta = data.meta;
				return d;
            } 
			return data;
        });
		
		console.log('user : '  		+gaAuthUser		);
		console.log('config : '		+gaAppConfig	);
		console.log('authNames : '	+gaAuthNames	);
		console.log('validators : '	+gaValidators	);
		console.log('flashMessages : '+gaFlashMessages);
		//console.log(' : '+);

        // If there are FlashMessages from server, toast will display them
        if(!_.isEmpty(gaFlashMessages)) 
		{	console.log(gaFlashMessages);
        	$timeout(function() 
				{ gaToast.show( gaFlashMessages[0] 
							  , { delay : 20000 }
							  );
				}
				, 1000);
		}
		
        $rootScope.$on('$stateChangeError', function() 
        {	gaToast.show('Sorry, there was a error while loading that page.');
        });

        // Fires when content is scrolled to bottom. This is defined in base.html
        $rootScope.mainContentScrolled = function() 
        {	$rootScope.$broadcast('mainContentScrolled');
        };

    });

}());
