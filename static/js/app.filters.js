(function() {

    var myApp = angular.module('myApp')

    myApp.filter('secondsToHHmmss', function($filter) {
        return function(seconds) {
            return $filter('date')(new Date(0, 0, 0).setSeconds(seconds), 'mm:ss');
        };
    })

    myApp.filter('capitalize', function() {
        return function(input) {
          return (!!input) ? input.charAt(0).toUpperCase() + input.substr(1).toLowerCase() : '';
        }
    });

    myApp.filter('attack', function() {
        return function(input) {
          return (!!input) ? input.replace('Shot', '') : '';
        }
    });

})();