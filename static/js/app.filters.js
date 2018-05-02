(function() {

    var myApp = angular.module('myApp')

    myApp.filter('secondsToHHmmss', function($filter) {
        return function(seconds) {
            return $filter('date')(new Date(0, 0, 0).setSeconds(seconds), 'mm:ss');
        };
    })

})();