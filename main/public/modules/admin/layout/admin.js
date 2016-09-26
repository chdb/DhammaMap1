(function() {
    'use strict';
    var module = angular.module('admin');

    module.controller('AdminController', function(gaAuth, gaToast, gaBrowserHistory) {
        if (!gaAuth.is_admin()) {
            gaToast.show('No, you cannot access that page');
            gaBrowserHistory.back();
        }
    });

}());
