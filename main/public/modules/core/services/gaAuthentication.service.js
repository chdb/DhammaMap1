(function() {
    'use strict';
    var module = angular.module('core');

    /**
     * @name gaAuthentication
     * @memberOf angularModule.core
     * @description
     * This service holds user object, so it can be used in any controller
     */

    module.factory('gaAuthentication', function(gaAuthenticatedUser, Restangular) {
		var u =	{ user     : gaAuthenticatedUser
				, loggedIn : function() 	{ return !! u.user; }
				, isAdmin  : function() 	{ return u.loggedIn() && u.user.isAdmin_; }
				, setUser  : function(user) { u.user = Restangular.restangularizeElement(null, user, 'users'); }
				};

		return u;
    });

}());
