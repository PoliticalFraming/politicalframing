'use strict';

// # Globbing
// for performance reasons we're only matching one level down:
// 'test/spec/{,*/}*.js'
// use this if you want to recursively match all subfolders:
// 'test/spec/**/*.js'

module.exports = function (grunt) {

  require('load-grunt-tasks')(grunt);
  require('time-grunt')(grunt);

  grunt.initConfig({

    yeoman: {
      app: require('./bower.json').appPath || 'app',
    },

    watch: {
      // js: {
      //   files: ['<%= yeoman.app %>/static/scripts/{,*/}*.js'],
      //   tasks: ['newer:jshint:all'],
      //   options: {
      //     livereload: true
      //   }
      // },
      // jsTest: {
      //   files: ['<%= yeoman.app %>/static/test/spec/{,*/}*.js'],
      //   tasks: ['newer:jshint:test', 'karma']
      // },
      compass: {
        files: ['<%= yeoman.app %>/static/styles/{,*/}*.{scss,sass}'],
        tasks: ['compass:server', 'autoprefixer']
      },
      gruntfile: {
        files: ['Gruntfile.js']
      },
      jade: {
        files: ['<%= yeoman.app %>/static/views/{,*/}*.jade'],
        tasks: ['jade']
      },
      // livereload: {
      //   options: {
      //     livereload: '<%= connect.options.livereload %>'
      //   },
      //   files: [
      //     '<%= yeoman.app %>/{,*/}*.html',
      //     '<%= yeoman.app %>/static/.tmp/styles/{,*/}*.css',
      //     '<%= yeoman.app %>/static/images/{,*/}*.{png,jpg,jpeg,gif,webp,svg}'
      //   ]
      // }
    },

    // Make sure code styles are up to par and there are no obvious mistakes
    jshint: {
      options: {
        jshintrc: '<%= yeoman.app %>/static/.jshintrc',
        reporter: require('jshint-stylish')
      },
      all: [
        'Gruntfile.js',
        '<%= yeoman.app %>/static/scripts/{,*/}*.js'
      ],
      test: {
        options: {
          jshintrc: '<%= yeoman.app %>/static/test/.jshintrc'
        },
        src: ['<%= yeoman.app %>/static/test/spec/{,*/}*.js']
      }
    },

    // Empties folders to start fresh
    clean: {
      dist: {
        files: [{
          dot: true,
          src: [
            '<%= yeoman.app %>/static/.tmp',
            // '<%= yeoman.dist %>/*',
            // '!<%= yeoman.dist %>/.git*'
          ]
        }]
      },
      server: '<%= yeoman.app %>/static/.tmp'
    },

    // Add vendor prefixed styles
    autoprefixer: {
      options: {
        browsers: ['last 1 version']
      },
      dist: {
        files: [{
          expand: true,
          cwd: '<%= yeoman.app %>/static/.tmp/styles/',
          src: '{,*/}*.css',
          dest: '<%= yeoman.app %>/static/.tmp/styles/'
        }]
      }
    },
    
    jade: {
      compile: {
        options: {
          data: {
            debug: false
          }
        },
        files: [{
          expand:true,
          cwd: '<%= yeoman.app %>/static',
          src: ['views/**/*.jade'],
          dest: '<%= yeoman.app %>/static/.tmp',
          ext: '.html'
        }]
      }
    },

    // Automatically inject Bower components into the app
    'bower-install': {
      app: {
        html: '<%= yeoman.app %>/templates/index.html',
        ignorePath: '<%= yeoman.app %>/static'
      }
    },




    // Compiles Sass to CSS and generates necessary files if requested
    compass: {
      options: {
        sassDir: '<%= yeoman.app %>/static/styles',
        cssDir: '<%= yeoman.app %>/static/.tmp/styles',
        generatedImagesDir: '<%= yeoman.app %>/static/.tmp/images/generated',
        imagesDir: '<%= yeoman.app %>/static/images',
        javascriptsDir: '<%= yeoman.app %>/static/scripts',
        fontsDir: '<%= yeoman.app %>/static/styles/fonts',
        importPath: '<%= yeoman.app %>/static/components',
        httpImagesPath: '/images',
        httpGeneratedImagesPath: '/images/generated',
        httpFontsPath: '/styles/fonts',
        relativeAssets: false,
        assetCacheBuster: false,
        raw: 'Sass::Script::Number.precision = 10\nrequire "sass-globbing"\n'
      },
      dist: {
        options: {
          // generatedImagesDir: '<%= yeoman.dist %>/static/images/generated'
        }
      },
      server: {
        options: {
          debugInfo: true
        }
      }
    },

    // Renames files for browser caching purposes
    rev: {
      dist: {
        files: {
          src: [
            // '<%= yeoman.dist %>/static/scripts/{,*/}*.js',
            // '<%= yeoman.dist %>/static/styles/{,*/}*.css',
            // '<%= yeoman.dist %>/static/images/{,*/}*.{png,jpg,jpeg,gif,webp,svg}',
            // '<%= yeoman.dist %>/static/styles/fonts/*'
          ]
        }
      }
    },

    // Reads HTML for usemin blocks to enable smart builds that automatically
    // concat, minify and revision files. Creates configurations in memory so
    // additional tasks can operate on them
    useminPrepare: {
      html: '<%= yeoman.app %>/templates/index.html',
      options: {
        // dest: '<%= yeoman.dist %>',
        staging: '<%= yeoman.app %>/static/.tmp'
      }
    },

    // Performs rewrites based on rev and the useminPrepare configuration
    usemin: {
      // html: ['<%= yeoman.dist %>/{,*/}*.html'],
      // css: ['<%= yeoman.dist %>/static/styles/{,*/}*.css'],
      options: {
        // assetsDirs: ['<%= yeoman.dist %>']
      }
    },

    // The following *-min tasks produce minified files in the dist folder
    imagemin: {
      dist: {
        files: [
          {
            expand: true,
            cwd: '<%= yeoman.app %>/static/images',
            src: '{,*/}*.{png,jpg,jpeg,gif}'
            // dest: '<%= yeoman.dist %>/static/images'
          }
        ]
      }
    },
    svgmin: {
      dist: {
        files: [
          {
            expand: true,
            cwd: '<%= yeoman.app %>/static/images',
            src: '{,*/}*.svg'
            // dest: '<%= yeoman.dist %>/static/images'
          }
        ]
      }
    },
    htmlmin: {
      dist: {
        options: {
          collapseWhitespace: true,
          collapseBooleanAttributes: true,
          removeCommentsFromCDATA: true,
          removeOptionalTags: true
        },
        files: [{
          expand: true,
          // cwd: '<%= yeoman.dist %>',
          src: ['*.html', 'views/{,*/}*.html'],
          // dest: '<%= yeoman.dist %>'
        }]
      }
    },

    // Allow the use of non-minsafe AngularJS files. Automatically makes it
    // minsafe compatible so Uglify does not destroy the ng references
    ngmin: {
      dist: {
        files: [{
          expand: true,
          cwd: '<%= yeoman.app %>/static/.tmp/concat/scripts',
          src: '*.js',
          dest: '<%= yeoman.app %>/static/.tmp/concat/scripts'
        }]
      }
    },

    // Replace Google CDN references
    cdnify: {
      dist: {
        // html: ['<%= yeoman.dist %>/*.html']
      }
    },

    // Copies remaining files to places other tasks can use
    copy: {
      dist: {
        files: [{
          expand: true,
          dot: true,
          // cwd: '<%= yeoman.app %>/static/',
          // dest: '<%= yeoman.dist %>/static/',
          src: [
            '*.{ico,png,txt}',
            '.htaccess',
            '*.html',
            'views/{,*/}*.html',
            'components/**/*',
            'images/{,*/}*.{webp}',
            'fonts/*'
          ]
        }, {
          expand: true,
          cwd: '<%= yeoman.app %>/static/.tmp/images',
          // dest: '<%= yeoman.dist %>/static/images',
          src: ['generated/*']
        }]
      },
      styles: {
        expand: true,
        cwd: '<%= yeoman.app %>/static/styles',
        dest: '<%= yeoman.app %>/static/.tmp/styles/',
        src: '{,*/}*.css'
      }
    },

    // Run some tasks in parallel to speed up the build process
    concurrent: {
      dist: [
        'compass',
        'imagemin',
        'svgmin'
      ]
    },

    // By default, your `index.html`'s <!-- Usemin block --> will take care of
    // minification. These next options are pre-configured if you do not wish
    // to use the Usemin blocks.
    // cssmin: {
    //   dist: {
    //     files: {
    //       '<%= yeoman.dist %>/styles/main.css': [
    //         '<%= yeoman.app %>/static/.tmp/styles/{,*/}*.css',
    //         '<%= yeoman.app %>/styles/{,*/}*.css'
    //       ]
    //     }
    //   }
    // },
    // uglify: {
    //   dist: {
    //     files: {
    //       '<%= yeoman.dist %>/scripts/scripts.js': [
    //         '<%= yeoman.dist %>/scripts/scripts.js'
    //       ]
    //     }
    //   }
    // },
    // concat: {
    //   dist: {}
    // },

    // Test settings
    karma: {
      unit: {
        configFile: '<%= yeoman.app %>/static/karma.conf.js',
        singleRun: true
      }
    }
  });


  grunt.registerTask('serve', function () {
    // if (target === 'dist') {
      // return grunt.task.run(['build', 'connect:dist:keepalive']);
    // }

    grunt.task.run([
      'clean:server',
      'bower-install',
      'compass:server',
      'autoprefixer',
      'jade',
      'watch'
    ]);
  });

  grunt.registerTask('heroku', [
    'clean:server',
    'bower-install',
    'compass:server',
    'autoprefixer',
    'jade'
  ]);

  grunt.registerTask('test', [
    'clean:server',
    'compass',
    'autoprefixer',
    // 'connect:test',
    'karma'
  ]);

  grunt.registerTask('build', [
    'clean:dist',
    'bower-install',
    'useminPrepare',
    'jade',
    'concurrent:dist',
    'autoprefixer',
    'concat',
    'ngmin',
    'copy:dist',
    'cdnify',
    'cssmin',
    'uglify',
    'rev',
    'usemin',
    'htmlmin'
  ]);

  // grunt.registerTask('default', [
  //   'newer:jshint',
  //   'test',
  //   'build'
  // ]);

};
