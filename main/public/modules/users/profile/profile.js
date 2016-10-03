(function() 
{	'use strict';
    var module = angular.module('users');

    module.controller('ProfileController', function($scope, Restangular, gaAppConfig, gaAuth
                                                    , $stateParams, $mdDialog, gaToast, $state) 
    {	$scope.cfg = gaAppConfig;
        $scope.auth = gaAuth;
        $scope.isMyProfile = function() 
        {	return gaAuth.loggedIn() && $stateParams.username === gaAuth.user.username;
        };

        if ($scope.isMyProfile()) 
        	$scope.user = gaAuth.user;
        else 
        	Restangular.one('users', $stateParams.username).get()
				.then(function(user) 
					{	$scope.user = user;
					});

        // $scope.getAvailableSocialAccounts = function() 
        // {	if ($scope.user) 
				// return _.pick($scope.socialAccounts, function(val, key) 
					// {	/*jslint unparam:true*/
						// return !! $scope.user[key]; // pick socialAccounts which have key and val in user
					// });
        // };

        $scope.hasAuthorization = function() 
        {	return $scope.isMyProfile() || $scope.auth.is_admin();
        };

        $scope.showDeleteUserDialog = function(ev) 
        {	var confirm = $mdDialog.confirm()
                .title('Do you really want to delete user ' + $scope.user.username)
                .content('Note, this deletion is irreversible')
                .ariaLabel('Delete User')
                .ok('Delete')
                .cancel('Cancel')
                .targetEvent(ev);
            $mdDialog.show(confirm).then(function() 
            {	$scope.user.remove().then(function() 
                {	gaToast.show('User ' + $scope.user.username + ' was deleted');
                    $state.go('users');
                });
            });
        };

    });
}());
