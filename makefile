deploy:
	docker build -t us-central1-docker.pkg.dev/savvy-equator-441813-c3/ca-api/caapi . --platform=linux/amd64
	docker push us-central1-docker.pkg.dev/savvy-equator-441813-c3/ca-api/caapi