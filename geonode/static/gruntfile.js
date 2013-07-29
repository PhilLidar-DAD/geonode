module.exports = function(grunt) {

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

    jshint: {
      // files to lint
      files: ['gruntfile.js'],
      // configure JSHint (see http://www.jshint.com/docs/)
      options: {
        globals: {
          jQuery: true,
          console: true,
          module: true
        }
      }
    },

    less: {
      development: {
        options: {
          paths: [
            'geonode/less'
          ]
        },
        files: [
          {
            // includes bootstrap.css
            'geonode/css/base.css': 'geonode/less/base.less'
          }
        ]
      },
      production: {
        options: {
          paths: ['.components/bootstrap/less'],
          yuicompress: true
        },
        files: [
          {
            // includes bootstrap.css
            'geonode/css/base.css': 'geonode/less/base.less'
          }
        ]
      }
    },

    concat: {
      bootstrap: {
        src: [
          '.components/bootstrap/js/bootstrap-affix.js',
          '.components/bootstrap/js/bootstrap-dropdown.js',
          '.components/bootstrap/js/bootstrap-tooltip.js',
          '.components/bootstrap/js/bootstrap-alert.js',
          '.components/bootstrap/js/bootstrap-modal.js',
          '.components/bootstrap/js/bootstrap-transition.js',
          '.components/bootstrap/js/bootstrap-button.js',
          '.components/bootstrap/js/bootstrap-popover.js',
          '.components/bootstrap/js/bootstrap-typeahead.js',
          '.components/bootstrap/js/bootstrap-carousel.js',
          '.components/bootstrap/js/bootstrap-scrollspy.js',
          '.components/bootstrap/js/bootstrap-collapse.js',
          '.components/bootstrap/js/bootstrap-tab.js'
        ],
        dest: 'lib/js/bootstrap.js'
      }
    },

    copy: {
      development: {
        files: [{
          expand: true,
          flatten: true,
          cwd: '.components',
          dest: 'lib/css',
          src: [
            'datatables/media/css/jquery.dataTables.css',
            'select2/select2.css', 'select2/*.png',
            'jquery-ui/themes/cupertino/jquery-ui.css',
            'fontselect-jquery-plugin/fontselect.css', 'fontselect-jquery-plugin/*.png',
            'jquery-miniColors/jquery.minicolors.css', 'jquery-miniColors/jquery.minicolors.png',
            'multi-select/css/multi-select.css',
            'qunit/qunit/qunit.css'
          ]
        }, {
          expand: true,
          flatten: true,
          cwd: '.components',
          dest: 'lib/img',
          src: [
            'bootstrap/img/*.png',
            'raty/img/*.png',
            'multi-select/img/switch.png'
          ]
        }, {
          expand: true,
          flatten: true,
          cwd: '.components',
          dest: 'lib/images',
          src: [
            'datatables/media/images/*.png'
          ]
        }, {
          expand: true,
          flatten: true,
          cwd: '.components',
          dest: 'lib/css/images',
          src: [
            'jquery-ui/themes/cupertino/images/*.png'
          ]
        }, {
          'lib/js/hogan.js': ['.components/hogan/web/builds/2.0.0/hogan-2.0.0.js']
        }, {
          expand: true,
          flatten: true,
          cwd: '.components',
          dest: 'lib/js',
          src: [
            'jquery/jquery.js',
            'datatables/media/js/jquery.dataTables.js',
            'jquery-timeago/jquery.timeago.js',
            'tinysort/src/jquery.tinysort.js',
            'json2/json2.js',
            'select2/select2.js',
            'bootstrap-datepicker/js/bootstrap-datepicker.js',
            'requirejs/require.js',
            // Copy dist-minified libs
            // TODO: references to those require more attention (pun intended)
            'raty/js/jquery.raty.min.js',
            'jquery-waypoints/waypoints.min.js',
            // Others, with unclear reference
            // migrated from bower-installer configuration
            'jquery-ui/jquery-ui.js',
            'fontselect-jquery-plugin/jquery.fontselect.min.js',
            'jquery-loadmore/loadmore.js',
            'jquery-miniColors/jquery.minicolors.js',
            'multi-select/js/jquery.multi-select.js',
            'wysihtml5/dist/wysihtml5-0.3.0.min.js',
            'requirejs-text/text.js',
            'underscore/underscore.js',
            'qunit/qunit/qunit.js'
          ]
        }]
      }
    },

    cssmin: {
      production: {
        options: {
          // the banner is inserted at the top of the output
          banner: '/*! <%= pkg.name %> <%= grunt.template.today("dd-mm-yyyy") %> */\n'
        },
        files: {
          'lib/css/assets.min.css': [
            'lib/css/jquery.dataTables.css',
            'lib/css/select2.css'
          ]
        }
      }
    },

    uglify: {
      options: {
        // the banner is inserted at the top of the output
        banner: '/*! <%= pkg.name %> <%= grunt.template.today("dd-mm-yyyy") %> */\n'
      },
      production: {
        files: {
          'lib/js/assets.min.js': [
            'lib/js/json2.js',
            'lib/js/jquery.js',
            'lib/js/jquery.timeago.js',
            'lib/js/jquery.dataTables.js',
            'lib/js/jquery.tinysort.js',
            'lib/js/bootstrap.js',
            'lib/js/select2.js',
            'lib/js/bootstrap-datepicker.js'
          ],
          'lib/js/require.min.js': ['lib/js/require.js']
        }
      }
    }
  });

  // Load libs
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-less');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-cssmin');

  // test
  grunt.registerTask('test', ['jshint']);

  // build development
  grunt.registerTask('default', ['jshint', 'less:development', 'concat:bootstrap', 'copy']);

  // build production
  grunt.registerTask('production', ['jshint', 'less:production', 'concat:bootstrap', 'copy', 'cssmin', 'uglify' ]);

};