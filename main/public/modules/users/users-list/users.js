(function() 
{	'use strict';
    
	var module = angular.module('admin');
    module.controller('UsersController', function($scope, $timeout, Restangular, gaX) 
	{
        var ctrl = this;
        var nextCursor = '';
        var more = true;
        $scope.users = [];
		$scope.avatarUrl = gaX.avatarUrl;
       
        ctrl.getUsers = function() 
		{	if(more)
			{	$scope.isLoading = true;
				Restangular.all('users').getList({cursor: nextCursor}) //, filter: $scope.filter
					.then(function(userList) 
						{	$scope.users = $scope.users.concat(userList);
							$scope.total = userList.meta.totalCount;
							nextCursor 	 = userList.meta.nextCursor;
							more 		 = userList.meta.more;
							
							$timeout( function() //make sure enough users are loaded to need a scroll bar.(lrInfiniteScroll doesn't seem to do this job.)
								{ 	var el = angular.element(document.querySelector('#mainBox'));
									var sh = el.prop('scrollHeight');
									var ch = el.prop('clientHeight');
									if(sh > 0 && sh === ch)//if no vertical scroll bar ...
										ctrl.getUsers(); 	//...  call recursively
								}		
								, 250
							);
						})
					.finally(function()
						{	$scope.isLoading = false;
						});
			}
		};
		ctrl.getUsers();
        
        $scope.$on('mainContentScrolled', function() // fired when user scrolls to bottom
			{	ctrl.getUsers();
			});
    });	
}());
