(function() {
    'use strict';
    var module = angular.module('admin');

    module.controller('AdminAppConfigController', function($scope, Restangular, _, gaToast, gaAppConfig) {
        Restangular.one('config').get().then(function(cfg) {
            $scope.cfg = cfg;
            $scope.cfg2 = {};
			$scope.newauth = {name:''};
			$scope.appConfigForm.unchanged = true;
			copyCfg();
			
			//console.log('0 forms = ', $scope.cfg.recaptcha_forms);
			
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

		// $scope.init = function (fname)
		// {
			// return $scope.cfg ? fname in $scope.cfg.recaptcha_forms : false;
		// }
		
        // $scope.isSecretKey = function(key) {
            // return _.endsWith(key, '_secret');
        // };

        // $scope.getAuthOptions = function() {
			
            // /*jslint unparam:true*/ // return object of all keys (names) in cfg that start with 'auth_' 
            // return _.pick($scope.cfg, function(prop, name) {
                // return _.startsWith(name, 'auth_');
            // });
        // };

        // $scope.getAuthName = function(str) {
            // return str.replace('_id', '').replace('_secret', '').replace('auth_', '');
        // };

        // $scope.capitalizeAuthName = function(str) {
            // str = $scope.getAuthName(str);
            // return _.capitalize(str);
        // };
////////////
/*		todo 
		add angular-input-modified instead of using custom code ?
		For each edit process, we need a to do deep diff client-side 
		but we dont need a patch/merge server-side - just this will work
			json = request.get_json()
			myObj = ndb.get_by_id(id)
			myObj.populate(json)
*/		
		var copyCfg = function()
		{	angular.copy($scope.cfg, $scope.cfg2);
		};
		
		$scope.reset = function () {
			angular.copy($scope.cfg2, $scope.cfg);
		};
			
		$scope.$watch(function() {
			// var cfg1 = _.pick($scope.cfg, function(val, key) 
							// {	return ! _.startsWith(key, "$");
							// });
			// var cfg2 = _.pick($scope.cfg2, function(val, key) 
							// {	return ! _.startsWith(key, "$");
							// });
			
			// var cfg1 = filter ($scope.cfg);
			// var cfg2 = filter ($scope.cfg2);
			//console.log("cfg  = ", cfg1); 
			//console.log("cfg2 = ", cfg2); 
			// var c1 = JSON.stringify(cfg1);
			// var c2 = JSON.stringify(cfg2);
			//console.log("cfg  = ", c1); 
			//console.log("cfg2 = ", c2); 
			
			//$scope.appConfigForm.unchanged = (c1 === c2);
			
			var same = angular.equals($scope.cfg, $scope.cfg2);
			$scope.appConfigForm.unchanged = same;
			
			//if (c1 !== c2)
			if (! same)
			{		
				var filter = function (obj) 
				// deep filter of $ keys: return obj except if any key of obj or sub-object of obj starts with '$' then exclude key,val from result
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
		/*		var c1 = JSON.stringify(filter ($scope.cfg));
				var c2 = JSON.stringify(filter ($scope.cfg2));
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
		*/	}
			//console.log("cfg  = ", c1); 
			//console.log("cfg2 = ", c2); 
			//console.log("unchanged = ", $scope.appConfigForm.unchanged); 
		});
		
/*		$scope.submitForm = function(){
			
			// do w/e to save, then update the cfg to match the cfg2
			angular.copy($scope.cfg2, $scope.cfg);
		};

		function findDiff (original, edited){
			var diff = {};
			for (var k in original)
				if (k in edited)
					//if (original[k] !== edited[k])
					if(! angular.equals(original[k], edited[k]))
						diff[k] = edited[k];
			return diff;
		}
*/ ///////////		
		$scope.addAuthProv = function() 
		{
			var n = $scope.cfg.authProviders.length;
			//console.log('n = ', n);
			//console.log('name = ', $scope.newauth.name);
			
			$scope.cfg.authProviders[n] = { name	: $scope.newauth.name
										  , id 		: ''
										  , secret_ : ''
										  };
			$scope.newauth.name = '';							  
			//console.log($scope.cfg.authProviders);
			$scope.appConfigForm.$setDirty()
			
		};
		$scope.removeAuthProv = function(i) 
		{
			//console.log('i = ', i);
			//console.log($scope.cfg.authProviders);
			
			$scope.cfg.authProviders.splice (i, 1);
			$scope.appConfigForm.$setDirty()
			//console.log($scope.cfg.authProviders);
			
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
			
            // 
			
            // });
        };
		
		$scope.toggle = function (formName) 
		{	//console.log('1 forms = ', $scope.cfg.recaptcha_forms);
			var idx = $scope.cfg.recaptcha_forms.indexOf(formName);
			if (idx > -1) 				//found, so remove
				$scope.cfg.recaptcha_forms.splice(idx, 1);
			else 						//not found, so insert at right position to preserve order
				$scope.cfg.recaptcha_forms.splice(idx, 0, formName);
				
			//console.log('2 forms = ', $scope.cfg.recaptcha_forms);
		};
		
		$scope.save = function() {
			//console.log($scope.cfg);
            $scope.cfg.save().then(function() {
				_.extend(gaAppConfig, $scope.cfg);
                gaToast.show('Application configuration was successfully saved.');
                $scope.appConfigForm.$setPristine();
				copyCfg();
            });
        };

    });

}());
