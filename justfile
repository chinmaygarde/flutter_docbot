build: clean
	uv run docbot.py --repo https://github.com/flutter/flutter.git --doc-destination build

clean:
	rm -rf build

docker:
	docker build .
