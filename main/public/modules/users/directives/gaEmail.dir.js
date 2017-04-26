(function() 
{   'use strict';
    var module = angular.module('users');

    /**
     * @name gaEmail
     * @memberOf angularModule.users
     * @description
     * Inserts email input into page. This directive is mainly to prevent code repetition
     * throughout the app
     */

    module.directive('gaEmail', function ($http, Restangular) 
    {    /*jslint unparam:true*/
        var linker = function (scope, el, attrs, form ) 
		{	//console.log('gaEmail scope --- ', scope)
			console.log('gaEmail el --- ', el);
			console.log('gaEmail attrs --- ', attrs);
			console.log('gaEmail form --- ', form);
			
			//scope.restNg = Restangular;
            scope.name  = scope.name  || 'email_';
            scope.label = scope.label || 'Email';
            scope.form = form;
            scope.required = attrs.required !== undefined && attrs.required !== 'false';
			//scope.restNg = $injector.get('Restangular');
	
			/* scope.onBlur = function() 
			{   console.log('qqqqqqqqqqqqqq : ' );
				// var parameter = JSON.stringify({type:"user", username:user_email, password:user_password});
				// $http.post(url, parameter)
				Restangular.all('auth/unique_ema').post({'email_':scope.ngModel})
				//scope.restNg.all('auth/unique_ema').post(scope.credentials.email_)
				.then( function(res)
						{	//console.log('xxxxxxxxxx res: ' , res);
							//console.log(res);
							form.ema.$setValidity('unique', true);
						}
					 , function(response) 
						{	//console.log("Error with status code", response, response.status); 
							form.ema.$setValidity('unique', false);
							//console.log(response.data); 
						}	
					 );
			}; */
        };	
        return 	{ templateUrl:'/p/modules/users/directives/gaEmail.html'
				, link    	 : linker /* { pre : linker } */
				, restrict	 : 'EA'
				, replace 	 : true
				, require 	 : '^form'
				, scope   	 : { inputTabindex :'@'
							   , name          :'@'
							   , label         :'@'
							   , ngModel       :'='
							   }
				};
    });
}());

