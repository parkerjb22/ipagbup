(function() {

    var myApp = angular.module('myApp')

    myApp.controller("StatsViewCtrl", StatsViewCtrl)

    StatsViewCtrl.$inject = ['$stateParams', 'StatsService']

    function StatsViewCtrl($stateParams, StatsService) {
        var vm = this
        vm.getStats = getStats

        vm.types = ['All', 'Squad', 'Duo', 'Solo']

        activate();

        function activate() {
            StatsService.getStats().then(function(stats){
                vm.stats = stats
            })

            StatsService.getWeaponStats().then(function(weapons){
                vm.weapons = weapons
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

    PlayerViewCtrl.$inject = ['$stateParams', 'StatsService', '$cacheFactory']

    function PlayerViewCtrl($stateParams, StatsService, $cacheFactory) {
        var vm = this

        vm.playerName = $stateParams.playerName
        vm.rowNumber = -1
        vm.tab = 0
        vm.sortType = '-date'

        vm.limits = [
            { 'text':'All Matches', 'amount': null},
            { 'text':'Last 10', 'amount': 10},
            { 'text':'Last 25', 'amount': 25},
            { 'text':'Last 50', 'amount': 50},
        ]

        vm.maps = [
            { 'name': 'Erangel', 'selected': true },
            { 'name': 'Mirimar', 'selected': true },
        ]

        vm.playerNames = [
            'BigGoof20',
            'Honkieharris',
            'UCBananaboy',
            'WTJ22'
        ]

        vm.selectedLimit = vm.limits[0]

        vm.getStats = getStats
        vm.selectMatch = selectMatch

        var cacheName = 'dmg_cache'
        if ($cacheFactory.get(cacheName)){
            vm.cache = $cacheFactory.get(cacheName)
        } else {
            vm.cache = $cacheFactory(cacheName, { capacity: 25 });
        }

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

            StatsService.getPlayerWeapons(vm.playerName).then(function(result){
                vm.weapons = result.weapons
            })
        }

        function getStats(limit){
            var selectedMaps = []
            for (var i=0; i<vm.maps.length; i++) {
                if (vm.maps[i].selected){
                    selectedMaps.push(vm.maps[i].name)
                }
            }
            StatsService.getPlayerStats(vm.playerName, limit.amount, selectedMaps).then(function(player){
                vm.player = player
                vm.selectedLimit = limit
            })
        }

        function selectMatch(row){
            vm.rowNumber = row
            var id = vm.matches[row].key
            if (vm.cache.get(id)){
                vm.matchKills = vm.cache.get(id)
            } else {
                StatsService.getMatchKills(id).then(function(matchKills){
                    vm.matchKills = matchKills
                    vm.cache.put(id, matchKills)
                })
            }
        }
    }

})();

(function() {

    var myApp = angular.module('myApp')

    myApp.controller("ShotChartViewCtrl", ShotChartViewCtrl)

    ShotChartViewCtrl.$inject = ['$stateParams', 'StatsService', '$cacheFactory']

    function ShotChartViewCtrl($stateParams, StatsService, $cacheFactory) {
        var vm = this
        vm.matchKey = $stateParams.matchKey

        var cacheName = 'dmg_cache'
        if ($cacheFactory.get(cacheName)){
            vm.cache = $cacheFactory.get(cacheName)
        } else {
            vm.cache = $cacheFactory(cacheName, { capacity: 25 });
        }

        activate();

        function activate() {
            var id = vm.matchKey
            if (vm.cache.get(id)){
                vm.matchKills = vm.cache.get(id)
            } else {
                StatsService.getMatchKills(id).then(function(matchKills){
                    vm.matchKills = matchKills
                    vm.cache.put(id, matchKills)
                })
            }
        }
    }

})();
