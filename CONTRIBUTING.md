# Contributing

Contributions are welcome. Here is how to get started.

## Setup

```
git clone https://github.com/Andrew-most-likely/l2w.git
cd l2w
pip install -e .
pip install pytest
```

## Running tests

```
pytest tests/ -v
```

All tests must pass before submitting a pull request.

## Adding a command

1. Open `l2w/commands.py`
2. Add a `CommandDef` entry to `COMMAND_MAP`
3. If the command needs special argument handling (beyond simple flag substitution), add a `_handle_<command>` method to the `Translator` class in `translator.py`
4. Add tests in `tests/test_translator.py`

## Pull requests

- Keep changes focused - one command or feature per PR
- Include tests for any new translation logic
- Run `pytest tests/ -v` and confirm everything passes

## Reporting bugs

Open an issue and include:
- The `l2w` command you ran
- The translated Windows command that was produced (use `--dry-run` to check)
- What you expected instead
- Your Windows version (`winver`)
