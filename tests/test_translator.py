"""Unit tests for the Translator module."""

import pytest
from l2w.translator import Translator, TranslationError


@pytest.fixture
def t():
    return Translator()


# ---------------------------------------------------------------------------
# Basic translations
# ---------------------------------------------------------------------------

def test_ls_basic(t):
    assert t.translate(["ls"]) == "dir"


def test_ls_hidden(t):
    result = t.translate(["ls", "-a"])
    assert result == "dir /a"


def test_ls_path(t):
    result = t.translate(["ls", "C:\\Users"])
    assert "C:\\Users" in result


def test_pwd(t):
    assert t.translate(["pwd"]) == "cd"


def test_clear(t):
    assert t.translate(["clear"]) == "cls"


def test_echo(t):
    result = t.translate(["echo", "hello world"])
    assert result.startswith("echo")
    assert "hello world" in result


def test_whoami(t):
    assert t.translate(["whoami"]) == "whoami"


# ---------------------------------------------------------------------------
# cp / copy
# ---------------------------------------------------------------------------

def test_cp_simple(t):
    result = t.translate(["cp", "a.txt", "b.txt"])
    assert result.startswith("copy")
    assert "a.txt" in result and "b.txt" in result


def test_cp_force(t):
    result = t.translate(["cp", "-f", "a.txt", "b.txt"])
    assert "/y" in result


def test_cp_recursive(t):
    result = t.translate(["cp", "-r", "src/", "dest/"])
    assert result.startswith("xcopy")
    assert "/e" in result and "/i" in result


def test_cp_recursive_force(t):
    result = t.translate(["cp", "-r", "-f", "src/", "dest/"])
    assert "xcopy" in result
    assert "/y" in result


# ---------------------------------------------------------------------------
# mv / move
# ---------------------------------------------------------------------------

def test_mv_basic(t):
    result = t.translate(["mv", "old.txt", "new.txt"])
    assert result.startswith("move")
    assert "old.txt" in result and "new.txt" in result


def test_mv_force(t):
    result = t.translate(["mv", "-f", "old.txt", "new.txt"])
    assert "/y" in result


# ---------------------------------------------------------------------------
# rm / del / rmdir
# ---------------------------------------------------------------------------

def test_rm_file(t):
    result = t.translate(["rm", "file.txt"])
    assert result.startswith("del")


def test_rm_force(t):
    result = t.translate(["rm", "-f", "file.txt"])
    assert result.startswith("del") and "/f" in result


def test_rm_recursive(t):
    result = t.translate(["rm", "-r", "mydir"])
    assert result.startswith("rmdir") and "/s" in result


def test_rm_rf(t):
    result = t.translate(["rm", "-rf", "mydir"])
    assert "rmdir" in result and "/s" in result and "/q" in result


# ---------------------------------------------------------------------------
# touch
# ---------------------------------------------------------------------------

def test_touch_single(t):
    result = t.translate(["touch", "newfile.txt"])
    assert "type nul" in result and "newfile.txt" in result


def test_touch_multiple(t):
    result = t.translate(["touch", "a.txt", "b.txt"])
    assert "a.txt" in result and "b.txt" in result
    assert "&&" in result


def test_touch_no_args(t):
    with pytest.raises(TranslationError):
        t.translate(["touch"])


# ---------------------------------------------------------------------------
# grep / findstr
# ---------------------------------------------------------------------------

def test_grep_basic(t):
    result = t.translate(["grep", "pattern", "file.txt"])
    assert result.startswith("findstr")


def test_grep_case_insensitive(t):
    result = t.translate(["grep", "-i", "error", "log.txt"])
    assert "/i" in result


def test_grep_recursive(t):
    result = t.translate(["grep", "-r", "TODO", "."])
    assert "/s" in result


# ---------------------------------------------------------------------------
# head / tail
# ---------------------------------------------------------------------------

def test_head_default(t):
    result = t.translate(["head", "file.txt"])
    assert "TotalCount 10" in result and "file.txt" in result


def test_head_n_flag(t):
    result = t.translate(["head", "-n", "20", "file.txt"])
    assert "TotalCount 20" in result


def test_head_short_n(t):
    result = t.translate(["head", "-5", "file.txt"])
    assert "TotalCount 5" in result


def test_tail_default(t):
    result = t.translate(["tail", "file.txt"])
    assert "Tail 10" in result


def test_tail_follow(t):
    result = t.translate(["tail", "-f", "file.txt"])
    assert "-Wait" in result


# ---------------------------------------------------------------------------
# sleep
# ---------------------------------------------------------------------------

def test_sleep(t):
    result = t.translate(["sleep", "5"])
    assert result == "timeout /t 5 /nobreak"


# ---------------------------------------------------------------------------
# wc
# ---------------------------------------------------------------------------

def test_wc_lines(t):
    result = t.translate(["wc", "-l", "file.txt"])
    assert "Measure-Object" in result and "-Line" in result


def test_wc_default(t):
    result = t.translate(["wc", "file.txt"])
    assert "-Line" in result and "-Word" in result and "-Character" in result


# ---------------------------------------------------------------------------
# kill / killall
# ---------------------------------------------------------------------------

def test_kill_basic(t):
    result = t.translate(["kill", "1234"])
    assert "taskkill" in result and "1234" in result


def test_kill_force(t):
    result = t.translate(["kill", "-9", "1234"])
    assert "/f" in result


def test_killall_basic(t):
    result = t.translate(["killall", "notepad.exe"])
    assert "taskkill" in result and "notepad.exe" in result


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_unknown_command(t):
    with pytest.raises(TranslationError):
        t.translate(["notacommand"])


def test_empty_tokens(t):
    with pytest.raises(ValueError):
        t.translate([])


# ---------------------------------------------------------------------------
# Custom mapping override
# ---------------------------------------------------------------------------

def test_custom_mapping():
    from l2w.commands import CommandDef
    extra = {"myls": CommandDef(windows="dir /w", description="wide list")}
    t = Translator(extra_map=extra)
    result = t.translate(["myls"])
    assert result == "dir /w"


def test_custom_override_builtin():
    from l2w.commands import CommandDef
    extra = {"ls": CommandDef(windows="Get-ChildItem", description="PS list")}
    t = Translator(extra_map=extra)
    result = t.translate(["ls"])
    assert result == "Get-ChildItem"
