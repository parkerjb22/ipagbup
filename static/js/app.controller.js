(function() {

    var myApp = angular.module('myApp')

    myApp.controller("StatsViewCtrl", StatsViewCtrl)

    StatsViewCtrl.$inject = ['$routeParams', '$interval', 'StatsService']

    function StatsViewCtrl($routeParams, $interval, StatsService) {
        var vm = this
        activate();

        function activate() {
            StatsService.getStats().then(function(stats){
                vm.stats = stats
            })
        }
    }

})();
