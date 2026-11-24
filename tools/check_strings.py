"""Check street_fade_fix_1's strings.lua and mod.lua.

Loads both files with a Lua interpreter (`lua` on PATH, or LUA=<path>; without
one the check is skipped, not failed) and asserts:
  * mod.lua loads with the game's `_()` stubbed, and its description key exists;
  * every language table holds a non-empty string for every key mod.lua asks for;
  * the language codes are the ones in LANGUAGES (a typo would silently never be
    used by the game), `en` is among them, and no table is empty;
  * no description contains a raw control character or a leading/trailing blank.

    python tools/check_strings.py
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'street_fade_fix_1'
# the codes TpF2 mods use for their strings.lua tables
LANGUAGES = {'en', 'de', 'fr', 'es', 'it', 'nl', 'pl', 'cs', 'ru', 'uk', 'tr',
             'pt_BR', 'ja', 'ko', 'zh_CN', 'zh_TW'}

LUA_SNIPPET = r'''
local modPath, stringsPath = arg[1], arg[2]
local asked = {}
function _(k) asked[#asked + 1] = k; return k end
dofile(modPath)
local info = data().info
assert(type(info.description) == "string", "mod.lua: description")
dofile(stringsPath)
local langs = data()
local out = {}
local codes = {}
for code in pairs(langs) do codes[#codes + 1] = code end
table.sort(codes)
for _, code in ipairs(codes) do
    local t = langs[code]
    local n = 0
    for k, v in pairs(t) do n = n + 1; assert(type(v) == "string", code .. "." .. tostring(k)) end
    out[#out + 1] = code .. "\t" .. n
    for _, key in ipairs(asked) do
        local v = t[key]
        assert(type(v) == "string" and v ~= "", code .. " lacks " .. key)
        assert(v == v:match("^%s*(.-)%s*$"), code .. "." .. key .. ": leading/trailing blank")
        assert(not v:find("[%c]"), code .. "." .. key .. ": control character")
    end
end
print(table.concat(asked, ","))
print(table.concat(out, "\n"))
'''


def lua_exe():
    return os.environ.get('LUA') or shutil.which('lua') or shutil.which('lua5.4') or shutil.which('luajit')


def main():
    exe = lua_exe()
    if not exe:
        print('SKIP: no Lua interpreter (put `lua` on PATH or set LUA)')
        return
    r = subprocess.run([exe, '-e', LUA_SNIPPET.replace('arg[1]', repr(str(MOD / 'mod.lua'))).replace('arg[2]', repr(str(MOD / 'strings.lua')))],
                       capture_output=True, text=True, encoding='utf-8')
    if r.returncode:
        sys.exit('FAIL: ' + (r.stderr.strip() or r.stdout.strip()))
    lines = r.stdout.splitlines()
    asked = [k for k in lines[0].split(',') if k]
    found = {l.split('\t')[0]: int(l.split('\t')[1]) for l in lines[1:] if l}
    missing = LANGUAGES - set(found)
    unknown = set(found) - LANGUAGES
    assert 'en' in found, 'no en table'
    assert not unknown, f'unknown language codes (typo?): {sorted(unknown)}'
    assert not missing, f'languages without a table: {sorted(missing)}'
    assert asked, 'mod.lua asks for no string'
    assert all(n > 0 for n in found.values()), 'empty table'
    print(f'PASS: mod.lua asks for {asked}; {len(found)} languages each hold them: {", ".join(sorted(found))}')


if __name__ == '__main__':
    main()
