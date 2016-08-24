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
        var me = {
            user     : gaAuthenticatedUser,
            loggedIn : function() {
                return !!me.user;
            },
            isAdmin  : function() {
                return me.loggedIn() && me.user.isAdmin_;
            },
            setUser  : function(user) {
                me.user = Restangular.restangularizeElement(null, user, 'users');
            }
        };

        return me;
    });

}());
