.PHONY: help test fmt harbor nsq-up nsq-down pgplay compose-up compose-down zip

help:
	@printf '%s\n' \
	  'make test        Run all Go tests' \
	  'make fmt         Format all Go files' \
	  'make harbor      Run Harbor Observer on :8081' \
	  'make nsq-up      Start NSQ, API, worker, and NSQ Admin' \
	  'make nsq-down    Stop the NSQ stack' \
	  'make pgplay      Start the browser PostgreSQL workbench' \
	  'make compose-up  Start the complete Docker stack' \
	  'make compose-down Stop the complete Docker stack'

test:
	go test ./apps/harbor-observer/... ./apps/nsq-reliable-worker/...

fmt:
	gofmt -w $$(find apps/harbor-observer apps/nsq-reliable-worker -name '*.go')

harbor:
	cd apps/harbor-observer && go run ./cmd/harbor-observer

nsq-up:
	docker compose up --build nsqlookupd nsqd nsqadmin nsq-api nsq-worker

nsq-down:
	docker compose down

pgplay:
	cd apps/pgplay-recipes && npm install && npm run dev

compose-up:
	docker compose up --build

compose-down:
	docker compose down
