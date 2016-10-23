(function() 
{	'use strict';
    angular
		.module('users')
		.controller('ProfileController', 
	function ($scope , Restangular , gaAppConfig , gaAuth , gaX , $stateParams , $mdDialog , gaToast , $state)
    {	$scope.cfg = gaAppConfig;
        $scope.avatarUrl = gaX.avatarUrl;
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
