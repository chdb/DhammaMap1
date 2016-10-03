(function() 
{   'use strict';
    var module = angular.module('core');

    /**
     * @name gaAuth
     * @memberOf angularModule.core
     * @description
     * This service holds a user object so that it can be accessed in any controller
     */

    module.factory('gaAuth', function(gaAuthUser, Restangular) 
	{	
		var u =	{ user : gaAuthUser
				, loggedIn : function() 	
					{ 	return !! u.user; }
				, is_admin : function() 	
					{ 	if (! u.user)
							return false;
						if (u.user.isAdmin_ === undefined) 
							console.log('unknown admin status!', u.user);
						//console.log(' admin status: ', u.user.isAdmin_);
						return u.user.isAdmin_
					}
				, setUser : function(user) 
					{ 	u.user = Restangular.restangularizeElement(null, user, 'users'); }
				};
		return u;
    });

}());
