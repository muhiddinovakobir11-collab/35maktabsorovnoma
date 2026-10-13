import sqlite3
import os
import json
import datetime
import random
import string
import openpyxl

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")
SEED_EXCEL_PATH = r"C:\Users\user\Downloads\Sorovnoma_35maktab_Barchasi_20261008_055244.xlsx"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def generate_fingerprint():
    chars = string.ascii_uppercase + string.digits
    return "FP" + "".join(random.choices(chars, k=6))

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fish TEXT NOT NULL,
        sinf TEXT NOT NULL,
        sinf_group TEXT NOT NULL,
        test_type TEXT NOT NULL,
        til TEXT DEFAULT 'O''zbek',
        score REAL DEFAULT 0.0,
        level TEXT DEFAULT '',
        dominant_scales TEXT DEFAULT '',
        scale_scores TEXT DEFAULT '{}',
        fanlar TEXT DEFAULT '',
        togaraklar TEXT DEFAULT '',
        iqtidor TEXT DEFAULT '',
        kasb TEXT DEFAULT '',
        startap TEXT DEFAULT 'Yo''q',
        yangi_togaraklar TEXT DEFAULT '',
        takliflar TEXT DEFAULT '',
        answers TEXT DEFAULT '{}',
        timestamp TEXT,
        fingerprint TEXT DEFAULT ''
    )
    """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM entries")
    count = cursor.fetchone()[0]
    if count == 0 and os.path.exists(SEED_EXCEL_PATH):
        print(f"Seeding database from Excel: {SEED_EXCEL_PATH}")
        seed_from_excel(conn)
    conn.close()

def parse_sinf_group(sinf_str):
    s = (sinf_str or '').lower()
    if '5' in s or '6' in s: return '5-6'
    elif '7' in s: return '7'
    elif '8' in s: return '8'
    elif '9' in s: return '9'
    elif '10' in s or '11' in s: return '10-11'
    return 'boshqa'

def seed_from_excel(conn):
    try:
        wb = openpyxl.load_workbook(SEED_EXCEL_PATH, data_only=True)
        ws = wb.active
        cursor = conn.cursor()
        seeded_count = 0
        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row or not row[1]: continue
            fish = str(row[1]).strip()
            sinf = str(row[2] or '').strip()
            til_val = str(row[3] or 'O\'zbek').strip()
            til = 'Русский' if 'rus' in til_val.lower() else 'O\'zbek'
            fanlar = str(row[4] or '').strip()
            togaraklar = str(row[5] or '').strip()
            iqtidor = str(row[6] or '').strip()
            kasb = str(row[7] or '').strip()
            startap = str(row[8] or 'Yo\'q').strip()
            yangi_togaraklar = str(row[9] or '').strip()
            takliflar = str(row[10] or '').strip()
            ts = str(row[11] or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")).strip()
            sinf_group = parse_sinf_group(sinf)
            fp = generate_fingerprint()

            cursor.execute("""
            INSERT INTO entries (
                fish, sinf, sinf_group, test_type, til, score, level,
                dominant_scales, scale_scores, fanlar, togaraklar, iqtidor,
                kasb, startap, yangi_togaraklar, takliflar, answers, timestamp, fingerprint
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fish, sinf, sinf_group, 'umumiy', til, 0.0, '',
                iqtidor, '{}', fanlar, togaraklar, iqtidor,
                kasb, startap, yangi_togaraklar, takliflar, json.dumps({
                    'fanlar': fanlar, 'togaraklar': togaraklar, 'iqtidor': iqtidor,
                    'kasb': kasb, 'startap': startap, 'yangi_togaraklar': yangi_togaraklar,
                    'takliflar': takliflar
                }, ensure_ascii=False), ts, fp
            ))
            seeded_count += 1
        conn.commit()
        print(f"Successfully seeded {seeded_count} entries from Excel.")
    except Exception as e:
        print(f"Error seeding Excel: {e}")

def add_entry(entry_data):
    conn = get_connection()
    cursor = conn.cursor()

    ts = entry_data.get('timestamp') or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sinf = entry_data.get('sinf', '').strip()
    sinf_group = entry_data.get('sinf_group') or parse_sinf_group(sinf)

    til = entry_data.get('til', 'O\'zbek')
    if til in ['uz', 'uzbek', 'o\'zbek', 'O\'zbek']:
        til = 'O\'zbek'
    elif til in ['ru', 'rus', 'russian', 'Русский']:
        til = 'Русский'

    fp = entry_data.get('fingerprint') or generate_fingerprint()

    scale_scores = entry_data.get('scale_scores', {})
    if isinstance(scale_scores, dict):
        scale_scores_str = json.dumps(scale_scores, ensure_ascii=False)
    else:
        scale_scores_str = str(scale_scores)

    answers = entry_data.get('answers', {})
    if isinstance(answers, dict):
        answers_str = json.dumps(answers, ensure_ascii=False)
    else:
        answers_str = str(answers)

    fanlar = entry_data.get('fanlar', '')
    if isinstance(fanlar, list): fanlar = ", ".join(fanlar)

    togaraklar = entry_data.get('togaraklar', '')
    if isinstance(togaraklar, list): togaraklar = ", ".join(togaraklar)

    iqtidor = entry_data.get('iqtidor', '')
    if isinstance(iqtidor, list): iqtidor = ", ".join(iqtidor)

    yangi_togaraklar = entry_data.get('yangi_togaraklar', '')
    if isinstance(yangi_togaraklar, list): yangi_togaraklar = ", ".join(yangi_togaraklar)

    cursor.execute("""
    INSERT INTO entries (
        fish, sinf, sinf_group, test_type, til, score, level,
        dominant_scales, scale_scores, fanlar, togaraklar, iqtidor,
        kasb, startap, yangi_togaraklar, takliflar, answers, timestamp, fingerprint
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        entry_data.get('fish', '').strip(),
        sinf,
        sinf_group,
        entry_data.get('test_type', 'umumiy'),
        til,
        float(entry_data.get('score', 0.0)),
        entry_data.get('level', ''),
        entry_data.get('dominant_scales', ''),
        scale_scores_str,
        fanlar,
        togaraklar,
        iqtidor,
        entry_data.get('kasb', '').strip(),
        entry_data.get('startap', 'Yo\'q').strip(),
        yangi_togaraklar,
        entry_data.get('takliflar', '').strip(),
        answers_str,
        ts,
        fp
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id, fp

def get_entry(entry_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        d = dict(row)
        try: d['scale_scores'] = json.loads(d.get('scale_scores') or '{}')
        except: pass
        try: d['answers'] = json.loads(d.get('answers') or '{}')
        except: pass
        return d
    return None

def update_entry(entry_id, data):
    conn = get_connection()
    cursor = conn.cursor()

    fields = ['fish', 'sinf', 'sinf_group', 'test_type', 'til', 'score', 'level',
              'dominant_scales', 'fanlar', 'togaraklar', 'iqtidor', 'kasb',
              'startap', 'yangi_togaraklar', 'takliflar']

    updates = []
    values = []
    for f in fields:
        if f in data:
            val = data[f]
            if isinstance(val, list):
                val = ", ".join(val)
            updates.append(f"{f} = ?")
            values.append(val)

    if not updates:
        conn.close()
        return False

    values.append(entry_id)
    query = f"UPDATE entries SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    return True

def delete_entry(entry_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    return True

def clear_all():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM entries")
    conn.commit()
    conn.close()
    return True

def get_entries(q=None, sinf=None, sinf_group=None, test_type=None, til=None, kasb=None, limit=None, offset=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM entries WHERE 1=1"
    params = []

    if q:
        query += " AND (fish LIKE ? OR kasb LIKE ? OR sinf LIKE ? OR iqtidor LIKE ? OR fanlar LIKE ? OR togaraklar LIKE ? OR yangi_togaraklar LIKE ? OR fingerprint LIKE ?)"
        q_term = f"%{q}%"
        params.extend([q_term, q_term, q_term, q_term, q_term, q_term, q_term, q_term])

    if sinf:
        if sinf.endswith('-sinf') or sinf.endswith('-klass') or sinf.endswith('-класс'):
            grade_prefix = sinf.split('-')[0] + '-'
            query += " AND (sinf = ? OR sinf LIKE ?)"
            params.extend([sinf, f"{grade_prefix}%"])
        else:
            query += " AND sinf = ?"
            params.append(sinf)

    if sinf_group and sinf_group != 'all':
        query += " AND sinf_group = ?"
        params.append(sinf_group)

    if test_type and test_type != 'all':
        query += " AND test_type = ?"
        params.append(test_type)

    if til and til != 'all':
        if til.lower() in ['uz', 'uzbek', 'o\'zbek']:
            query += " AND (til = 'O''zbek' OR til = 'uz')"
        elif til.lower() in ['ru', 'rus', 'русский']:
            query += " AND (til = 'Русский' OR til = 'ru')"
        else:
            query += " AND til = ?"
            params.append(til)

    if kasb:
        query += " AND kasb LIKE ?"
        params.append(f"%{kasb}%")

    query += " ORDER BY id DESC"

    if limit is not None:
        query += f" LIMIT {int(limit)}"
        if offset is not None:
            query += f" OFFSET {int(offset)}"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    results = []
    for r in rows:
        d = dict(r)
        try: d['scale_scores'] = json.loads(d.get('scale_scores') or '{}')
        except: pass
        try: d['answers'] = json.loads(d.get('answers') or '{}')
        except: pass
        results.append(d)

    conn.close()
    return results

def get_class_aggregated(sinf):
    conn = get_connection()
    cursor = conn.cursor()

    if sinf.endswith('-sinf') or sinf.endswith('-klass') or sinf.endswith('-класс'):
        grade_prefix = sinf.split('-')[0] + '-'
        cursor.execute("SELECT * FROM entries WHERE sinf = ? OR sinf LIKE ? ORDER BY id DESC", (sinf, f"{grade_prefix}%"))
    else:
        cursor.execute("SELECT * FROM entries WHERE sinf = ? ORDER BY id DESC", (sinf,))

    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    total = len(rows)
    with_clubs = 0
    without_clubs = 0

    fanlar_counter = {}
    togarak_counter = {}
    iqtidor_counter = {}
    kasb_counter = {}
    yangi_togarak_counter = {}

    for r in rows:
        tog = r.get('togaraklar', '').strip()
        is_no_club = not tog or any(w in tog.lower() for w in ['bormayman', 'yoq', "yo'q", 'qatnashmayman', 'нет'])
        if is_no_club:
            without_clubs += 1
        else:
            with_clubs += 1

        for f in [x.strip() for x in r.get('fanlar', '').split(',') if x.strip()]:
            fanlar_counter[f] = fanlar_counter.get(f, 0) + 1

        for t in [x.strip() for x in tog.split(',') if x.strip() and not is_no_club]:
            togarak_counter[t] = togarak_counter.get(t, 0) + 1

        iqt = r.get('iqtidor', '') or r.get('dominant_scales', '')
        for iq in [x.strip() for x in iqt.split(',') if x.strip()]:
            iqtidor_counter[iq] = iqtidor_counter.get(iq, 0) + 1

        k = r.get('kasb', '').strip()
        if k:
            kasb_counter[k] = kasb_counter.get(k, 0) + 1

        yt = r.get('yangi_togaraklar', '').strip()
        for y in [x.strip() for x in yt.split(',') if x.strip()]:
            yangi_togarak_counter[y] = yangi_togarak_counter.get(y, 0) + 1

    club_percent = round((with_clubs / total * 100)) if total > 0 else 0

    top_fanlar = sorted(fanlar_counter.items(), key=lambda x: x[1], reverse=True)[:8]
    top_iqtidor = sorted(iqtidor_counter.items(), key=lambda x: x[1], reverse=True)[:8]
    top_kasblar = sorted(kasb_counter.items(), key=lambda x: x[1], reverse=True)[:8]
    top_yangi_togaraklar = sorted(yangi_togarak_counter.items(), key=lambda x: x[1], reverse=True)[:8]

    return {
        "status": "success",
        "sinf": sinf,
        "total": total,
        "club_percent": club_percent,
        "with_clubs": with_clubs,
        "without_clubs": without_clubs,
        "top_fanlar": top_fanlar,
        "top_iqtidor": top_iqtidor,
        "top_kasblar": top_kasblar,
        "top_yangi_togaraklar": top_yangi_togaraklar,
        "students": rows
    }

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM entries")
    total = cursor.fetchone()[0]

    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) FROM entries WHERE timestamp LIKE ?", (f"{today_str}%",))
    today = cursor.fetchone()[0]

    cursor.execute("SELECT sinf_group, COUNT(*) FROM entries GROUP BY sinf_group")
    by_grade = dict(cursor.fetchall())

    cursor.execute("SELECT kasb, COUNT(*) as c FROM entries WHERE kasb != '' GROUP BY kasb ORDER BY c DESC LIMIT 5")
    top_careers = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM entries WHERE togaraklar != '' AND togaraklar NOT LIKE '%yoq%' AND togaraklar NOT LIKE '%qatnashmayman%'")
    with_clubs = cursor.fetchone()[0]
    club_percent = round((with_clubs / total * 100)) if total > 0 else 0

    conn.close()
    return {
        "total": total,
        "today": today,
        "by_grade": by_grade,
        "top_careers": top_careers,
        "club_percent": club_percent
    }

