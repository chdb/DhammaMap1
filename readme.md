# Dhamma Map

### TODO
* ##### server module structure ...
	has imports loops and over-complexity 
	* remove main/__init__.py and create a direct entrypoint in main.py from app.yaml into /main.app 
	
	* config is defined in config.py constants and also in model/config.py   
	then imported into config module rethink and simplify this!
	Some config setting should not be visible or readonly in the client eg crypto ones.

	What goes into config?
		* constants that might be changed but possibly saved and returned to.
		* data that is sensitive so cannot be in source control eg crypto keys
		* data that is shared over different modules   
It is simple and convenient to create some hard-coded configuration data in a config file  
But other config data is stored in ndb DataStore because  
		1) main Source Code is not a secure location for cryptographic keys and other secrets because our code base is 
		open-source	(Even closed-source code has access issues because its inevitably and habitually saved to a cvs with 
		different/lower security than the DataStore)    
		2) Its convenient to change some config settings eg throttle settings, via the client, or the GAE dashboard, 
		without having to deploy modified application code
		(However while some secure data may be in DataStore, it should not be modifiable in the Client eg private keys
		
		* create 2 config files : config-dev in source control, config-prod in gitignore 
		* use datastore only for config items needing dynamic adjustment IE without uploading restarting instance - therefore needs to be in datastore   
		eg Rate liniting cfg
		* use config package with config_devt.py / config-prod.py for 
			* secure data - crypto keys etc, module
			* other module-shared cfg data
			* import ds config into it with once-only singleton pattern
		* remove any others (non-secure single-module data) from config altogether and define in a local module, any item that is 
	
*  ##### Idle Instances
It seems (from SO posts) to take 1 - 10 seconds to spin up a new instance and we have no control over that. One second is ok but 10 means a bad 'unresponsive' user experience. 
We have free quota of 28 instance hours per day. So for a low-traffic site we obviously want to keep one instance running 24 hours per day.
Then the other 4 hours are available for a second instance to spin up at peak times.
   
However from SO posts, it seems that Google makes this slightly difficult. Setting automatic-scaling to true and min-idle-instances to 1 does not seem to prevent the 1 instance shutting down (after 5 or 15 minutes?)

Solution:  Create a low-traffic keep-alive Cron job that calls an api method but otherwise does nothing, every X seconds (configurable EG 10 minutes?)
This is said to prevent the runtime from shutting the instance.

* ##### throttling  
	Currently the an Anonymous threat is Identified with 
		* source ip address - but 
			* bot attacks come from multiple sources
			* NAT means that many users can share ip address eg corporate users but even wjole countries may be NATted 
		* target email address - but
			* dictionary attacks distribute calls over a range of targets
	This is weak so we want to add this -
	* a device token to supplement ip-address for anonymous client id
		* signed client device token can hold ipaddress and rate data + HMAC  
		The rate data would be waitExpiry and numberFailures.  Same data copied to MemCache for this.
		* unlike ip-address, a device token in a cookie can be deleted   
		and unfortunately, if the device cookie is not found, we cannot distinguish these two causes
			* cookie was deleted 
			* first use of app with this device  
		* solution? : the device token is sent twice to client 
				* as httponly cookie
				* as template data
			(This is like how csfr token is usally sent - if so the mechanisms can be combined)
			The server checks for both of these and also memcache for the rate limit data.
			If anything is missing then it is repaired with a log warning 
			* If nothing missing then a new token must be issued. 
				* on app start ("please wait while we register this device")
				* on login or whatever with or without a message  
				* Creating a new device token must have a time penalty which could be imposed 
			* a global mechanism to ratelimit creation of new device tokens
				* creation of a new token done is in a task, with task queue set to max rate for issuing tokens
				* task creates then puts the new token in memcache with key "newDeviceToken"
				* a request can get a new decvice token from memcache   
				\- if it has a value, then request takes it and replaces it with None

	Therefore the user can avoid the rate limit mechanism by deleting the cookie.  
	But to do this
		* she has to enable cookies before running our app
		* she has to close, then delete, then reopen the app 
		* she has to pay a (smallish because its paid by the true first-timers) time penalty
		* she cannot efectively exploit this in a botnet attack because global token issuing is limited

* ##### Validation
Implement multiple input validation feedback. Currently if there are multiple input fields, user gets feedback only on the first firld to fail.
and she has to go through multiple subnissions to iron them all out. We want an error message with each failed field.
So one of these -   
1 instead of throwing an exception in the loop, we need the loop to populate eg a dict : 'fieldName' -> 'errorMessage' and then raise the exception after the loop ends 	
2 have a separate ajax call  and validation for each input.  Need to fire the call on ngBlur for input losing focus

* ##### features
* provide gs host support for uploading email lists
* provide gs host support for managing One Day Course bookings 
* provide gs host support for email - canned responses 

	----
	* Lock.\_keystr needs to adapted
		* remove hdr. We should not separate out locks by handler
		* add prefix for
			* client device token id
			* source ip address
			* target email address
	* revise Kryptoken for use with device token - encryption should be optional
	* revise basehandler and User throttle code
	* On client side create ng-service etc for throttled API calls 
	* ... and a directive? for their submit buttons
* write the description of the app - this goes into html meta-data
* simplify clientside folders
* convert from Angular Material to Bootstrap
* add map content
* Status is usually unVerified or Active(ie verified and not blocked) or Blocked.  
But it could (in the event of an attack on an unVerified account) be both un-Verified and Blocked (in-Active) as at present.  
	* merge _isVerified_\_ with _token_\_\_  
	* add *token_expiry*  
	* add properties to decode token prefixes -  
		* _su_ prefix - waiting for signup verification
		* _pw_ prefix - waiting for password reset verification
		* None - user "isActive"   
* replace auth code with authomatic lib
* replace/test recaptcha code - it looks wrong
* add MailGun sending code 
* add MailGun email validation and result-hint support in client
* add password strength using _zxcvbn_ code
* implement oldstudent-login 
* consider adding back suport for IE8 (0.5% of users according to caniuse.com)   
For example IE8 does not support indexOf 

### Done
* separate validation module from model.Base and ArgVdr class 
* check data leakage to non admin etc / finish property code 
* replace User model with extensible User + AuthId models

### Notes
#### Private User properties and Admin status
In the client a user can see her own profile once she has logged in and she can edit her own non-read-only public properties.
The logged-in admin user can see and edit all (private and public) non-hidden non-read-only properties of all users.
So she can add or remove admin status from others and herself.

Currently * isAdmin\_ * is a private property of User.  Thats why it ends with __\_ __. 
Therefore the non-admin user cannot even see explicitly that she is not an admin (However it will be obvious from lack of features eg get User List)
But an admin user can remove admin status from self or others. Once it is removed then it can only be replaced by another admin or by using the Google Cloud Dashboard aka Console


#### template rendering
We are currently using 2 templating engines - 
* jinja2  server-side
* angular client-side

The locations are different
* jinja2  html files are in **main/templates** and **main/templates/bit**
* angular html files are in **main/public**

Since this is a Single Page App, jinja2 engine is just only rendering **most of** the home page. Angular does the rest 
but also (oddly) Angular also renders those bits of home page that are inserted with **ng-include**
* /public/modules/core/layout/sidenav.html 
* /public/modules/core/layout/header.html

This is why some files locations seem inconsistent:- 
*  **footer.html** is at **main/templates/bit**    			(for jinja2  rendering)
*  **header.html** is at **main/public/modules/core/layout**	(for angular rendering)


This seems to be working ok, although there are many SO posts expalining that you have to change the delimiters 
of one side, so that they dont conflict.  Both engines use **{{ ... }}** by default, but can be configured otherwise.


# GAE Angular Material Starter
##### Easiest way to start Google App Engine Angular Material project on Earth & Mars!
As a base for this I've used starter projects [gae-init] and [MEANJS], so big thanks to them!

This full stack uses following technologies:
* Google App Engine
* Python Flask
* AngularJS
* Angular Material
* Gulp, Bower, npm

###### You can see live demo here: https://gae-angular-material-starter.appspot.com/

## What's implemented?
* Everything about user authentication - signin, signup, forgot pass, reset pass ... and all the boring stuff is done for you :)
* Authentication with 11 different OAuth sites (Facebook, Twitter, etc.)
* User profile pages - users can view/edit their profiles
* Users list
* Admin Interface - admin can edit app config, edit/delete/block users, etc.
* "Send Feedback" page
* Ability to generate mock data, while developing
* Integration with no-captcha
* Tracking with Google Analytics
* Lots of useful angular directives and services

## What do I need?
First make sure you've got following things installed on your machine:
* [Google App Engine SDK for Python][]
* [Node.js][]
* [pip][]
* [virtualenv][]

## Install!
Using yeoman:
```
sudo npm install -g generator-gae-angular-material-starter
mkdir myNewApp && cd myNewApp
yo gae-angular-material-starter  # it will ask you few questions, e.g your app name, etc.
gulp run
```

Using github:
```
git clone https://github.com/madvas/gae-angular-material-starter
cd gae-angular-material-starter
npm install
gulp run
```
And that's it! You should now see the app running on port 8080.
You can now sign in via Google, or you can click "Generate Database" and then sign in as "admin" with password "123456"

## Deploy!
When you're done with your beautiful Material Design app it's time to deploy!
First, make sure you change your application name in `app.yaml`
```
gulp build
appcfg.py update main
```
And that's it! Your next big thing is out!

## What's left to do?
* Tests - soon to be done
* Docs/Tutorial - Although, docs doesn't exist yet, code is heavily commented, so you know what's going on :)

## Contribute!
Sure you can :)

License
--
MIT. Can't be more open, source ;)

[google app engine sdk for python]: https://developers.google.com/appengine/downloads
[node.js]: http://nodejs.org/
[pip]: http://www.pip-installer.org/
[virtualenv]: http://www.virtualenv.org/
[gae-init]: https://github.com/gae-init/gae-init
[meanjs]: https://github.com/meanjs/mean
