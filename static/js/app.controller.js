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
        vm.sortType = '-date'
        activate();

        function activate() {
            StatsService.getPlayerMatches(vm.playerName).then(function(matches){
                vm.matches = matches
                for (var i=0; i<vm.matches.length; i++) {
                  vm.matches[i].index = i
                  vm.matches[i].winPlace = vm.matches[i].stats[vm.playerName].winPlace
                  vm.matches[i].kills = vm.matches[i].stats[vm.playerName].kills
                  vm.matches[i].damageDealt = vm.matches[i].stats[vm.playerName].damageDealt
                  vm.matches[i].dist = vm.matches[i].stats[vm.playerName].rideDistance +
                    vm.matches[i].stats[vm.playerName].walkDistance
                }
            })

            StatsService.getPlayerStats(vm.playerName).then(function(player){
                vm.player = player
            })
        }
    }

})();
