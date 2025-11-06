# Flutter Engine Documentation Generator

## Website

A self-updating feed of the [Doxygen documentation generated from Flutter Engine source is located here](https://engine.chinmaygarde.com).

## Dash Docset

A Dash Docset from the same documentation is also generated and the following self-updating feed can be added to Doxygen:

```sh
https://engine.chinmaygarde.com/FlutterEngine.xml
```

Subscribe to this feed in Dash using `Preferences` -> `Downloads` -> `+` icon at the bottom, and pasting in that feed.

![Feed](./assets/feed.webp)
![Docset](./assets/docset.webp)

## Locally Hosted

To host the documentation server yourself, use Docker to run the most up-to-date container.

```sh
docker run --platform linux/amd64 -p 8080:80 ghcr.io/chinmaygarde/flutter_docbot:main
```

The documentation will be available at port 8080.
