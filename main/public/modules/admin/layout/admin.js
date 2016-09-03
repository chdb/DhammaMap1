(function() {
    'use strict';
    var module = angular.module('admin');

    module.controller('AdminController', function(gaAuthentication, gaToast, gaBrowserHistory) {
        if (!gaAuthentication.isAdmin()) {
            gaToast.show('No, you cannot access that page');
            gaBrowserHistory.back();
        }
    });

}());
