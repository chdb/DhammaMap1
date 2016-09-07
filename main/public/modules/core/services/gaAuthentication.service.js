(function() 
{   'use strict';
    var module = angular.module('core');

    /**
     * @name gaAuth
     * @memberOf angularModule.core
     * @description
     * This service holds user object, so it can be used in any controller
     */

    module.factory('gaAuth', function(gaAuthUser, Restangular) 
	{	var u =	{ user     : gaAuthUser
				, loggedIn : function() 	{ return !! u.user; }
				, isAdmin  : function() 	{ return u.loggedIn() && u.user.isAdmin_; }
				, setUser  : function(user) { u.user = Restangular.restangularizeElement(null, user, 'users'); }
				};
		return u;
    });

}());
