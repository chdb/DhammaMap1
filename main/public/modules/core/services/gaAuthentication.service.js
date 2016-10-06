(function() 
{   'use strict';
    var module = angular.module('core');

    /**
     * @name gaAuth
     * @memberOf angularModule.core
     * @description
     * This service holds a user object so that it can be accessed in any controller
     */

    module.factory('gaAuth', function(gaAuthUser, gaAuthNames, Restangular) 
	{	
		var u =	
		{ user 		: gaAuthUser
		, loggedIn  : function() 	
					{ 	return !! u.user; }
		, is_admin  : function() 	
					{ 	if (! u.user)
							return false;
						if (u.user.isAdmin_ === undefined) 
							console.log('unknown admin status!', u.user);
						//console.log(' admin status: ', u.user.isAdmin_);
						return u.user.isAdmin_
					}
		, setUser : function(user) 
					{ 	u.user = Restangular.restangularizeElement(null, user, 'users'); }
		, authProviderName : function(authId)
					{	if (authId[2] !== ':')
							throw "invalid authId: missing colon"
						var shortname = authId.substr(0, 3);
						if (! shortname in gaAuthNames)
							throw "missing shortname in authNames";
						return gaAuthNames[shortname];
					}
		};
		return u;  
    });

}());
