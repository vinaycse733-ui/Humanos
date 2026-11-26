# HumanOS developer preview

Requires Python 3.11+ and a running local Ollama installation.

```sh
ollama pull llama3.2
python3 -m humanos "Hello"
python3 -m unittest discover -s tests
```

The CLI sends prompts only to the loopback Ollama endpoint. It does not execute model output, store memory, or send telemetry itself. Ollama installation and model downloads are external prerequisites. Unit tests mock the model server; actual inference requires a separate local smoke test. This is an early development snapshot, not a stable release.
