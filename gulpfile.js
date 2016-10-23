(function() {

/*to debug use:
	node-debug %appdata%\npm\node_modules\gulp\bin\gulp.js <task>	
*/	
    var gulp = require('gulp');
    require('gulp-grunt')(gulp);

    var $ 			= require('gulp-load-plugins')();
    var watch		= require('gulp-watch');
    var del			= require('del');
    var exec		= require('child_process').exec;
    var inject		= require('gulp-inject');
    var uglify		= require('gulp-uglifyjs');
    var less		= require('gulp-less');
    var minifyCSS	= require('gulp-minify-css');
    var concatCss	= require('gulp-concat-css');
    var glob		= require('glob');
    var rename		= require('gulp-rename');
    var ngAnnotate	= require('gulp-ng-annotate');
    var sourcemaps	= require('gulp-sourcemaps');
    var jshint		= require('gulp-jshint');
    var stylish		= require('jshint-stylish');
    var jslint		= require('gulp-jslint-simple');
    var jslintrc	= require('./jslintrc');
    var jscs		= require('gulp-jscs');
    var htmlhint	= require('gulp-htmlhint');
    var templateCache=require('gulp-angular-templatecache');
    var zip			= require('gulp-zip');
	var gutil = require('gulp-util');
	gutil.log('Hello world!');
	
    // Frontend Paths
    var rootDir 	= 'main';
    var publicDir 	= rootDir + '/public';
    var publicLibDir= publicDir + '/lib';
    var distDir 	= publicDir + '/dist';
    var modulesDir 	= publicDir + '/modules';

    // Backend Paths
    var pyLib     = '/lib';
    var pyLibDir  = rootDir + pyLib;
    var tempDir   = 'temp';
    var venvDir   = tempDir + '/venv';
    var storageDir= tempDir + '/storage';
    var lessPaths = [ publicDir + '/lib/font-awesome/less'];
    var appLessPaths = publicDir + '/modules/**/less';
    lessPaths = lessPaths.concat(glob.sync(appLessPaths));
    var templatesDir = rootDir + '/templates';
	
    var htmlViews = ['modules/**/*.html'];
    var manifestLessFile = 'modules/core/less/manifest.less';
    var cssFiles =  [ 'lib/angular-material/angular-material.css'];

    var jsFiles = 
	{ lib : [ './lib/angular/angular.js'
            , './lib/angular-ui-router/release/angular-ui-router.js'
            , './lib/angular-animate/angular-animate.js'
            , './lib/angular-messages/angular-messages.js'
            , './lib/angular-aria/angular-aria.js'
            , './lib/restangular/dist/restangular.js'
            , './lib/angular-no-captcha/src/angular-no-captcha.js'
            , './lib/angular-material/angular-material.js'
            , './lib/lodash/lodash.js'
            , './lib/lrInfiniteScroll/lrInfiniteScroll.js'
            , './lib/angulartics/src/angulartics.js'
            , './lib/angulartics/src/angulartics-ga.js'
			]
	, scripts :
			[ './application.js'
            , './modules/**/*.js'
            , '!./modules/**/tests/**/*.js'
			]
    };
    gulp.task('bower-install', function() 
    {	return $.bower();
    });

    gulp.task('reload', function() 
    {	$.livereload.listen();
        gulp.watch( jsFiles.scripts.concat(htmlViews)
				  , { cwd : publicDir }
				  )
		.on('change', $.livereload.changed);
    });

    function injectScripts() 
	{   
		var target  = gulp.src ( templatesDir + '/bit/script.html');
        var sources = gulp.src ( jsFiles.lib.concat(jsFiles.scripts)
							   , { read : false		
								 , cwd  : __dirname + '/main/public/'  // rootDir //  publicDir + '/'
							   } );
        return target.pipe ( inject ( sources
								   , { relative	: true // added
								     , addPrefix: '/p'
									 , ignorePath: '../../public'
								   } ) ) 
					 .pipe ( gulp.dest (templatesDir)); // was publicDir
    }

    gulp.task('inject-scripts', injectScripts);

    gulp.task('watch-new-scripts', function() 
    {	watch([modulesDir + '/**/*.js', publicDir + '/*.js'], function(e) 
        {	if (e.event === 'add' || e.event === 'unlink') 
            {	injectScripts();
            }
        });
    });

    gulp.task('uglify', ['less'], function() 
    {	gulp.src( jsFiles.lib
				, {	cwd : publicDir }
				)
			.pipe(uglify('libs.min.js'))
			.pipe(gulp.dest(distDir));
		gulp.src(jsFiles.scripts 
				, {	cwd : publicDir }
				)
			.pipe(ngAnnotate())
			.pipe(uglify('scripts.min.js'))
			.pipe(gulp.dest(distDir));
        gulp.src( 'style.css'
				, {	cwd : distDir }
				)
			.pipe(minifyCSS())
			.pipe(rename({ suffix : '.min'}))
			.pipe(gulp.dest(distDir));
    });

    gulp.task('less', function() 
    {	console.log('cssFiles ',cssFiles);
    	console.log('manifestLessFile ',manifestLessFile);
    	console.log('lessPaths ',lessPaths);
		
		return gulp.src ( cssFiles.concat(manifestLessFile) 
						, {	cwd : publicDir }
	   ).pipe(sourcemaps.init())
	    .pipe(less({ paths : lessPaths }))
	    .pipe(sourcemaps.write())
	    .pipe(concatCss('style.css'))
	    .pipe(gulp.dest(distDir));
    });

    gulp.task('watch-less', function() 
    {	gulp.watch(appLessPaths + '/*.less', ['less']);
    });

    gulp.task('jshint', function() 
    {	return gulp.src ( jsFiles.scripts 
						, {	cwd : publicDir }
						)
		.pipe(jshint())
		.pipe(jshint.reporter(stylish));
    });

    gulp.task('jslint', function() 
    {	return gulp.src	( jsFiles.scripts
						, {	cwd : publicDir }
						)
		.pipe(jslint.run(jslintrc))
		.pipe(jslint.report({ reporter : stylish.reporter }));
        
    });

    gulp.task('jscs', function() 
    {	return gulp.src([modulesDir + '/**/*.js', './*.js']).pipe(jscs());
    });

    gulp.task('htmlhint', function() 
    {	return gulp.src(htmlViews 
						, {	cwd : publicDir }
						)
		.pipe(htmlhint({ htmlhintrc : 'htmlhintrc.json'}))
		.pipe(htmlhint.reporter());
    });

    gulp.task('lint', ['jshint', 'jslint', 'jscs', 'htmlhint', 'grunt-pylint']);

    gulp.task('template-cache', function() 
    {	gulp.src( 'modules/**/*.html' 
				, {	cwd : publicDir }
				)
		.pipe ( templateCache('templates.js'
			  , { standalone : false
				, root       : '/p/modules'
				, module     : 'Dhamma Map'
			  } ) )
		.pipe(gulp.dest(distDir));
    });

    gulp.task('copy-fonts', function() 
    {	gulp.src('font-awesome/fonts/*'
				, {	cwd : publicLibDir } // + '/font-awesome/fonts'
				)
		.pipe(gulp.dest(distDir + '/fonts'))
    });

    gulp.task('clean-js', function() 
    {	del([publicLibDir, distDir]);
    });

    gulp.task('clean-cache', function(callback) 
    {	del([rootDir + '/**/*.pyc', rootDir + './**/*.pyo', rootDir + './**/.*~'], callback);
    });

    gulp.task('zip-lib', ['clean-cache'], function() 
    {	gulp.src(pyLibDir + '/**/*')
            .pipe(zip(pyLib + '.zip'))
            .pipe(gulp.dest(rootDir));
    });

    gulp.task('clean-storage', function() 
    {	del([storageDir]);
    });

    gulp.task('clean-python', function() 
    {	del([venvDir, pyLibDir]);
    });

    gulp.task('clean-all', ['clean-cache', 'clean-python'], function() 
    {	del(['bower_compenents', 'node_modules', publicLibDir, distDir, venvDir, pyLibDir]);
    });
	
	var runServer_ = function(skipChecks) 
    {	var execStr = 'python -u run.py --appserver-args --log_level=debug';
		if (skipChecks)
			execStr	+= ' --skip-checks'
		var proc = exec(execStr);
        proc.stderr.on('data', function(data) 
        {	process.stderr.write(data);
        });
        proc.stdout.on('data', function(data) 
        {	process.stdout.write(data);
        });
    };	
    gulp.task(  'run-server', function() {runServer_(false)});
    gulp.task('rerun-server', function() {runServer_(true )});

    gulp.task('watch', 	[ 'reload'
						, 'watch-less'
						, 'watch-new-scripts'
						]);

    gulp.task('rerun',	[ 'watch'
						, 'rerun-server'
						]);

	gulp.task('run',	[ 'clean-cache'
						, 'bower-install'
						, 'inject-scripts'
						, 'less'
						, 'watch'
						, 'copy-fonts'
						, 'run-server'
						]);

    gulp.task('build', 	[ 'lint'
						, 'zip-lib'
						, 'uglify'
						, 'inject-scripts'
						, 'template-cache'
						, 'copy-fonts'
						]);

    gulp.task('default', ['run']);

}());
