(function() 
{ 'use strict';
	var module = angular.module('users');

	/**
	 * @name gaPassword
	 * @memberOf angularModule.users
	 * @description
	 * Inserts password input into page.
	 * If model is passed in repeat-password="myPassword" it adds additional validity checking
	 * for this directive. It will display error is passwords don't match
	 */

	module.directive('gaPassword', function(gaValidators) 
	{ /*jslint unparam:true*/
		var link = function(scope, el, attrs, ctrls) 
		{	var form = ctrls[0];
			var ngModel = ctrls[1];
			scope.name	= scope.name  || 'password';
			scope.label = scope.label || 'Password';
			var v = gaValidators.password_span;
			scope.minlen = v ? v[0] : 0;
			scope.maxlen = v ? v[1] : 0;
			scope.form = form;
			if(attrs.repeatPwd) 
			{	scope.$watch
				( function() 			//watch expression
					{ return scope.repeatPwd() === ngModel.$modelValue; }
				, function(newVal) 	//watch listener 
					{ form[scope.name].$setValidity('mismatch', newVal); }
				);
			}
		};
		return	{ link	  	: link
				, restrict	: 'EA'
				, replace 	: true
				, require 	: ['^form', 'ngModel']
				, scope	  	: { inputTabindex :'@'
							  , name		  :'@'
							  , label	      :'@'
							  , optional	  :'@'
							  , ngModel		  :'='
							  , repeatPwd	  :'&'
							  }
				, templateUrl:'/p/modules/users/directives/gaPassword.html'
				};

	});

}());
