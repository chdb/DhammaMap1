(function() 
{	'use strict';
    var module = angular.module('admin');

    module.controller('AdminAppConfigController'
	, function($scope, Restangular, _, gaToast, gaAppConfig) 
    {	var cfg0 = {};
		Restangular.one('config').get()
		.then(function(cfg) 
        {	$scope.cfg = cfg;
            $scope.newauth = {name:''};
			$scope.appConfigForm.unchanged = true;
			copyCfg();
			
			// recaptcha is configurable on forms with these names
			// edit the array to allow other forms
			$scope.reCaptchaForms = ['signinForm', 'signupForm', 'feedbackForm'];
			
			$scope.init = {};
			var n = $scope.cfg.recaptcha_forms.length;
			for (var i = 0; i < n; i++) 
			{	var f = $scope.cfg.recaptcha_forms[i];
				//console.log('0 form = ', f);
				$scope.init[f] = true;
			}
        });
/*		todo 
		add angular-input-modified instead of using custom code ?
		For each edit process, we need a to do deep diff client-side 
		but we dont need a patch/merge server-side - just this will work
			json = request.get_json()
			myObj = ndb.get_by_id(id)
			myObj.populate(json)
*/		
		var copyCfg = function()
		{	if ($scope.cfg)
				angular.copy($scope.cfg.plain(), cfg0);
		};
		
		$scope.reset = function() 
		{	copyCfg();
		};
			
		$scope.$watch(function() 
		{	if ($scope.cfg)
			{	var same = angular.equals($scope.cfg.plain(), cfg0);
				$scope.appConfigForm.unchanged = same;
			}
		/*	if (! same)
			{	var filter = function (obj) 
				// deep filter of $ keys: return obj without any key or sub-key starting with '$'
				{	var k, r;
					if (typeof obj !== "object" && !(obj instanceof Array)) 
						return obj; 
					r = {};
					for (k in obj)
						if (obj.hasOwnProperty(k))
							if (k[0] !== '$')		//if key starts with '$' exclude key,val from result  
								r[k] = filter (obj[k]);  
					return r;
				};
				var c1 = JSON.stringify(filter ($scope.cfg));
				var c2 = JSON.stringify(filter (cfg0));
				var min = c1.length < c2.length ? c1.length : c2.length;
				//var max = c1.length < c2.length ? c2.length : c1.length;
				for (var i=0; i < min; i++) 
					if (c1[i] !== c2[i])	//find the first different char
						break;
				for (var j=1; j < min; j++) //find the last different char
					if (c1[c1.length - j] !== c2[c2.length - j])
						break;	
				console.log("diff cfg2 = ", c2.substring(i-20, c2.length-j+20)); 
				console.log("diff cfg  = ", c1.substring(i-20, c1.length-j+20)); 
			}
		*/	//console.log("cfg  = ", c1); 
			//console.log("cfg2 = ", c2); 
			//console.log("unchanged = ", $scope.appConfigForm.unchanged); 
		});
		
		$scope.addAuthProv = function() 
		{	var n = $scope.cfg.authProviders.length;
			$scope.cfg.authProviders[n] = { name	: $scope.newauth.name
										  , id 		: ''
										  , secret_ : ''
										  };
			$scope.newauth.name = '';							  
			$scope.appConfigForm.$setDirty()
		};
		
		$scope.removeAuthProv = function(i) 
		{	$scope.cfg.authProviders.splice (i, 1); // at position i remove 1 element with no replacements
			$scope.appConfigForm.$setDirty()
			
			// var confirm = $mdDialog.confirm()
                // .title('Do you really want to delete Auth Provider ' + $scope.user.username)
                // .content('Note, this deletion is irreversible')
                // .ariaLabel('Delete Auth Provider')
                // .ok('Delete')
                // .cancel('Cancel')
                // .targetEvent(ev)
				// ;
            // $mdDialog.show(confirm).then(function() 
            // {	$scope.user.remove().then(function() 
                // {	
                // });
            // });
        };
		
		$scope.toggle = function (formName) //on user toggling checkbox, determine whether to add or remove
		{	var idx = $scope.cfg.recaptcha_forms.indexOf(formName);
			if (idx > -1) 				
				$scope.cfg.recaptcha_forms.splice(idx, 1);//found, so remove
			else 						
				$scope.cfg.recaptcha_forms.splice(idx, 0, formName);//not found, so insert at right position to preserve order
		};
		
		$scope.save = function() 
		{	/* Remove unchanged cfg properties at top level- we dont need to send these
			   We assume properties can be modified but not renamed or added or deleted. A value can of course become empty. 
			   Although isEqual is deep, only top level traversal is done. 
			   So, unlike the top level, a substructure EG authIds is either sent wholesale or not at all. 
			*/
			var cfg = $scope.cfg.plain();
			
			// for (var key in validation_messages) {
				// if (!validation_messages.hasOwnProperty(key)) continue;
				// var obj = validation_messages[key];
				// for (var prop in obj) {
					// if(!obj.hasOwnProperty(prop)) continue;
					// alert(prop + " = " + obj[prop]);
				// }
			// }
			
			var ng = angular;
			
			var diff = function (cfg, cfg0)
			{ 	ng.forEach(cfg, function(v,k)
				{ 	
					var v0 = cfg0[k];
					if (_.isEqual(v, v0)) 
					{	//delete $scope.cfg[k];
						delete cfg[k];
						//console.log('deleted: '+k); 
					}			
					else if(ng.isObject(v))
					 	diff(v, v0); 
				});
			};
			//console.log('cfg0: ',cfg0); 
			diff(cfg, cfg0);
			//console.log('cfg: ',cfg); 
			
			cfg = Restangular.restangularizeElement (null, cfg, 'config');
			
			// var keys = _.keys(cfg);
			// var sameKeys = [];
			// for (var i = 0; i < keys.length; i++) 
			// {	var key = keys[i];
				// if (_.isEqual(cfg0[key], cfg[key])) // deep comparison
					// sameKeys.push(key);
			// };
			
			// angular.forEach()
			// for (var i = 0; i < sameKeys.length; i++) 
			// {	delete $scope.cfg[sameKeys[i]];
				// delete cfg[sameKeys[i]];
			// }
			
           // $scope.cfg.save()
            cfg.put()
			.then(function() 
			{	_.extend(gaAppConfig, cfg);
				gaToast.show('Application configuration was successfully saved.');
				copyCfg();
            });
        };
    });
}());
