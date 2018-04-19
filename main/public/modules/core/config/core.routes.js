(function()
    {	'use strict';

    var module = angular.module('core');
    module.config(
		function($stateProvider, $urlRouterProvider)
		{	//$urlRouterProvider.otherwise('/');
			// $urlRouterProvider.otherwise(function($injector, $location){
				// $injector.invoke(['$state', function($state) {
					// $state.go('home');
				// }]);
			// });
				// var $state = $injector.get('$state');
				// $state.go('app.main');

			$urlRouterProvider.otherwise(
				function($injector)
				{	console.log('Route not found - going home!');
					var $state = $injector.get('$state');
					$state.go('home');
				});

			$stateProvider
			.state('home'
				  , { url         : '/'
					, controller  : 'HomeController'
					, templateUrl : '/p/modules/core/home/home.html'
				  })
			.state('feedback'
				  , { url         : '/feedback'
					, controller  : 'FeedbackController'
					, templateUrl : '/p/modules/core/feedback/feedback.html'
				  });
		});
}());
