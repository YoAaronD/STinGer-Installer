"""Mirror the MRAs a Downloader database points at into a local folder the pipeline can read.

usage: python3 -I tools/mirror_db.py <db.json or db.json.zip> <out_dir>

For databases (like shmupfan's) whose MRAs live in other repos, each MRA's raw.githubusercontent
URL is fetched through git and written to <out_dir>/<db path>. Also writes:
  <out_dir>/.urls.json  - db path -> original URL, so build_db.py links to the real source
  <out_dir>/.rbf_list   - core names the database ships, for core_check.py
"""
import json, os, re, subprocess, sys, urllib.parse, zipfile

def load(path):
    if path.endswith(".zip"):
        z = zipfile.ZipFile(path)
        return json.load(z.open(z.namelist()[0]))
    return json.load(open(path, encoding="utf-8"))

def main(db_path, out):
    db = load(db_path)
    base = db.get("base_files_url", "")
    cache = os.path.join(out, ".repos")
    os.makedirs(cache, exist_ok=True)
    urls, rbfs = {}, []
    for p, f in db["files"].items():
        if p.lower().endswith(".rbf"):
            rbfs.append(os.path.basename(p)[:-4])
        if not p.lower().endswith(".mra"):
            continue
        url = f.get("url") or base + urllib.parse.quote(p)
        m = re.match(r"https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.+)", url)
        if not m:
            print("skip (not a GitHub raw URL):", p); continue
        owner, repo, ref, rpath = m.group(1), m.group(2), m.group(3), urllib.parse.unquote(m.group(4))
        rdir = os.path.join(cache, f"{owner}__{repo}")
        if not os.path.isdir(rdir):
            subprocess.run(["git", "clone", "-q", "--filter=blob:none", "--no-checkout",
                            f"https://github.com/{owner}/{repo}", rdir], check=True)
        blob = subprocess.run(["git", "-C", rdir, "show", f"{ref}:{rpath}"], capture_output=True)
        if blob.returncode:
            subprocess.run(["git", "-C", rdir, "fetch", "-q", "origin", ref], check=False)
            blob = subprocess.run(["git", "-C", rdir, "show", f"{ref}:{rpath}"], capture_output=True)
        if blob.returncode:
            print("skip (not found upstream):", p); continue
        dest = os.path.join(out, p)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "wb").write(blob.stdout)
        urls[p] = url
    json.dump(urls, open(os.path.join(out, ".urls.json"), "w"), indent=1)
    open(os.path.join(out, ".rbf_list"), "w").write("\n".join(rbfs) + "\n")
    print(f"mirrored {len(urls)} MRAs, {len(rbfs)} cores listed")

if __name__ == "__main__":
    main(*sys.argv[1:])
