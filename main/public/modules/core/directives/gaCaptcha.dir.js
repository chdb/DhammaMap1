(function()
{	'use strict';
	var module = angular.module('core');
	/**
	 * @name gaCaptcha
	 * @memberOf angularModule.core
	 * @description
	 * This directive inserts no-captcha into page.
	 * In order to display captcha certain conditions must be met:
	 * - Captcha must be enabled for the form, in which this directive is called. This can be enabled/disabled via Admin Interface
	 * - Admin must set recaptcha_id & recaptcha_secret
	 * - If captcha has attribute anonymousOnly, logged users won't see it
			todo: Ok, but if that is all it is, why not call it 'disable' rather than 'anonymousOnly' ?
					Also we have that functionality already in 'isEnabled' - see below
					NB 'anonymousOnly' only appears in this directive defn - so what is *really* for and how is it used?
	 */
	module.directive('gaCaptcha', function(gaAppConfig, gaAuth)
	{	/*jslint unparam:true*/
		var prelink = function(scope, el, attrs, form)
		{	//jscs:disable requireCamelCaseOrUpperCaseIdentifiers
			scope.isEnabled =  gaAppConfig.recaptcha_id
							&& gaAppConfig.recaptcha_id.length > 0;
			if(scope.isEnabled)
			{	// gaAppConfig.recaptcha_forms contains list of form names e.g 'signinForm' from '<form name="signinForm">'
				// which should display captcha.  If the form name is not in the list, captcha won't be enabled even
				// if this directive is in the form
				var anonOnly = attrs.anonymousOnly !== undefined
							&& attrs.anonymousOnly !== 'false';
				if 	(( anonOnly && gaAuth.loggedIn())
					|| ! gaAppConfig.recaptcha_forms[form.$name]
					)
					scope.isEnabled = false;
				scope.recaptcha_id = gaAppConfig.recaptcha_id;
			}
			else
				attrs.$set('ngRequired', false);
		};
		return	{ link	  : { pre : prelink }
				, restrict: 'EA'
				, require : '^form'
				, scope	  : { ngModel		: '='
							, control		: '='
							, anonymousOnly : '@'
							, 'class'		: '@'
							}
				, template: ['<no-captcha'
							,	'ng-if="isEnabled"'
							,	'class="no-captcha {{ class }}"'
							,	'theme="light"'
							,	'g-recaptcha-response="$parent.ngModel"'
							,	'control="$parent.control"'
							,	'site-key="{{ recaptcha_id }}">'
							,'</no-captcha>'
							].join(' ')
				};
	});
}());
