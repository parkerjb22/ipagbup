(function(){
	'use strict';   // See note about 'use strict'; below

	var myApp = angular.module('myApp', ['ngResource', 'ui.router']);

	myApp.config(['$stateProvider', '$urlRouterProvider', function($stateProvider, $urlRouterProvider) {

		$urlRouterProvider.otherwise('/stats');

		$stateProvider
			.state('index', {
	          abstract: true,
	          views: {
	            '@' : { templateUrl: '../static/partials/layout.html' }
	          }
	        })
			.state('stats', {
				url:"/stats",
				views: {
					"@": { templateUrl: '../static/partials/stats.html', controller: 'StatsViewCtrl', controllerAs: "vm" },
				}
	        })
			.state('stats2', {
				url:"/stats/:playerId",
				views: {
					"@": { templateUrl: '../static/partials/stats.html', controller: 'StatsViewCtrl', controllerAs: "vm" },
				}
	        })
			.state('player/', {
				url:"/player/:playerName",
				views: {
					"@": { templateUrl: '../static/partials/player.html', controller: 'PlayerViewCtrl', controllerAs: "vm" },
				}
			});
	    }]);
})();


