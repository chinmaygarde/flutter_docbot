build: clean
	python3 ./docbot.py --repo https://github.com/flutter/flutter.git --doc-destination build

clean:
	rm -rf build

upload: build
	gsutil cp build/FlutterEngine.tgz gs://public.chinmaygarde.com/docs/flutter_engine/FlutterEngine.tgz
	gsutil cp build/FlutterEngine.xml gs://public.chinmaygarde.com/docs/flutter_engine/FlutterEngine.xml
