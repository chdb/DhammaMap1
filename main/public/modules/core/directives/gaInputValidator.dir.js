(function() {
    'use strict';
    var module = angular.module('core');

    /**
     * @name ValidatorType
     * @memberOf angularModule.core
     * @description
     * This directive automatically adds following directives to element:
     * -(md-maxlength or ng-maxlength) with ng-minlength
     * - ng-pattern
     * Values for these directives are from python model validator factories(see BaseValidator in model/mBase.py)
     * Let's take for example user validator class:
     *
     * class UserVdr(model.BaseValidator):
     *      name = [3, 100]
     *
     * This min/max value for name is then passed to client as gaValidators.name_span === [3, 100]
     * Now, when we use directive:
     * <input name="name" validator="userVdr">
     * It will automatically add ng-minlength and ng-maxlength like this:
     * <input name="name" validator ng-minlength="3" ng-maxlength="100">
     *
     * If you want to use md-maxlength to show character counter pass show-counter="true"
     */
    module.directive('validator', function($compile, gaValidators, _) {
		var compile = function(el, attrs) {

			//var type = attrs.name + attrs.validator;
			var vdr = gaValidators[attrs.validator];
			if(_.isArray(vdr)) {
				if(vdr.length != 2)
					throw 'unexpected validator array length'
				if(vdr[0] > 0)
					attrs.$set('ng-minlength', vdr[0]);
				if(vdr[1] > 0) {
					var maxType = attrs.showCounter === 'true' ? 'md-maxlength' : 'ng-maxlength';
					attrs.$set(maxType, vdr[1]);
				}
			} else if(_.isString(vdr)){
				attrs.$set('ng-pattern', '/' + vdr + '/');
			}
			else throw 'unknown validator type'

			//Now that we added new directives to the element, proceed with compilation
			//but skip directives with priority 5000 or above to avoid infinite
			//recursion(we don't want to compile ourselves again)
			var compiled = $compile(el, null, 5000);
			return function(scope) {
				compiled(scope);
			};
        };

        return {
            priority : 5000, // High priority means it will execute first
            terminal : true, //Terminal prevents compilation of any other directive on first pass
            compile  : compile,
            restrict : 'A'
        };
    });

}());
