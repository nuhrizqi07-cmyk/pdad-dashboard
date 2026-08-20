#!/usr/bin/env python3
"""Update data Dashboard PDAD — satu command untuk refresh tiket + SLA + push.
Alur:
  1. Cek token CEISACare (valid? expired?)
  2. Collect tiket Penyelesaian terbaru (collect_cica.py)
  3. Hitung ulang SLA → tickets_clean.json (prep_data.py)
  4. Opsional: sintesis ulang masalah baru (synth_llm.py, butuh DeepSeek)
  5. Opsional: commit & push ke GitHub

Usage:
  python update_data.py                # collect + prep, tanpa push
  python update_data.py --push         # + commit push GitHub
  python update_data.py --synth        # + sintesis masalah baru (LLM)
  python update_data.py --check-token  # hanya cek status token
"""
import argparse
import datetime
import json
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = "/home/noah/.hermes/scripts/ceisacare_token.json"
VENV_PY = "/run/media/noah/Data/My SaaS/project-perbaikan/venv/bin/python"


def check_token():
    """Cek status token CEISACare. Return (ok, msg)."""
    if not os.path.exists(TOKEN_FILE):
        return False, "Token file tidak ada — perlu login ulang."
    with open(TOKEN_FILE) as f:
        tok = json.load(f)
    exp = tok.get("exp")
    if not exp:
        return False, "Token tidak punya field exp."
    exp_dt = datetime.datetime.fromtimestamp(exp)
    sisa = exp_dt - datetime.datetime.now()
    if sisa.total_seconds() <= 0:
        return False, f"Token EXPIRED sejak {exp_dt:%Y-%m-%d %H:%M:%S}."
    return True, f"Token valid sampai {exp_dt:%Y-%m-%d %H:%M:%S} (sisa {sisa})."


def run_collect():
    print("\n[1/3] Mengumpulkan tiket Penyelesaian CEISACare...")
    r = subprocess.run([VENV_PY, os.path.join(BASE_DIR, "collect_cica.py")],
                       cwd=BASE_DIR)
    if r.returncode != 0:
        print("  ⚠️ Collector exit != 0 — mungkin token expired di tengah.")
    return r.returncode == 0


def run_prep():
    print("\n[2/3] Menghitung ulang SLA → tickets_clean.json...")
    r = subprocess.run([VENV_PY, os.path.join(BASE_DIR, "prep_data.py")],
                       cwd=BASE_DIR)
    return r.returncode == 0


def run_synth():
    print("\n[2.5/3] Sintesis ulang masalah baru (DeepSeek)...")
    # synth_llm.py ada di buku-saku-ceisacare; jalankan dengan venv
    synth_script = "/run/media/noah/Data/My SaaS/buku-saku-ceisacare/synth_llm.py"
    if not os.path.exists(synth_script):
        print("  ⚠️ synth_llm.py tidak ditemukan, skip.")
        return True
    r = subprocess.run([VENV_PY, synth_script], cwd=os.path.dirname(synth_script))
    # hasil synth_results.json harus disalin ke data/
    src = "/tmp/synth_results.json"
    if os.path.exists(src):
        dst = os.path.join(BASE_DIR, "data", "synth_results.json")
        import shutil
        shutil.copy(src, dst)
        print("  ✓ synth_results.json disalin ke data/")
    return r.returncode == 0


def count_tickets():
    p = os.path.join(BASE_DIR, "data", "tickets_clean.json")
    if os.path.exists(p):
        with open(p) as f:
            return len(json.load(f))
    return 0


def git_push():
    print("\n[3/3] Commit & push ke GitHub...")
    subprocess.run(["git", "add", "-A"], cwd=BASE_DIR, check=False)
    today = datetime.date.today().isoformat()
    r = subprocess.run(
        ["git", "commit", "-q", "-m", f"chore: update data tiket {today} ({count_tickets()} tiket)"],
        cwd=BASE_DIR, check=False,
    )
    if r.returncode == 0:
        subprocess.run(["git", "push", "-q"], cwd=BASE_DIR, check=False)
        print("  ✓ pushed ke GitHub")
    else:
        print("  (tidak ada perubahan / commit kosong, skip push)")


def main():
    parser = argparse.ArgumentParser(description="Update data Dashboard PDAD")
    parser.add_argument("--push", action="store_true", help="Commit & push ke GitHub setelah update")
    parser.add_argument("--synth", action="store_true", help="Jalankan sintesis masalah baru (LLM)")
    parser.add_argument("--check-token", action="store_true", help="Hanya cek status token")
    args = parser.parse_args()

    ok, msg = check_token()
    print(f"Token CEISACare: {msg}")
    if args.check_token:
        return
    if not ok:
        print("\n❌ Token expired. Login ulang dulu:")
        print("   1. Jalankan script login CEISACare (butuh kode 2FA)")
        print("   2. Atau minta asisten: 'login CEISACare'")
        sys.exit(1)

    before = count_tickets()
    print(f"Jumlah tiket sebelum update: {before:,}")

    ok_collect = run_collect()
    ok_prep = run_prep()
    after = count_tickets()
    delta = after - before

    if args.synth:
        run_synth()

    print("\n" + "=" * 50)
    print(f"  Tiket sebelum: {before:,}")
    print(f"  Tiket sesudah: {after:,}")
    print(f"  Selisih: {'+' if delta > 0 else ''}{delta:,}")
    print("=" * 50)

    if args.push:
        git_push()

    print("\n✅ Selesai. Jalankan ulang app Streamlit untuk lihat data baru.")


if __name__ == "__main__":
    main()
