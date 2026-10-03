#!/usr/bin/env python3
"""
bgtrack.py - live Hearthstone Battlegrounds tracker for the terminal.

Reads Hearthstone's Power.log while you play and shows the tavern, your board
and your hand with names, stats, tiers, types and card text.

Put this file next to bgminions.py (it reuses its card loading), then:
    python bgtrack.py
    python bgtrack.py --log "C:\\path\\to\\Power.log"
"""

import argparse
import glob
import os
import re
import sys
import time

import bgui as ui
from bgminions import load_cards, clean_text

RE_CREATE = re.compile(r"FULL_ENTITY - Creating ID=(\d+) CardID=(\S*)")
RE_SHOW = re.compile(r"SHOW_ENTITY - Updating Entity=(.+?) CardID=(\S*)\s*$")
RE_CHANGE = re.compile(r"TAG_CHANGE Entity=(.+?) tag=(\w+) value=(\S*)")
RE_TAG = re.compile(r"GameState\.DebugPrintPower\(\) -\s+tag=(\w+) value=(\S*)")
RE_BRACKET = re.compile(r"\[entityName=.+?\bplayer=\d+\]")


def default_logs_dir():
    if os.name == "nt":
        return r"C:\Program Files (x86)\Hearthstone\Logs"
    if sys.platform == "darwin":
        return "/Applications/Hearthstone/Logs"
    return ""


def newest_log(logs_dir):
    files = glob.glob(os.path.join(logs_dir, "*", "Power.log"))
    return max(files, key=os.path.getmtime) if files else None


class State:
    def __init__(self):
        self.reset()

    def reset(self):
        self.ents = {}
        self.cur = None

    def ent(self, i):
        return self.ents.setdefault(i, {"card": "", "tags": {}})

    def learn(self, s):
        """Turn an Entity=... field into an id, picking up card/controller hints."""
        s = s.strip()
        if s.isdigit():
            return int(s)
        if not s.startswith("["):
            return None
        m = re.search(r"\bid=(\d+)", s)
        if not m:
            return None
        i = int(m.group(1))
        e = self.ent(i)
        c = re.search(r"cardId=([^\s\]]*)", s)
        if c and c.group(1) and not e["card"]:
            e["card"] = c.group(1)
        p = re.search(r"player=(\d+)", s)
        if p and "CONTROLLER" not in e["tags"]:
            e["tags"]["CONTROLLER"] = p.group(1)
        return i

    def feed(self, line):
        if "DebugPrintPower()" not in line:
            return
        if "GameState.DebugPrintPower()" not in line:
            # PowerTaskList lags behind GameState, so only use it for hints.
            b = RE_BRACKET.search(line)
            if b:
                self.learn(b.group(0))
            return
        if line.rstrip().endswith("CREATE_GAME"):
            self.reset()
            return
        m = RE_TAG.search(line)
        if m and self.cur is not None:
            self.ent(self.cur)["tags"][m.group(1)] = m.group(2)
            return
        m = RE_CREATE.search(line)
        if m:
            self.cur = int(m.group(1))
            self.ent(self.cur)["card"] = m.group(2)
            return
        m = RE_SHOW.search(line)
        if m:
            i = self.learn(m.group(1))
            if i is not None:
                self.ent(i)["card"] = m.group(2)
            self.cur = i
            return
        m = RE_CHANGE.search(line)
        if m:
            i = self.learn(m.group(1))
            if i is not None:
                self.ent(i)["tags"][m.group(2)] = m.group(3)
            return
        self.cur = None  # any other line ends an entity block

    def controller_of(self, card_prefix):
        for e in self.ents.values():
            if e["card"].startswith(card_prefix) and "CONTROLLER" in e["tags"]:
                return e["tags"]["CONTROLLER"]
        return None

    def minions(self, ctrl, zone, by_id):
        out = []
        if ctrl is None:
            return out
        for e in self.ents.values():
            t = e["tags"]
            if (t.get("ZONE") == zone and t.get("CONTROLLER") == ctrl
                    and by_id.get(e["card"], {}).get("type") == "MINION"):
                out.append((int(t.get("ZONE_POSITION", 0) or 0), e))
        return [e for _, e in sorted(out, key=lambda x: x[0])]


def describe(e, by_id):
    c = by_id.get(e["card"])
    if not c:
        return None
    t = e["tags"]
    races = c.get("races") or ([c["race"]] if c.get("race") else [])
    return {
        "name": c.get("name", "?"),
        "atk": t.get("ATK", c.get("attack", "?")),
        "hp": t.get("HEALTH", c.get("health", "?")),
        "tier": c.get("techLevel", "?"),
        "races": [r.title().replace("_", " ") for r in races] or ["Neutral"],
        "text": clean_text(c.get("text")),
        "golden": t.get("PREMIUM") == "1" or "battlegroundsNormalDbfId" in c,
    }


def section(title, ents, by_id, color):
    lines = [ui.header(title, len(ents), color)]
    if not ents:
        lines.append(ui.c("  (empty)", "90"))
    for n, e in enumerate(ents, 1):
        d = describe(e, by_id)
        if d is None:
            lines.append(f"{n:>2}  " + ui.c(f"? {e['card'] or 'unknown card'}", "91"))
        else:
            lines += ui.minion_lines(num=n, **d)
    return lines


def render(st, by_id):
    bob = st.controller_of("TB_BaconShopBob")
    me = st.controller_of("TB_BaconShop_8P_PlayerE")
    lines = [ui.banner("BATTLEGROUNDS TRACKER"), ""]
    lines += section("TAVERN", st.minions(bob, "PLAY", by_id), by_id, "1;93")
    lines += [""] + section("YOUR BOARD", st.minions(me, "PLAY", by_id), by_id, "1;92")
    lines += [""] + section("YOUR HAND", st.minions(me, "HAND", by_id), by_id, "1;96")
    counts = {}
    for e in st.ents.values():
        tg = e["tags"]
        if tg.get("ZONE") == "PLAY" and by_id.get(e["card"], {}).get("type") == "MINION":
            k = tg.get("CONTROLLER", "?")
            counts[k] = counts.get(k, 0) + 1
    play = " ".join(f"{k}:{v}" for k, v in sorted(counts.items()))
    lines += ["",
              ui.c(f"entities={len(st.ents)} bob_ctrl={bob} you_ctrl={me}", "90"),
              ui.c(f"minions in play by controller -> {play or 'none'}", "90"),
              ui.c("Ctrl+C to quit", "90")]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Live Battlegrounds tracker.")
    ap.add_argument("--log", help="path to Power.log (default: newest one found)")
    ap.add_argument("--no-color", action="store_true", help="turn off colors")
    ap.add_argument("--logs-dir", default=default_logs_dir(),
                    help="Hearthstone Logs folder")
    args = ap.parse_args()
    ui.set_enabled(not args.no_color)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    by_id = {c["id"]: c for c in load_cards()}
    path = args.log or newest_log(args.logs_dir)
    if not path:
        sys.exit("Couldn't find Power.log. Use --log PATH or --logs-dir PATH.")

    st = State()
    f = open(path, "rb")
    sys.stdout.write("\033[2J\033[H")
    print(f"Reading {path} (catching up, big logs can take a few seconds)...")
    last_shown, last_check, count = None, time.time(), 0
    try:
        while True:
            pos = f.tell()
            line = f.readline()
            if line and not line.endswith(b"\n"):
                f.seek(pos)  # half-written line, try again shortly
                line = b""
            if line:
                st.feed(line.decode("utf-8", "replace"))
                count += 1
                if count % 200000 == 0:
                    print(f"  ...{count:,} lines", flush=True)
                continue
            text = render(st, by_id)
            if text != last_shown:
                body = text.replace("\n", "\033[K\n")
                sys.stdout.write("\033[H" + body + "\033[K\n\033[J")
                sys.stdout.flush()
                last_shown = text
            if not args.log and time.time() - last_check > 3:
                last_check = time.time()
                new = newest_log(args.logs_dir)
                if new and new != path:
                    path = new
                    f.close()
                    f = open(path, "rb")
                    st.reset()
            time.sleep(0.3)
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
