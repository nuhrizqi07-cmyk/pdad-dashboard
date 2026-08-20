#!/usr/bin/env python3
"""Collector tiket CEISACare status Penyelesaian → JSON.
Disalin dari /tmp/collect_cica_all.py, path disesuaikan ke folder project.
Output: data/ceisacare_selesai_all.json (raw) — lalu update_data.py akan memprosesnya."""
import json
import os
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = "/home/noah/.hermes/scripts/ceisacare_token.json"
OUTPUT = os.path.join(BASE_DIR, "data", "ceisacare_selesai_all.json")
CHECKPOINT = OUTPUT  # pakai file sama sbg checkpoint resume

with open(TOKEN_FILE) as f:
    TOKEN = json.load(f)["access_token"]

API = "https://apis-gw.beacukai.go.id/cica-be"


def api_post(path, body=None, retries=5):
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(API + path, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", "Bearer " + TOKEN)
        data = json.dumps(body or {}).encode()
        try:
            with urllib.request.urlopen(req, data=data, timeout=30) as resp:
                return json.loads(resp.read().decode()), resp.status
        except urllib.error.HTTPError as e:
            last = e.code
            if e.code == 401:
                return None, 401
            if e.code < 500:
                return None, e.code
        except Exception:
            last = 0
        time.sleep(1.5 * (attempt + 1))
    return None, last


def api_get(path, retries=5):
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(API + path, method="GET")
        req.add_header("Accept", "application/json")
        req.add_header("Authorization", "Bearer " + TOKEN)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode()), resp.status
        except urllib.error.HTTPError as e:
            last = e.code
            if e.code == 401:
                return None, 401
            if e.code < 500:
                return None, e.code
        except Exception:
            last = 0
        time.sleep(1.5 * (attempt + 1))
    return None, last


def clean_html(text):
    if not text:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&#39;", "'", text)
    text = re.sub(r"&quot;", '"', text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def collect(max_pages=400):
    all_tickets = {}
    for page in range(1, max_pages + 1):
        resp, status = api_post(f"/layanan/v2/tiket/{page}", {})
        if status == 401:
            print("  TOKEN EXPIRED di listing — stop & resume nanti.", flush=True)
            break
        if status != 200 or not resp:
            print(f"  HTTP {status} at page {page}, stop.", flush=True)
            break
        items = resp.get("data", {}).get("items", [])
        if not items:
            print(f"  Page {page} kosong, stop.", flush=True)
            break
        for t in items:
            if t.get("idStatus") == 3:  # Penyelesaian
                uuid = t.get("uuidLayanan")
                if uuid:
                    all_tickets[uuid] = t
        if len(items) < 10:
            print(f"  Page {page}: {len(items)} items, stop.", flush=True)
            break
        if page % 25 == 0:
            print(f"  ...page {page}, tiket selesai terkumpul {len(all_tickets)}", flush=True)
        time.sleep(0.15)
    return all_tickets


def fetch_one(uuid_t):
    uuid, t = uuid_t
    detail, ds = api_get(f"/layanan/detail/{uuid}")
    if ds == 401:
        return "TOKEN_EXPIRED", uuid
    if not detail:
        return None, uuid
    d = detail.get("data", {})
    analisa = d.get("analisa", {}) or {}
    layanan = d.get("layanan", {}) or {}
    proseses = d.get("proseses", []) or []
    convs = d.get("conversations", []) or []

    catatan_list = []
    for p in proseses:
        catatan_list.append({
            "posisi": p.get("namaPosisi"),
            "status": p.get("namaStatusLayanan"),
            "catatan": clean_html(p.get("catatan")),
            "waktu": p.get("wkRekam") or p.get("tanggal"),
        })

    return {
        "uuid": uuid,
        "nomor_tiket": (layanan.get("nomorTiket") or t.get("nomorTiket") or "").split(" - ")[0],
        "tanggal": analisa.get("tanggal") or t.get("tanggal"),
        "kantor": (analisa.get("namaKantorPendek") or t.get("namaKantorPendek") or ""),
        "pelapor": (analisa.get("fullName") or t.get("fullName") or ""),
        "katalog": (analisa.get("namaKatalog") or t.get("namaKatalog") or ""),
        "masalah": (analisa.get("namaMasalah") or t.get("namaMasalah") or ""),
        "probis": (analisa.get("namaProbis") or t.get("namaProbis") or ""),
        "uraian": clean_html(analisa.get("uraian") or t.get("uraian")),
        "duktek": (analisa.get("namaDuktek") or t.get("namaDuktek") or ""),
        "proseses": catatan_list,
        "conversations": [
            {"nama": c.get("fullName"), "respon": clean_html(c.get("respon"))}
            for c in convs
        ],
    }, uuid


def fetch_details(all_tickets, workers=5):
    enriched = []
    uuids = list(all_tickets.keys())
    total = len(uuids)
    # resume dari checkpoint kalau ada
    if os.path.exists(CHECKPOINT):
        try:
            with open(CHECKPOINT) as f:
                done = json.load(f)
            done_uuids = {d.get("uuid") for d in done}
            uuids = [u for u in uuids if u not in done_uuids]
            enriched = done
            print(f"  Resume: {len(done)} sudah terkumpul, sisa {len(uuids)}", flush=True)
        except Exception:
            pass

    done_count = len(enriched)
    failed = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(fetch_one, (u, all_tickets[u])): u for u in uuids}
        for i, fut in enumerate(as_completed(futures)):
            try:
                result, uuid = fut.result()
            except Exception:
                result, uuid = None, futures[fut]
            if result == "TOKEN_EXPIRED":
                print(f"  TOKEN EXPIRED (setelah {done_count + i} diproses) — simpan & stop.", flush=True)
                for f2 in futures:
                    f2.cancel()
                break
            if result:
                enriched.append(result)
                done_count += 1
            else:
                failed.append(uuid)
            if done_count % 100 == 0:
                print(f"  ...detail {done_count}/{total}", flush=True)
                with open(CHECKPOINT, "w") as f:
                    json.dump(enriched, f, ensure_ascii=False, indent=1)

    with open(CHECKPOINT, "w") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=1)
    if failed:
        print(f"  Gagal {len(failed)} detail (akan di-retry run berikutnya via resume)", flush=True)
    return enriched


if __name__ == "__main__":
    print("Mengumpulkan daftar tiket selesai...", flush=True)
    tickets = collect()
    print(f"Total tiket Penyelesaian: {len(tickets)}", flush=True)
    details = fetch_details(tickets)
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(details, f, ensure_ascii=False, indent=1)
    print(f"DONE: {len(details)} tickets → {OUTPUT}", flush=True)
