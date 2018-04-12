(function() 
{   'use strict';
    var module = angular.module('core');
    /**
     * @name gaBrowserHistory
     * @memberOf angularModule.core
     * @description
     * Keeps track of states user navigates
     */
    module.factory( 'gaBrowserHistory' 
		, function( $state
			      , $rootScope
				  , _, gaAuth
				  ) 
		{	var history = [];
			var ignoredStates = ['signout'];
			return { init : function()  // Initialize browser history. This has to be run on app startup
							{	
								history = [];
								/*jslint unparam:true*/
								$rootScope.$on('$stateChangeStart'
									, function(event, toState, toParams, fromState, fromParams) 
									{
										if(fromState.abstract 
										|| _.some(ignoredStates, fromState.name)) 
											return;
										history.push( { state  : fromState
													  , params : fromParams
													} );
									} );
							}
				   , back : function()	// Navigates back to previous state, or HOME
							{
								var state = history.pop();
								if 	(	! state 
									|| 	(  gaAuth.loggedIn() // If user is logged in and ... 
										&& state.state.data  // ... was previously on a signedOutOnly page
										&& state.state.data.signedOutOnly
										)) 
									$state.go('home');
								else 
									$state.go(state.state, state.params);
							}
				   };
		} );
}());
