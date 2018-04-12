(function() {
    'use strict';
    var module = angular.module('core');

    module.controller('SidenavController', function($scope, $mdSidenav, gaAuth, gaAppConfig, Restangular,
                                                    gaToast, $mdDialog, $timeout) {
        $scope.auth = gaAuth;
        //$scope.cfg = gaAppConfig;
		  //console.log(gaAppConfig);
        $scope.closeSidenav = function() {
            $mdSidenav('leftSidenav').close();
        };
	
        $scope.generateDatabase = function(ev) 
        {	
			$scope.genDB = function(re) 
			{	gaToast.show(re+'Generating database...', {delay : 0});
				Restangular.all('generate_database').post().then(function() 
				{   gaToast.update('Database was successfully '+re+'generated. You can sign in with admin:123456');
					$timeout(gaToast.hide, 5000);
				});
			};
			
			Restangular.all('num_users').customGET().then(function(n)
			{	if(n > 0) 	
				{	var confirm = $mdDialog.confirm()
						.title('There are currently '+ n +' users.')
						.content('Do you really want to delete all these users?(Deletions are irreversible.)')
						.ariaLabel('Delete all existing Users and generate new Database')
						.ok('OK')
						.cancel('Cancel')
						.targetEvent(ev);
						
					$mdDialog.show(confirm).then(function() 
					{	$scope.genDB('Re-');
					});
				}
				else $scope.genDB('');
			});
        };


        $scope.$on('$stateChangeSuccess', $scope.closeSidenav);
    });
}());
