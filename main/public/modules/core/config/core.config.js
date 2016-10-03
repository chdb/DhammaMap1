(function() 
{	'use strict';

    var module = angular.module('core');
    module.constant('_', _);

    module.config(function($locationProvider, RestangularProvider, $mdThemingProvider) 
    {	$locationProvider.html5Mode(false);

        RestangularProvider
            .setBaseUrl('/api/v1')
            .setRestangularFields( { id : 'key' } );

        $mdThemingProvider.theme('default')
            .primaryPalette('indigo')
            .accentPalette('blue');
    });

    module.run(function(Restangular, gaToast, $state, $rootScope, $timeout, gaFlashMessages, _,
                        gaAuth, gaBrowserHistory) 
    {	var loadingPromise;
        var endLoading = function() 
        {	$timeout.cancel(loadingPromise);
            $rootScope.isLoading = false;
        };

        if (gaAuth.loggedIn()) 
        	gaAuth.user = Restangular.restangularizeElement(null, gaAuth.user, 'users');

        gaBrowserHistory.init();

        Restangular.setErrorInterceptor(function(res) 
        {	endLoading();
           /* if (res.status === 401) 
			{	gaToast.show('Please sign in first.');
				//$state.go('signin');
				// $location.path('/signin'); 
            } else 
			*/
			if (res.status === 403) 
            {	gaToast.show('No access to that page!');
                //$timeout(function() { $state.go('signin'); }, 1000)
				//$location.path('/signin'); 
			} else if (res.status === 404) 
            {	gaToast.show('Sorry, but that page does not exist.');
                gaBrowserHistory.back();
            } else 
			{	if (res.data && res.data.message)  
					gaToast.show(res.data.message );
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
            if (operation === 'remove') 
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
        {	if (operation === 'getList') 
			{	var d = data.list;
				d.meta = data.meta;
				return d;
            } 
			return data;
        });

        // If there are FlashMessages from server, toast will display them
        if (!_.isEmpty(gaFlashMessages)) 
        	$timeout(function() 
				{	gaToast.show(gaFlashMessages[0], 
					{	delay : 20000
					});
				}
				, 1000);

        $rootScope.$on('$stateChangeError', function() 
        {	gaToast.show('Sorry, there was a error while loading that page.');
        });

        // Fires when content is scrolled to bottom. This is defined in base.html
        $rootScope.mainContentScrolled = function() 
        {	$rootScope.$broadcast('mainContentScrolled');
        };

    });

}());
