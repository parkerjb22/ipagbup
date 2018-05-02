( function() {

    var myApp = angular.module('myApp')

    myApp.factory('StatsService', StatsService)

    StatsService.$inject = ['$resource']

    function StatsService($resource) {

	    var statsResource = $resource('api/stats', {}, {
			get: { method: 'GET', params: {}, isArray: false },
            query: { method: 'GET', params: {}, isArray: true }
	    })

        return {
            getStats: getStats,
        }

        function getStats() {
            return statsResource.query().$promise
        }

    }

})();