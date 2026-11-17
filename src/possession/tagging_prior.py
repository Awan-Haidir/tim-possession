"""STASIUN 4c: petunjuk dari Smart Tagging (set piece = restart).

Smart Tagging otomatis, bukan kebenaran. Perlakukan sebagai bukti, bukan jawaban.
Interval adalah JENDELA beberapa detik di sekitar restart, bukan titik presisi.
Tag Team berbunyi 'Barcelona' / 'Atletic Club' / 'N/A' (N/A pada semua lemparan ke dalam).
"""


def team_code(tag, p):
    """Nilai tag Team -> kode tim (HOME/AWAY), atau NOBODY jika N/A atau kosong."""
    value = (tag or "").strip().lower()
    if not value or value == "n/a":
        return p.NOBODY
    return p.HOME if "barcelona" in value else p.AWAY


def restart_events(events, p):
    """Set piece (restart) terurut waktu: [{start, end, type, team}]."""
    found = []
    for event in events:
        if event["code"].strip().lower() != "set pieces":
            continue
        found.append({
            "start": event["start_frame"],
            "end": event["end_frame"],
            "type": event["tags"].get("Type"),
            "team": team_code(event["tags"].get("Team"), p),
        })
    return sorted(found, key=lambda e: e["start"])
