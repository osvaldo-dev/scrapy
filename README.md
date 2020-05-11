# But
command line:
	scrapy crawl but

deploying to scrapyd server
	pip install scrapyd-client
	scrapyd-deploy default

	#Schedule a spider run
	curl http://localhost:6800/schedule.json -d project=but_fr -d spider=but


	#Cancel a spider run
	curl http://localhost:6800/cancel.json -d project=but_fr -d job=JOBID
