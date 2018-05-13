( function() {

    var myApp = angular.module('myApp')

    myApp.factory('StatsService', StatsService)

    StatsService.$inject = ['$resource']

    function StatsService($resource) {

	    var statsResource = $resource('api/stats', {}, {
			get: { method: 'GET', url: 'api/stats/:name', params: {name: "@name"}, isArray: false },
            query: { method: 'GET', params: {}, isArray: true }
	    })

	    var playerResource = $resource('api/player/:name', {name: "@name"}, {
			get: { method: 'GET', params: {}, isArray: false }
	    })

	    var weaponStatsResource = $resource('api/weapons', {}, {
			query: { method: 'GET', params: {}, isArray: true },
			get: { method: 'GET', params: {}, isArray: false }
	    })

        return {
            getStats: getStats,
            getPlayerStats: getPlayerStats,
            getPlayerMatches: getPlayerMatches,
            getWeaponStats: getWeaponStats,
            getPlayerWeapons: getPlayerWeapons
        }

        function getWeaponStats(){
            return weaponStatsResource.query().$promise
        }

        function getStats(type) {
            return statsResource.query({type: type}).$promise
        }

        function getPlayerStats(name, limit){
            return statsResource.get({name: name, limit:limit}).$promise
        }

        function getPlayerMatches(name) {
            return playerResource.query({name: name}).$promise
        }

        function getPlayerWeapons(name) {
            return weaponStatsResource.get({name:name}).$promise
        }

    }

})();