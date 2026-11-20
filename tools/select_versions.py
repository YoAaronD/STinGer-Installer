"""Pick one MRA per game: Japanese first, newest revision within the region.

usage: python3 -I tools/select_versions.py <classified.csv> <prefer.csv> <out.csv> [db_priority=distribution,jotego,coinop]

Ranking per game (lower wins):
  1. pinned in prefer.csv
  2. not a bootleg / hack / prototype / "special ver." / homebrew
  3. region: Japan < World < everything else
  4. newest date or version found in the MRA name ("older" counts as oldest)
  5. database priority, then the MRA that its database ships as main
"""
import csv, re, sys, collections, os

MONTHS = {m: i for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split(), 1)}

def group_key(row):
    t = row["title"] or row["mra_name"]
    if row["source"] == "db category" or row["title"] != row["mra_name"]:
        base = t
    else:
        base = t.split(" (")[0]
    base = re.sub(r"\(.*?\)|\[.*?\]", "", base)
    base = re.sub(r"\b(set \d|ver\.? ?\w+|rev\.? ?\w+)\b", "", base, flags=re.I)
    return re.sub(r"[^a-z0-9]", "", base.lower())

def is_japan(row):
    n = row["mra_name"] + " " + os.path.basename(row["mra_path"])
    return row["region"].strip().lower().startswith("japan") or bool(
        re.search(r"\((?:[^)]*\b)?(japan|jp|jpn)\b", n, re.I))

def is_world(row):
    n = row["mra_name"]
    return row["region"].strip().lower() == "world" or bool(re.search(r"\(world\b", n, re.I))

def junk(row):
    n = (row["mra_name"] + " " + row["mra_path"]).lower()
    return bool(re.search(r"\[(bl|hb|h)\]|bootleg|hack|prototype|special ver|trainer|satsuei|"
                          r"\beasier\b|\bharder\b|arrange|location test|\bdemo\b|practice rom|visibility mod|round select|"
                          r"ship color|no bgm|no discomen|show time|roppaku|rosy future|& knuckles|\(hack\)|\bmod\]", n))

def hackish(row):
    """Fan hacks, mods and trainers. Prototypes and bootlegs of otherwise-lost games are NOT hacks."""
    n = (row["mra_name"] + " " + row["mra_path"]).lower()
    if "official hack" in n: return False
    return bool(re.search(r"\(hack\)|\[h\]|hack\)|\bmod\]|visibility mod|round select|ship color|no bgm|"
                          r"no discomen|show time|roppaku|rosy future|& knuckles|faster, harder", n))

def newness(name):
    """Return a sortable tuple: bigger = newer."""
    n = name.lower()
    if "older" in n: return (0,)
    if re.search(r"\bold\b", n): return (0, 1)
    m = re.search(r"\b(?:mon|tue|wed|thu|fri|sat|sun) (\w{3}) (\d{1,2}) (\d{4})", n)
    newer = 1 if re.search(r"\bnewer?\b", n) else 0
    if m and m.group(1) in MONTHS: return (3, int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)), newer)
    m = re.search(r"(\d{4})[./](\d{2})[./](\d{2})", n)
    if m: return (3, int(m.group(1)), int(m.group(2)), int(m.group(3)), newer)
    m = re.search(r"\b(\d{2})(\d{2})(\d{2})\b", n)  # Capcom-style YYMMDD
    if m:
        y = int(m.group(1)); return (3, 1900 + y if y > 70 else 2000 + y, int(m.group(2)), int(m.group(3)))
    m = re.search(r"\b(?:ver(?:sion)?\.?|v|rev\.?) ?(\d+)(?:\.(\d+))?", n)
    if m: return (2, int(m.group(1)), int(m.group(2) or 0))
    m = re.search(r"\b([a-d]) version\b|\bversion ([a-d])\b", n)
    if m: return (2, ord((m.group(1) or m.group(2))) - 96)
    if re.search(r"\bnewer?\b", n): return (1, 1)
    return (1,)

def main(inp, pref_csv, out, prio="db_priority=distribution,jotego,coinop,ongo", split_csv=None):
    split_csv = split_csv or os.path.join(os.path.dirname(os.path.abspath(pref_csv)), "split.csv")
    splits = [r["pattern"] for r in csv.DictReader(l for l in open(split_csv) if not l.startswith("#"))] if os.path.exists(split_csv) else []
    prio = prio.split("=", 1)[1].split(",")
    pinned = {r["setname"] for r in csv.DictReader(l for l in open(pref_csv) if not l.startswith("#"))}
    rows = list(csv.DictReader(open(inp, encoding="utf-8")))
    # Union-find: an MRA joins its MAME parent, its _alternatives folder, and same-named mains.
    # Practice ROMs and trainers sit off to the side: listed individually, never picked as a game's version.
    PRACTICE = re.compile(r"practice rom|(?<!bradley )trainer", re.I)
    practice = [dict(r, tier="practice", pick_reason="practice ROM / trainer", other_versions="0", also_in="")
                for r in rows if PRACTICE.search(r["mra_name"])]
    rows = [r for r in rows if not PRACTICE.search(r["mra_name"])]
    by_set = {r["setname"]: r for r in rows if r["setname"]}
    # Shooter tier of each _alternatives folder, so split-off games and unlisted alts keep it.
    folder_tier = {}
    for r in rows:
        parts = r["mra_path"].split("/")
        if r["tier"] != "other":
            key = parts[parts.index("_alternatives") + 1].lstrip("_") if "_alternatives" in parts else os.path.basename(r["mra_path"])[:-4]
            folder_tier[group_key({"title": key, "mra_name": key, "source": ""})] = r["tier"]
    for r in rows:
        parts = r["mra_path"].split("/")
        if r["tier"] == "other" and r["in_db"] == "no" and "_alternatives" in parts:
            f = parts[parts.index("_alternatives") + 1].lstrip("_")
            r["tier"] = folder_tier.get(group_key({"title": f, "mra_name": f, "source": ""}), "other")
    up = {}
    def find(x):
        while up.setdefault(x, x) != x:
            up[x] = up[up[x]]; x = up[x]
        return x
    def join(a, b): up[find(a)] = find(b)
    for i, r in enumerate(rows):
        me = f"#{i}"
        hit = next((p for p in splits if re.search(p, r["mra_name"], re.I)), None)
        if hit:  # its own game: don't follow folder/parent links
            join(me, "split:" + group_key({"title": r["mra_name"], "mra_name": r["mra_name"], "source": ""})); continue
        if r["setname"]: join(me, "set:" + r["setname"])
        if r["parent"]:
            # Different games on shared hardware can name each other as parent (Saturn -> Blueprint).
            # Only follow the link when it can't merge a shooter with a non-shooter that the DB knows.
            p = by_set.get(r["parent"])
            if not p or r["in_db"] == "no" or p["in_db"] == "no" or (r["tier"] == "other") == (p["tier"] == "other"):
                join(me, "set:" + r["parent"])
        parts = r["mra_path"].split("/")
        if "_alternatives" in parts:
            folder = parts[parts.index("_alternatives") + 1].lstrip("_")
            join(me, "key:" + group_key({"title": folder, "mra_name": folder, "source": ""}))
        else:
            join(me, "key:" + group_key(r))
    groups = collections.defaultdict(list)
    for i, r in enumerate(rows):
        groups[find(f"#{i}")].append(r)
    picks = []
    for key, g in groups.items():
        def rank(r):
            region = 0 if is_japan(r) else 1 if is_world(r) else 2
            nw = newness(r["mra_name"])
            return (r["setname"] not in pinned, junk(r), region, tuple(-x for x in nw),
                    prio.index(r["database"]) if r["database"] in prio else 9, r["alternative"] == "yes")
        g.sort(key=rank)
        best = dict(g[0])
        # The group's tier is its most specific shooter tier: an untagged alt shouldn't drag Raiden II into 'unsorted'.
        stg = [r["tier"] for r in g if r["tier"] != "other"]
        if stg:
            best["tier"] = min(stg, key=["core", "fixed", "multidirectional", "overhead", "3d", "unsorted"].index)
        if hackish(best):  # only hacks/mods in this group: keep them out of the main lists
            best["tier"] = "hack"
        best["pick_reason"] = ("pinned in prefer.csv" if best["setname"] in pinned else
                               "Japan" if is_japan(best) else "World (no Japanese set)" if is_world(best)
                               else "no region in name" if not re.search(r"\((usa?|europe|korea|asia|hong kong|china|taiwan|germany)", best["mra_name"], re.I)
                               else "no Japanese or World set")
        best["other_versions"] = len(g) - 1
        best["also_in"] = ",".join(sorted({r["database"] for r in g} - {best["database"]}))
        picks.append(best)
    picks += practice
    picks.sort(key=lambda r: r["title"].lower())
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(picks[0]))
        w.writeheader(); w.writerows(picks)
    print("games", len(picks), collections.Counter(p["pick_reason"] for p in picks).most_common())

if __name__ == "__main__":
    main(*sys.argv[1:])
