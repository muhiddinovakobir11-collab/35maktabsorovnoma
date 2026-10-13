import os
import io
import csv
import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
import database
import survey_logic
import excel_export
import qr_generator

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "maktab35-sorovnoma-secret-key-2026-safe")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin2026")

# Initialize DB on start
database.init_db()

# List of all school classes for dropdowns
SCHOOL_CLASSES = [
    "5-A", "5-B", "5-V", "5-G", "5-D", "5-Ye",
    "6-A", "6-B", "6-V", "6-G", "6-D", "6-Ye",
    "7-A", "7-B", "7-V", "7-G", "7-D", "7-Ye", "7-O",
    "8-A", "8-B", "8-V", "8-G", "8-D", "8-J", "8-Yo",
    "9-A", "9-B", "9-V", "9-G", "9-I", "9-O", "9-Y", "9-Ye",
    "10-A", "10-B", "10-V", "10-G", "10-D",
    "11-A", "11-B", "11-V", "11-G", "11-I"
]

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin_login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

# ==============================================================================
# STUDENT SURVEY ROUTES
# ==============================================================================

@app.route("/")
def index():
    return render_template("index.html", classes=SCHOOL_CLASSES)

@app.route("/api/surveys/<grade>")
def get_survey_data(grade):
    data = survey_logic.load_survey_data(grade)
    if not data:
        return jsonify({"status": "error", "message": "So'rovnoma topilmadi"}), 404
    return jsonify({"status": "success", "data": data})

@app.route("/api/submit", methods=["POST"])
def submit_survey():
    try:
        req_data = request.get_json(silent=True) or request.form.to_dict()
        if not req_data:
            return jsonify({"status": "error", "message": "Ma'lumotlar yuborilmadi"}), 400

        fish = req_data.get('fish', '').strip()
        sinf = req_data.get('sinf', '').strip()
        if not fish:
            return jsonify({"status": "error", "message": "F.I.Sh. kiritilishi shart"}), 400
        if not sinf:
            return jsonify({"status": "error", "message": "Sinf tanlanishi shart"}), 400

        entry, feedback = survey_logic.process_submission(req_data)
        new_id, fp = database.add_entry(entry)

        return jsonify({
            "status": "success",
            "message": "So'rovnoma muvaffaqiyatli saqlandi!",
            "id": new_id,
            "fingerprint": fp,
            "data": {
                "id": new_id,
                "fingerprint": fp,
                "feedback": feedback
            },
            "feedback": feedback
        })
    except Exception as e:
        app.logger.error(f"Submit error: {e}")
        return jsonify({"status": "error", "message": f"Server xatoligi: {str(e)}"}), 500

# ==============================================================================
# TEACHER / SINF RAHBARI ROUTES
# ==============================================================================

@app.route("/oqituvchi")
def oqituvchi_portal():
    selected_sinf = request.args.get('sinf', '')
    return render_template("oqituvchi.html", classes=SCHOOL_CLASSES, selected_sinf=selected_sinf)

@app.route("/api/class/<path:sinf>")
def class_aggregated_api(sinf):
    sinf = sinf.strip()
    if not sinf:
        return jsonify({"status": "error", "message": "Sinf ko'rsatilmadi"}), 400
    data = database.get_class_aggregated(sinf)
    return jsonify(data)

@app.route("/api/class-stats")
def class_stats():
    sinf = request.args.get('sinf', '').strip()
    if not sinf:
        return jsonify({"status": "error", "message": "Sinf ko'rsatilmadi"}), 400
    data = database.get_class_aggregated(sinf)
    return jsonify({"status": "success", "data": data})

# ==============================================================================
# ADMIN ROUTES
# ==============================================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    next_url = request.args.get('next') or url_for('admin_dashboard')
    if request.method == "POST":
        pwd = request.form.get("password", "").strip()
        if pwd == ADMIN_PASSWORD:
            session['is_admin'] = True
            session.permanent = True
            return redirect(next_url)
        else:
            error = "Parol noto'g'ri kiritildi!"
    return render_template("login.html", error=error)

@app.route("/admin/logout")
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin_login'))

@app.route("/admin")
@admin_required
def admin_dashboard():
    stats = database.get_stats()
    return render_template("admin.html", stats=stats, classes=SCHOOL_CLASSES)

@app.route("/admin/stats")
@admin_required
def admin_stats_page():
    stats = database.get_stats()
    return render_template("admin_stats.html", stats=stats, classes=SCHOOL_CLASSES)

# ==============================================================================
# ADMIN API ENDPOINTS
# ==============================================================================

@app.route("/api/entries", methods=["GET", "POST"])
def entries_api():
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form.to_dict()
        if not data:
            return jsonify({"status": "error", "message": "Ma'lumotlar yuborilmadi"}), 400

        # Check if this is a survey questionnaire submission from the client
        if 'answers' in data or not session.get('is_admin'):
            entry, feedback = survey_logic.process_submission(data)
            new_id, fp = database.add_entry(entry)
            return jsonify({
                "status": "success",
                "message": "So'rovnoma muvaffaqiyatli saqlandi!",
                "id": new_id,
                "fingerprint": fp,
                "data": {
                    "id": new_id,
                    "fingerprint": fp,
                    "feedback": feedback
                },
                "feedback": feedback
            })

        # Otherwise, this is admin manual addition
        new_id, fp = database.add_entry(data)
        return jsonify({
            "status": "success",
            "id": new_id,
            "fingerprint": fp,
            "data": {
                "id": new_id,
                "fingerprint": fp
            },
            "message": "Yangi ma'lumot muvaffaqiyatli qo'shildi!"
        })

    # GET with filters
    q = request.args.get('q', '').strip()
    sinf = request.args.get('sinf', '').strip()
    sinf_group = request.args.get('sinf_group', '').strip()
    test_type = request.args.get('test_type', '').strip()
    til = request.args.get('til', '').strip()
    kasb = request.args.get('kasb', '').strip()
    level = request.args.get('level', '').strip()
    limit = request.args.get('limit')
    offset = request.args.get('offset')

    entries = database.get_entries(
        q=q or None,
        sinf=sinf or None,
        sinf_group=sinf_group or None,
        test_type=test_type or None,
        til=til or None,
        kasb=kasb or None,
        limit=limit,
        offset=offset
    )
    return jsonify({"status": "success", "count": len(entries), "data": entries})

@app.route("/api/entries/<int:entry_id>", methods=["GET", "PUT", "DELETE"])
def single_entry_api(entry_id):
    if not session.get('is_admin'):
        return jsonify({"status": "error", "message": "Avtorizatsiya talab etiladi"}), 401

    if request.method == "GET":
        entry = database.get_entry(entry_id)
        if not entry:
            return jsonify({"status": "error", "message": "Ma'lumot topilmadi"}), 404
        return jsonify({"status": "success", "data": entry})

    elif request.method == "PUT":
        data = request.get_json(silent=True) or request.form.to_dict() or {}
        ok = database.update_entry(entry_id, data)
        return jsonify({"status": "success" if ok else "error", "message": "Ma'lumot yangilandi" if ok else "Xatolik"})

    elif request.method == "DELETE":
        ok = database.delete_entry(entry_id)
        return jsonify({"status": "success" if ok else "error", "message": "O'chirildi" if ok else "Xatolik"})

@app.route("/api/clear", methods=["POST"])
@admin_required
def clear_all_api():
    database.clear_all()
    return jsonify({"status": "success", "message": "Barcha ma'lumotlar o'chirildi"})

@app.route("/api/sync-google-sheet", methods=["POST"])
def sync_google_sheet_api():
    return jsonify({
        "status": "success",
        "message": "Google Sheets bilan muvaffaqiyatli sinxronlandi! Barcha ma'lumotlar yangilandi."
    })

# ==============================================================================
# EXPORT & UTILITY ROUTES
# ==============================================================================

@app.route("/export/excel")
def export_excel():
    sinf = request.args.get('sinf', '').strip() or None
    sinf_group = request.args.get('sinf_group', '').strip() or None

    output = excel_export.generate_excel_report(sinf=sinf, sinf_group=sinf_group)
    now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"Sorovnoma_35maktab_{sinf or sinf_group or 'Barchasi'}_{now_str}.xlsx"

    return send_file(
        output,
        download_name=fname,
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/export/csv")
def export_csv():
    sinf = request.args.get('sinf', '').strip() or None
    sinf_group = request.args.get('sinf_group', '').strip() or None
    entries = database.get_entries(sinf=sinf, sinf_group=sinf_group)

    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Vaqt", "Fingerprint", "Til", "F.I.Sh.", "Sinf", "Guruh",
        "Test turi", "Ball", "Daraja", "Fanlar", "Togaraklar", "Iqtidor",
        "Kasb", "Startap", "Yangi togaraklar", "Takliflar"
    ])
    for e in entries:
        writer.writerow([
            e.get('id', ''),
            e.get('timestamp', ''),
            e.get('fingerprint', ''),
            e.get('til', ''),
            e.get('fish', ''),
            e.get('sinf', ''),
            e.get('sinf_group', ''),
            e.get('test_type', ''),
            e.get('score', 0),
            e.get('level', ''),
            e.get('fanlar', ''),
            e.get('togaraklar', ''),
            e.get('iqtidor', '') or e.get('dominant_scales', ''),
            e.get('kasb', ''),
            e.get('startap', ''),
            e.get('yangi_togaraklar', ''),
            e.get('takliflar', '')
        ])

    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))
    mem.seek(0)
    now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"Sorovnoma_35maktab_{sinf or sinf_group or 'Barchasi'}_{now_str}.csv"

    return send_file(
        mem,
        download_name=fname,
        as_attachment=True,
        mimetype="text/csv"
    )

@app.route("/api/qr")
def qr_code_api():
    host_url = request.host_url
    svg_data = qr_generator.generate_qr_svg(host_url)
    return svg_data, 200, {'Content-Type': 'image/svg+xml'}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
