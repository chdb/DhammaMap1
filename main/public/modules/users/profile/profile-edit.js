(function() {
    'use strict';
    var module = angular.module('users');

    module.controller('ProfileEditController', function($scope, gaBrowserHistory
									 , gaAuth, gaToast, _, gaValidators, gaTracking) 
	{
		//console.log ('edit scope: ', $scope);
        if (!$scope.hasAuthorization()) {
            gaBrowserHistory.back();
        }

        $scope.validators = gaValidators.user;

        $scope.$watch('user', function(newVal) {
            if (newVal) {
                $scope.editedUser = $scope.user.clone();
            }
        });
		
		//$scope.authProviderName = gaAuth.authProviderName;
		// function(authId)
		// {	if (authId[2] !== ':')
				// throw "invalid authId: missing colon"
			// var shortname = authId.substr(0, 3);
			// if (! shortname in gaAuthNames)
				// throw "missing shortname in authNames";
			// return gaAuthNames[shortname];
		// };
		
		$scope.authUserId = function(authId)
		{	if (authId[2] !== ':')
				throw "invalid authId: missing colon"
			return authId.substr(3, authId.length - 3);
			//return '<i class="fa fa-'+name+'"></i>'
		};
		
		$scope.removeAuthProv = function(i) 
		{			
			$scope.editedUser.authIds.splice (i, 1); // at position i remove 1 element with no replacements
			$scope.profileEditForm.$setDirty()
        };


        $scope.save = function() {
            $scope.editedUser.save().then(function() {
                _.extend($scope.user, $scope.editedUser);
                gaTracking.eventTrack('Profile edit', $scope.editedUser.username);
                gaBrowserHistory.back();
                gaToast.show('A profile was successfully updated');
            });
        };
    });
}());
