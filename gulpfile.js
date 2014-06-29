var gulp = require('gulp');
var reactify = require('reactify');
var source = require('vinyl-source-stream');
var watchify = require('watchify');

var production = process.env.NODE_ENV === 'production';

function scripts(watch) {
	var bundler = watch ? watchify() : browserify();
	bundler.require('./weotu_ui/static/src/index.jsx', {expose: 'index'}); // {basedir: __dirname}
	bundler.require('./weotu_ui/static/src/sign-in.jsx', {expose: 'sign-in'}); // {basedir: __dirname}
	bundler.transform('reactify');

	// Optionally, you can apply transforms
	// and other configuration options on the
	// bundler just as you would with browserify
	//bundler.transform('brfs');

	bundler.on('update', rebundle);

	function rebundle() {
		return bundler.bundle({debug: !production})
			.pipe(source('bundle.js'))
			.pipe(gulp.dest('./weotu_ui/static/dist'));
	}

	return rebundle();
}

gulp.task('default', function() {
	return scripts(false);
});

gulp.task('watch', function() {
	return scripts(true);
});
