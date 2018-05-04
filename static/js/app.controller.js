(function() {

    var myApp = angular.module('myApp')

    myApp.controller("StatsViewCtrl", StatsViewCtrl)

    StatsViewCtrl.$inject = ['$stateParams', '$interval', 'StatsService']

    function StatsViewCtrl($stateParams, $interval, StatsService) {
        var vm = this
        vm.getStats = getStats

        vm.types = ['All', 'Squad', 'Duo', 'Solo']

        activate();

        function activate() {
            StatsService.getStats().then(function(stats){
                vm.stats = stats
            })
        }

        function getStats(type){

            if (type == 'All') {
                type = null
            } else {
                type = type.toLowerCase()
            }

            StatsService.getStats(type).then(function(stats){
                vm.stats = stats
            })
        }
    }

})();


(function() {

    var myApp = angular.module('myApp')

    myApp.controller("PlayerViewCtrl", PlayerViewCtrl)

    PlayerViewCtrl.$inject = ['$stateParams', '$interval', 'StatsService']

    function PlayerViewCtrl($stateParams, $interval, StatsService) {
        var vm = this
        vm.playerName = $stateParams.playerName
        vm.rowNumber = -1
        activate();

        function activate() {
            StatsService.getPlayerMatches(vm.playerName).then(function(matches){
                vm.matches = matches
                for (var i=0; i<vm.matches.length; i++) {
                  vm.matches[i].index = i
                }
            })

            StatsService.getPlayerStats(vm.playerName).then(function(player){
                vm.player = player
            })
        }
    }

})();
