( function() {

    var myApp = angular.module('myApp')

    myApp.factory('StatsService', StatsService)

    StatsService.$inject = ['$resource']

    function StatsService($resource) {

	    var statsResource = $resource('api/stats', {}, {
			get: { method: 'GET', params: {}, isArray: false },
            query: { method: 'GET', params: {}, isArray: true }
	    })

	    var playerResource = $resource('api/player/:name', {name: "@name"}, {
			get: { method: 'GET', params: {}, isArray: false }
	    })

        return {
            getStats: getStats,
            getPlayerMatches: getPlayerMatches
        }

        function getStats() {
            return statsResource.query().$promise
        }

        function getPlayerMatches(name) {
            return playerResource.query({name: name}).$promise
        }

    }

})();