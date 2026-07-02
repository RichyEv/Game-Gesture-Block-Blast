import cv2
import mediapipe as mp
import random
import math
import pygame
import numpy as np
import sys
import os
import requests
import threading


# ─────────────────────────────────────────────
#   Performance Boost
# ─────────────────────────────────────────────

try:
    cv2.setUseOptimized(True)
    cv2.setNumThreads(4)
except Exception:
    pass


# ─────────────────────────────────────────────
#   UTILITY
# ─────────────────────────────────────────────

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ─────────────────────────────────────────────
#   TELEGRAM BOT
# ─────────────────────────────────────────────

TELE_TOKEN       = "Masukkan Token BOT Telegram Anda"
ACTIVATION_TOKEN = str(random.randint(1000, 9999))
LAST_UPDATE_ID   = 0
CURRENT_PLAYER   = {"id": None, "name": "Guest"}


def cek_pairing_telegram():
    global ACTIVATION_TOKEN, LAST_UPDATE_ID
    if CURRENT_PLAYER["id"] is not None:
        return
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/getUpdates"
    try:
        params = {"offset": LAST_UPDATE_ID + 1, "timeout": 1}
        res    = requests.get(url, params=params).json()
        if res["ok"] and res["result"]:
            for update in res["result"]:
                LAST_UPDATE_ID = update["update_id"]
                if "message" in update and "text" in update["message"]:
                    parts = update["message"]["text"].strip().split()
                    if len(parts) >= 2 and parts[-1] == ACTIVATION_TOKEN:
                        nickname               = " ".join(parts[:-1])
                        CURRENT_PLAYER["id"]   = update["message"]["chat"]["id"]
                        CURRENT_PLAYER["name"] = nickname
                        print(f"[Pairing Sukses] {CURRENT_PLAYER['name']} (ID: {CURRENT_PLAYER['id']})")
                        msg = (
                            f"✅ Game Berhasil Diaktifkan!\n"
                            f"Nickname: {CURRENT_PLAYER['name']}\n"
                            f"Selamat bermain! Laporan rekor dikirim ke Telegram setelah game over."
                        )
                        threading.Thread(
                            target=kirim_pesan_tele_langsung,
                            args=(CURRENT_PLAYER["id"], msg)
                        ).start()
    except Exception:
        pass


def kirim_pesan_tele_langsung(chat_id, pesan):
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": chat_id, "text": pesan})
    except Exception:
        pass


def kirim_pesan_tele(pesan):
    if not CURRENT_PLAYER["id"]:
        return
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    try:
        res = requests.post(url, data={"chat_id": CURRENT_PLAYER["id"], "text": pesan})
        print(f"[Bot Log] Terkirim ke {CURRENT_PLAYER['name']}! Status: {res.status_code}")
    except Exception as e:
        print(f"[Bot Error] {e}")


def kirim_foto_tele(path_foto, caption):
    if not CURRENT_PLAYER["id"]:
        return
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendPhoto"
    try:
        with open(path_foto, "rb") as foto:
            res = requests.post(
                url,
                data={"chat_id": CURRENT_PLAYER["id"], "caption": caption},
                files={"photo": foto},
            )
            print(f"[Bot Log] Foto terkirim ke {CURRENT_PLAYER['name']}! Status: {res.status_code}")
    except Exception as e:
        print(f"[Bot Error] {e}")


# ─────────────────────────────────────────────
#   LEVEL / PROGRESSION
# ─────────────────────────────────────────────

LEVEL_STAGES = [
    {"min":     0, "max":   999, "nama": "🌱 Pemula Cilik",    "warna": (180, 180, 180)},
    {"min":  1000, "max":  2999, "nama": "⭐ Bintang Muda",    "warna": (0, 200, 255)} ,
    {"min":  3000, "max":  5999, "nama": "🔥 Si Pemberani",    "warna": (0, 140, 255)} ,
    {"min":  6000, "max":  9999, "nama": "💎 Jagoan Blok",     "warna": (180, 0, 255)} ,
    {"min": 10000, "max": 14999, "nama": "🚀 Petarung Sejati", "warna": (0, 255, 180)},
    {"min": 15000, "max": 19999, "nama": "🌟 Sang Penakluk",   "warna": (255, 200, 0)},
    {"min": 20000, "max": 29999, "nama": "👑 Raja Blok",       "warna": (0, 215, 255)},
    {"min": 30000, "max": 99999, "nama": "🏆 LEGENDA ABADI",   "warna": (255, 80, 80)},
]


def get_level_info(score):
    for lvl in LEVEL_STAGES:
        if lvl["min"] <= score <= lvl["max"]:
            return lvl
    return LEVEL_STAGES[-1]


def get_level_progress(score):
    lvl = get_level_info(score)
    if lvl["max"] == 99999:
        return 1.0
    return min(1.0, (score - lvl["min"]) / (lvl["max"] - lvl["min"]))


# ─────────────────────────────────────────────
#   QUIZ BANK
# ─────────────────────────────────────────────

QUIZ_BANK = [
    {"soal": "Berapa hasil dari 8 x 6 ?", "jawaban": "48", "pilihan": ["42", "48", "54"]},
    {"soal": "Berapa 50 + 75 ?", "jawaban": "125", "pilihan": ["115", "125", "135"]},
    {"soal": "Berapa 40 dibagi 5 ?", "jawaban": "8", "pilihan": ["7", "8", "9"]},
    {"soal": "Berapa hasil dari 100 - 35 ?", "jawaban": "65", "pilihan": ["55", "65", "75"]},
    {"soal": "1 meter sama dengan berapa centimeter?", "jawaban": "100", "pilihan": ["10", "100", "1000"]},
    {"soal": "Berapa hasil dari 12 x 3 ?", "jawaban": "36", "pilihan": ["32", "36", "38"]},
    {"soal": "Setengah dari 50 adalah...", "jawaban": "25", "pilihan": ["20", "25", "30"]},

    # --- PENGETAHUAN ALAM / UMUM ---
    {"soal": "Bagian tumbuhan yang berada di dalam tanah disebut...", "jawaban": "Akar", "pilihan": ["Daun", "Batang", "Akar"]},
    {"soal": "Hewan yang hanya memakan tumbuhan disebut...", "jawaban": "Herbivora", "pilihan": ["Karnivora", "Herbivora", "Omnivora"]},
    {"soal": "Matahari terbit dari sebelah...", "jawaban": "Timur", "pilihan": ["Barat", "Timur", "Selatan"]},
    {"soal": "Indera manusia untuk mencium bau adalah...", "jawaban": "Hidung", "pilihan": ["Mata", "Telinga", "Hidung"]},
    {"soal": "Air yang dibekukan di dalam kulkas akan berubah menjadi...", "jawaban": "Es", "pilihan": ["Uap", "Es", "Embun"]},
    {"soal": "Hewan yang bernapas menggunakan insang adalah...", "jawaban": "Ikan", "pilihan": ["Ayam", "Kucing", "Ikan"]},
    {"soal": "Benda langit yang bersinar di malam hari adalah...", "jawaban": "Bulan", "pilihan": ["Matahari", "Awan", "Bulan"]},

    # --- BAHASA INGGRIS ---
    {"soal": "Bahasa Inggris dari 'Keluarga' adalah...", "jawaban": "Family", "pilihan": ["Friend", "Family", "School"]},
    {"soal": "Apa bahasa Inggris dari 'Hari Senin'?", "jawaban": "Monday", "pilihan": ["Sunday", "Monday", "Tuesday"]},
    {"soal": "Angka 15 dalam bahasa Inggris adalah...", "jawaban": "Fifteen", "pilihan": ["Fifty", "Fifteen", "Five"]},
    {"soal": "Bahasa Inggris dari 'Sepatu' adalah...", "jawaban": "Shoes", "pilihan": ["Shirt", "Shoes", "Hat"]},
    {"soal": "Lawan kata dari 'Big' (Besar) adalah...", "jawaban": "Small", "pilihan": ["Tall", "Short", "Small"]},
    {"soal": "Apa arti dari kata 'Breakfast'?", "jawaban": "Sarapan", "pilihan": ["Makan Siang", "Sarapan", "Makan Malam"]},
    {"soal": "Bahasa Inggris dari warna 'Hitam' adalah...", "jawaban": "Black", "pilihan": ["White", "Brown", "Black"]},

  {"soal":"Berapa 6 + 3 ?","jawaban":"9","pilihan":["8","9","10"]},
  {"soal":"Bahasa Inggris dari 'Sepatu' adalah...","jawaban":"Shoes","pilihan":["Shoes","Hat","Socks"]},
  {"soal":"Planet tempat kita tinggal adalah...","jawaban":"Bumi","pilihan":["Mars","Bumi","Saturnus"]},

  {"soal":"Berapa 9 - 2 ?","jawaban":"7","pilihan":["6","7","8"]},
  {"soal":"Bahasa Inggris dari 'Air' adalah...","jawaban":"Water","pilihan":["Water","Fire","Wind"]},
  {"soal":"Hewan yang dapat hidup di darat dan air adalah...","jawaban":"Katak","pilihan":["Katak","Kucing","Ayam"]},

  {"soal":"Berapa 4 + 5 ?","jawaban":"9","pilihan":["8","9","10"]},
  {"soal":"Bahasa Inggris dari 'Guru' adalah...","jawaban":"Teacher","pilihan":["Doctor","Teacher","Police"]},
  {"soal":"Jika lampu lalu lintas berwarna kuning, kita harus...","jawaban":"Bersiap berhenti","pilihan":["Jalan terus","Bersiap berhenti","Putar balik"]},

  {"soal":"Berapa 10 - 4 ?","jawaban":"6","pilihan":["5","6","7"]},
  {"soal":"Bahasa Inggris dari 'Sekolah' adalah...","jawaban":"School","pilihan":["School","House","Market"]},
  {"soal":"Siapa presiden pertama Indonesia?","jawaban":"Soekarno","pilihan":["Soekarno","Habibie","Prabowo"]},

  {"soal":"Berapa 3 + 6 ?","jawaban":"9","pilihan":["8","9","10"]},
  {"soal":"Bahasa Inggris dari 'Mata' adalah...","jawaban":"Eye","pilihan":["Eye","Ear","Nose"]},
  {"soal":"Pulau tempat Jakarta berada adalah...","jawaban":"Jawa","pilihan":["Jawa","Sumatera","Sulawesi"]},

  {"soal":"Berapa 7 - 3 ?","jawaban":"4","pilihan":["3","4","5"]},
  {"soal":"Bahasa Inggris dari 'Rumah' adalah...","jawaban":"House","pilihan":["House","School","Office"]},
  {"soal":"Nama planet yang dikenal sebagai Planet Merah adalah...","jawaban":"Mars","pilihan":["Mars","Bumi","Venus"]},
    {"soal": "Warna apel yang matang?",      "jawaban": "Merah",          "pilihan": ["Hijau", "Merah", "Biru"]},
    {"soal": "Berapa kaki kucing?",          "jawaban": "4",              "pilihan": ["2", "4", "6"]},
    {"soal": "Ibu kota Indonesia adalah?",   "jawaban": "Jakarta",        "pilihan": ["Bandung", "Jakarta", "Surabaya"]},
    {"soal": "Binatang yang bertelur?",      "jawaban": "Ayam",           "pilihan": ["Kucing", "Ayam", "Sapi"]},
    {"soal": "Matahari terbit dari arah?",   "jawaban": "Timur",          "pilihan": ["Barat", "Timur", "Utara"]},
    {"soal": "Berapa hari dalam seminggu?",  "jawaban": "7",              "pilihan": ["5", "6", "7"]},
    {"soal": "Berapa bulan dalam setahun?",  "jawaban": "12",             "pilihan": ["10", "12", "14"]},
    {"soal": "Hewan raja hutan adalah?",     "jawaban": "Singa",          "pilihan": ["Harimau", "Singa", "Gajah"]},
    {"soal": "Sayuran berwarna oranye?",     "jawaban": "Wortel",         "pilihan": ["Bayam", "Wortel", "Kol"]},
    {"soal": "Air mendidih pada suhu?",      "jawaban": "100 C",          "pilihan": ["50 C", "100 C", "200 C"]},
    {"soal": "Planet kita bernama?",         "jawaban": "Bumi",           "pilihan": ["Mars", "Bumi", "Venus"]},
    {"soal": "Berapa warna pelangi?",        "jawaban": "7",              "pilihan": ["5", "6", "7"]},
    {"soal": "Bendera Indonesia berwarna?",  "jawaban": "Merah Putih",    "pilihan": ["Merah Putih", "Merah Biru", "Putih Hijau"]},
    {"soal": "Sumpah Pemuda tiap tanggal?",  "jawaban": "28 Oktober",     "pilihan": ["17 Agustus", "28 Oktober", "1 Juni"]},
    {"soal": "Bahasa Inggris 'Kucing'?",     "jawaban": "Cat",            "pilihan": ["Dog", "Cat", "Bird"]},
    {"soal": "Bahasa Inggris 'Anjing'?",     "jawaban": "Dog",            "pilihan": ["Cat", "Dog", "Fish"]},
    {"soal": "Bahasa Inggris 'Apel'?",       "jawaban": "Apple",          "pilihan": ["Mango", "Apple", "Orange"]},
    {"soal": "Bahasa Inggris 'Buku'?",       "jawaban": "Book",           "pilihan": ["Pen", "Book", "Bag"]},
    {"soal": "Bahasa Inggris 'Merah'?",      "jawaban": "Red",            "pilihan": ["Blue", "Red", "Green"]},
    {"soal": "Bahasa Inggris 'Biru'?",       "jawaban": "Blue",           "pilihan": ["Red", "Blue", "Yellow"]},
    {"soal": "Bahasa Inggris 'Satu'?",       "jawaban": "One",            "pilihan": ["One", "Two", "Three"]},
    {"soal": "Bahasa Inggris 'Tiga'?",       "jawaban": "Three",          "pilihan": ["One", "Two", "Three"]},
    {"soal": "Bahasa Inggris 'Ibu'?",        "jawaban": "Mother",         "pilihan": ["Father", "Mother", "Sister"]},
    {"soal": "Bahasa Inggris 'Ayah'?",       "jawaban": "Father",         "pilihan": ["Father", "Mother", "Brother"]},
    {"soal": "Artinya 'Good Morning'?",      "jawaban": "Selamat Pagi",   "pilihan": ["Selamat Malam", "Selamat Pagi", "Selamat Sore"]},
    {"soal": "Artinya 'Thank You'?",         "jawaban": "Terima Kasih",   "pilihan": ["Maaf", "Terima Kasih", "Tolong"]},
    {"soal": "Artinya 'I love you'?",        "jawaban": "Aku cinta kamu", "pilihan": ["Aku benci kamu", "Aku cinta kamu", "Aku rindu kamu"]},
    {"soal": "Bahasa Inggris 'Sekolah'?",    "jawaban": "School",         "pilihan": ["Home", "School", "Garden"]},
    {"soal": "Artinya 'My name is Budi'?",   "jawaban": "Namaku Budi",    "pilihan": ["Rumahku Budi", "Namaku Budi", "Temanku Budi"]},
    {"soal": "Bahasa Inggris 'Ikan'?",       "jawaban": "Fish",           "pilihan": ["Bird", "Fish", "Frog"]},
    {"soal": "Bahasa Inggris 'Bunga'?",      "jawaban": "Flower",         "pilihan": ["Tree", "Leaf", "Flower"]},
    {"soal": "Bahasa Inggris 'Besar'?",      "jawaban": "Big",            "pilihan": ["Small", "Big", "Long"]},
    {"soal": "Artinya 'How are you?'",       "jawaban": "Apa kabar?",     "pilihan": ["Siapa kamu?", "Apa kabar?", "Di mana kamu?"]},
    {"soal": "Bahasa Inggris 'Makan'?",      "jawaban": "Eat",            "pilihan": ["Drink", "Eat", "Sleep"]},
]

quiz_state = {
    "active":             False,
    "soal":               None,
    "pilihan":            [],
    "jawaban_benar":      "",
    "block_idx":          -1,
    "wrong_timer":        0,
    "wrong_max":          45,
    "selected_choice":    -1,
    "choice_confirm_timer": 0,
    "show_result":        False,
    "result_correct":     False,
    "result_timer":       0,
    "soal_ke":            0,
    "soal_used":          [],
    "fist_choice":        -1,
    "fist_timer":         0,
    "fist_max":           15,
    "consecutive_wrongs": 0,
}

nilai_state = {"total_soal": 0, "benar": 0, "salah": 0, "riwayat": []}


def get_nilai_persen():
    if nilai_state["total_soal"] == 0:
        return 0
    return round((nilai_state["benar"] / nilai_state["total_soal"]) * 100, 1)


def get_soal_baru():
    tersisa = [i for i in range(len(QUIZ_BANK)) if i not in quiz_state["soal_used"]]
    if not tersisa:
        quiz_state["soal_used"] = []
        tersisa = list(range(len(QUIZ_BANK)))
    idx  = random.choice(tersisa)
    quiz_state["soal_used"].append(idx)
    soal           = QUIZ_BANK[idx].copy()
    soal["pilihan"] = random.sample(soal["pilihan"], len(soal["pilihan"]))
    return soal


def mulai_kuis(block_idx):
    soal = get_soal_baru()
    quiz_state.update({
        "active":          True,
        "soal":            soal["soal"],
        "pilihan":         soal["pilihan"],
        "jawaban_benar":   soal["jawaban"],
        "block_idx":       block_idx,
        "wrong_timer":     0,
        "selected_choice": -1,
        "choice_confirm_timer": 0,
        "show_result":     False,
        "result_correct":  False,
        "result_timer":    0,
        "fist_choice":     -1,
        "fist_timer":      0,
    })
    quiz_state["soal_ke"] += 1


def tutup_kuis():
    quiz_state.update({
        "active":          False,
        "wrong_timer":     0,
        "selected_choice": -1,
        "show_result":     False,
        "fist_choice":     -1,
        "fist_timer":      0,
    })


# ─────────────────────────────────────────────
#   SCREENSHOT COUNTDOWN
# ─────────────────────────────────────────────

screenshot_timer_state = {"active": False, "countdown_frames": 0, "type": None}
SCREENSHOT_DELAY_FRAMES = 300


def mulai_countdown_screenshot(tipe):
    screenshot_timer_state.update({
        "active":           True,
        "countdown_frames": SCREENSHOT_DELAY_FRAMES,
        "type":             tipe,
    })


def draw_screenshot_countdown(frame):
    if not screenshot_timer_state["active"]:
        return
    sisa_detik = math.ceil(screenshot_timer_state["countdown_frames"] / 60)
    pct        = screenshot_timer_state["countdown_frames"] / SCREENSHOT_DELAY_FRAMES
    W, H       = frame.shape[1], frame.shape[0]
    if screenshot_timer_state["type"] == "highscore":
        msg, warna = f"FOTO REKOR BARU dalam {sisa_detik} detik!", (0, 215, 255)
    else:
        msg, warna = f"FOTO NILAI SEMPURNA dalam {sisa_detik} detik!", (0, 255, 150)
    draw_fancy_text(frame, msg, W // 2, H - 60, 32, warna, is_center=True)
    bar_w = int((W - 200) * pct)
    cv2.rectangle(frame, (100, H - 30), (W - 100, H - 15), (40, 40, 40), -1)
    cv2.rectangle(frame, (100, H - 30), (100 + bar_w, H - 15), warna, -1)


# ─────────────────────────────────────────────
#   NEON FRAME (SCREENSHOT OVERLAY)
# ─────────────────────────────────────────────

def draw_neon_glow(frame, x1, y1, x2, y2, color, layers=4, base_thick=2):
    for i in range(layers, 0, -1):
        alpha     = 0.15 + (layers - i) * 0.12
        thickness = base_thick + i * 3
        pad       = i * 3
        overlay   = frame.copy()
        cv2.rectangle(overlay, (x1 - pad, y1 - pad), (x2 + pad, y2 + pad), color, thickness)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, base_thick)


def draw_neon_corner(frame, x, y, length, color, direction):
    thick  = 4
    glow_c = tuple(min(255, int(c * 1.4)) for c in color)
    for gi in range(3):
        ov = frame.copy()
        if direction == "tl":
            cv2.line(ov, (x - gi, y), (x + length, y), glow_c, thick + (3 - gi) * 2)
            cv2.line(ov, (x, y - gi), (x, y + length), glow_c, thick + (3 - gi) * 2)
        elif direction == "tr":
            cv2.line(ov, (x + gi, y), (x - length, y), glow_c, thick + (3 - gi) * 2)
            cv2.line(ov, (x, y - gi), (x, y + length), glow_c, thick + (3 - gi) * 2)
        elif direction == "bl":
            cv2.line(ov, (x - gi, y), (x + length, y), glow_c, thick + (3 - gi) * 2)
            cv2.line(ov, (x, y + gi), (x, y - length), glow_c, thick + (3 - gi) * 2)
        elif direction == "br":
            cv2.line(ov, (x + gi, y), (x - length, y), glow_c, thick + (3 - gi) * 2)
            cv2.line(ov, (x, y + gi), (x, y - length), glow_c, thick + (3 - gi) * 2)
        cv2.addWeighted(ov, 0.15 + gi * 0.1, frame, 1 - (0.15 + gi * 0.1), 0, frame)
    if direction == "tl":
        cv2.line(frame, (x, y), (x + length, y), color, thick)
        cv2.line(frame, (x, y), (x, y + length), color, thick)
    elif direction == "tr":
        cv2.line(frame, (x, y), (x - length, y), color, thick)
        cv2.line(frame, (x, y), (x, y + length), color, thick)
    elif direction == "bl":
        cv2.line(frame, (x, y), (x + length, y), color, thick)
        cv2.line(frame, (x, y), (x, y - length), color, thick)
    elif direction == "br":
        cv2.line(frame, (x, y), (x - length, y), color, thick)
        cv2.line(frame, (x, y), (x, y - length), color, thick)


def draw_scan_lines(frame, alpha=0.08):
    h, w    = frame.shape[:2]
    overlay = frame.copy()
    for y in range(0, h, 4):
        cv2.line(overlay, (0, y), (w, y), (0, 0, 0), 1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def draw_neon_divider(frame, x1, x2, y, color):
    mid = (x1 + x2) // 2
    for i in range(3, 0, -1):
        ov = frame.copy()
        cv2.line(ov, (x1, y), (x2, y), color, i * 2)
        cv2.addWeighted(ov, 0.15, frame, 0.85, 0, frame)
    cv2.line(frame, (x1, y), (x2, y), color, 1)
    cv2.fillPoly(
        frame,
        [np.array([[mid, y - 6], [mid + 6, y], [mid, y + 6], [mid - 6, y]], np.int32)],
        color,
    )


def draw_neon_frame(frame, tipe, score, nama_player, nilai_persen=None):
    h, w = frame.shape[:2]
    out  = frame.copy()

    if tipe == "highscore":
        cp, cs, ca = (0, 215, 255), (255, 140, 0), (255, 255, 255)
        bg_strip   = (0, 30, 50)
        title_text = "NEW HIGH SCORE!"
        sub_text   = f"SKOR: {score:,}"
        badge_text = "RECORD BREAKER"
        badge_c    = (0, 215, 255)
    else:
        cp, cs, ca = (0, 255, 150), (180, 0, 255), (255, 255, 100)
        bg_strip   = (0, 30, 20)
        title_text = "NILAI SEMPURNA!"
        sub_text   = f"NILAI: {nilai_persen}%"
        badge_text = "PERFECT SCORE"
        badge_c    = (0, 255, 150)

    pad  = 18
    vign = out.copy()
    for thickness, alpha in [(80, 0.35), (50, 0.25), (25, 0.15)]:
        cv2.rectangle(vign, (0, 0), (w, h), (0, 0, 0), thickness)
        cv2.addWeighted(vign, alpha, out, 1 - alpha, 0, out)

    draw_scan_lines(out, alpha=0.07)
    draw_neon_glow(out, pad, pad, w - pad, h - pad, cp, layers=5, base_thick=2)
    draw_neon_glow(out, pad + 8, pad + 8, w - pad - 8, h - pad - 8, cs, layers=2, base_thick=1)

    cl  = 55
    cp2 = pad + 2
    for x, y, d in [
        (cp2,     cp2,     "tl"),
        (w - cp2, cp2,     "tr"),
        (cp2,     h - cp2, "bl"),
        (w - cp2, h - cp2, "br"),
    ]:
        draw_neon_corner(out, x, y, cl, cp, d)

    sy1, sy2 = pad + 10, pad + 10 + 90
    hov      = out.copy()
    cv2.rectangle(hov, (pad + 10, sy1), (w - pad - 10, sy2), bg_strip, -1)
    cv2.addWeighted(hov, 0.75, out, 0.25, 0, out)
    draw_neon_divider(out, pad + 10, w - pad - 10, sy2, cp)

    font = cv2.FONT_HERSHEY_SIMPLEX
    ts, tt = 1.6, 3
    (tw, th), _ = cv2.getTextSize(title_text, font, ts, tt)
    tx, ty = (w - tw) // 2, sy1 + (90 + th) // 2 - 4
    cv2.putText(out, title_text, (tx + 3, ty + 3), font, ts, (0, 0, 0), tt + 4, cv2.LINE_AA)
    for gi in range(4, 0, -1):
        ov2 = out.copy()
        cv2.putText(ov2, title_text, (tx, ty), font, ts, cp, tt + gi * 2, cv2.LINE_AA)
        cv2.addWeighted(ov2, 0.12, out, 0.88, 0, out)
    cv2.putText(out, title_text, (tx, ty), font, ts, ca, tt, cv2.LINE_AA)

    fy1, fy2 = h - pad - 10 - 85, h - pad - 10
    fov      = out.copy()
    cv2.rectangle(fov, (pad + 10, fy1), (w - pad - 10, fy2), bg_strip, -1)
    cv2.addWeighted(fov, 0.75, out, 0.25, 0, out)
    draw_neon_divider(out, pad + 10, w - pad - 10, fy1, cp)

    pl = f"PLAYER: {nama_player.upper()}"
    cv2.putText(out, pl, (pad + 22, fy1 + 30), font, 0.65, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(out, pl, (pad + 22, fy1 + 30), font, 0.65, cp,        2, cv2.LINE_AA)

    cv2.putText(out, sub_text, (pad + 22, fy1 + 62), font, 0.85, (0, 0, 0), 5, cv2.LINE_AA)
    for gi in range(3, 0, -1):
        ov3 = out.copy()
        cv2.putText(ov3, sub_text, (pad + 22, fy1 + 62), font, 0.85, cs, 2 + gi, cv2.LINE_AA)
        cv2.addWeighted(ov3, 0.18, out, 0.82, 0, out)
    cv2.putText(out, sub_text, (pad + 22, fy1 + 62), font, 0.85, ca, 2, cv2.LINE_AA)

    gt = "GESTURE BLOCK BLAST"
    (gw, _), _ = cv2.getTextSize(gt, font, 0.58, 2)
    gx = w - pad - 20 - gw
    cv2.putText(out, gt, (gx, fy1 + 30), font, 0.58, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(out, gt, (gx, fy1 + 30), font, 0.58, cp,        1, cv2.LINE_AA)

    lvl      = get_level_info(score)
    lvl_text = (
        lvl["nama"]
        .replace("🌱", "").replace("⭐", "").replace("🔥", "").replace("💎", "")
        .replace("🚀", "").replace("🌟", "").replace("👑", "").replace("🏆", "")
        .strip()
    )
    (lw, _), _ = cv2.getTextSize(lvl_text, font, 0.55, 2)
    lx = w - pad - 20 - lw
    cv2.putText(out, lvl_text, (lx, fy1 + 62), font, 0.55, (0, 0, 0),    4, cv2.LINE_AA)
    cv2.putText(out, lvl_text, (lx, fy1 + 62), font, 0.55, lvl["warna"], 1, cv2.LINE_AA)

    bx1, by1, bx2, by2 = w - pad - 170, pad + 10, w - pad - 10, pad + 46
    bov = out.copy()
    cv2.rectangle(bov, (bx1, by1), (bx2, by2), badge_c, -1)
    cv2.addWeighted(bov, 0.25, out, 0.75, 0, out)
    cv2.rectangle(out, (bx1, by1), (bx2, by2), badge_c, 1)
    (bw2, bh2), _ = cv2.getTextSize(badge_text, font, 0.5, 2)
    cv2.putText(out, badge_text, (bx1 + (160 - bw2) // 2, by1 + (36 + bh2) // 2), font, 0.5, (0, 0, 0),       3, cv2.LINE_AA)
    cv2.putText(out, badge_text, (bx1 + (160 - bw2) // 2, by1 + (36 + bh2) // 2), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    for dx in [pad + 22, pad + 34, pad + 46]:
        cv2.circle(out, (dx, sy1 + 45), 4, cs, -1)
        cv2.circle(out, (dx, sy1 + 45), 6, cs,  1)

    return out


# ─────────────────────────────────────────────
#   HIGH SCORE FILE
# ─────────────────────────────────────────────

HS_FILE = os.path.join(os.path.expanduser("~"), "BlockBlastHighScore.txt")


def load_highscore():
    try:
        if os.path.exists(HS_FILE):
            with open(HS_FILE, "r") as f:
                return int(f.read())
    except Exception:
        pass
    return 0


def save_highscore(score):
    try:
        with open(HS_FILE, "w") as f:
            f.write(str(score))
    except Exception:
        pass


# ─────────────────────────────────────────────
#   DRAW HELPERS
# ─────────────────────────────────────────────

def draw_crown_logo(frame, x, y, size, color=(0, 215, 255)):
    w2  = int(size * 1.3)
    pts = np.array([
        [x,               y],
        [x + w2,          y],
        [x + w2,          y - int(size * 0.6)],
        [x + int(w2*0.8), y - size],
        [x + int(w2*0.5), y - int(size * 0.6)],
        [x + int(w2*0.2), y - size],
        [x,               y - int(size * 0.6)],
    ], np.int32)
    cv2.fillPoly(frame, [pts], color)
    cv2.polylines(frame, [pts], True, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.circle(frame, (x + int(w2 * 0.5), y - size + int(size * 0.1)), int(size * 0.1), (255, 0, 0), -1)


def draw_crystal_block(frame, x, y, size, color):
    cv2.rectangle(frame, (x, y), (x + size, y + size), color, -1)
    lw    = max(1, size // 15)
    light = (min(255, color[0] + 90), min(255, color[1] + 90), min(255, color[2] + 90))
    dark  = (max(0,   color[0] - 90), max(0,   color[1] - 90), max(0,   color[2] - 90))
    cv2.line(frame, (x + 1, y + 2),        (x + size - 1, y + 2),        light, lw)
    cv2.line(frame, (x + 2, y + 1),        (x + 2, y + size - 1),        light, lw)
    cv2.line(frame, (x + 1, y + size - 2), (x + size - 1, y + size - 2), dark,  lw)
    cv2.line(frame, (x + size - 2, y + 1), (x + size - 2, y + size - 1), dark,  lw)
    cv2.rectangle(frame, (x + 4, y + 4), (x + size - 4, y + size - 4), (255, 255, 255), 1)


def draw_lock_icon(frame, cx, cy, size, color=(255, 200, 0)):
    bw, bh = int(size * 0.7), int(size * 0.55)
    bx, by = cx - bw // 2, cy
    cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), color, -1)
    cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), (0, 0, 0), 2)
    cv2.circle(frame, (cx, by + bh // 2), int(bw * 0.18), (0, 0, 0), -1)
    arc_r = int(bw * 0.4)
    cv2.ellipse(frame, (cx, by - arc_r), (arc_r, arc_r), 0, 200, 340, color, int(size * 0.15))


def draw_rounded_rect(frame, x1, y1, x2, y2, color, radius=20, thickness=-1):
    cv2.rectangle(frame, (x1 + radius, y1), (x2 - radius, y2), color, thickness)
    cv2.rectangle(frame, (x1, y1 + radius), (x2, y2 - radius), color, thickness)
    for cx, cy in [
        (x1 + radius, y1 + radius),
        (x2 - radius, y1 + radius),
        (x1 + radius, y2 - radius),
        (x2 - radius, y2 - radius),
    ]:
        cv2.circle(frame, (cx, cy), radius, color, thickness)


def draw_fancy_text(frame, text, x, y, size, color=(255, 255, 255), is_center=False, pulsing=1.0):
    scale     = (size / 35.0) * pulsing
    thickness = max(2, int(scale * 3))
    font      = cv2.FONT_HERSHEY_SIMPLEX
    (w2, h2), _ = cv2.getTextSize(text, font, scale, thickness)
    tx = int(x - w2 / 2) if is_center else int(x)
    ty = int(y + h2 / 2) if is_center else int(y)
    cv2.putText(frame, text, (tx + 3, ty + 3), font, scale, (0, 0, 0), thickness + 3, cv2.LINE_AA)
    cv2.putText(frame, text, (tx, ty),          font, scale, color,     thickness,     cv2.LINE_AA)


def draw_quiz_popup(frame, smooth_x, is_fist_current):
    if not quiz_state["active"]:
        return
    W, H = frame.shape[1], frame.shape[0]

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (W, H), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

    pw, ph = 820, 430
    px, py = (W - pw) // 2, (H - ph) // 2 - 20
    draw_rounded_rect(frame, px + 6, py + 6, px + pw + 6, py + ph + 6, (10, 10, 10), radius=22)
    draw_rounded_rect(frame, px,     py,     px + pw,     py + ph,     (20, 25, 50), radius=22)
    draw_rounded_rect(frame, px,     py,     px + pw,     py + ph,     (0, 200, 255), radius=22, thickness=3)

    draw_fancy_text(frame, "  BLOCK TERKUNCI! Jawab Dulu:", W // 2, py + 45, 32, (0, 220, 255), is_center=True)
    cv2.line(frame, (px + 20, py + 62), (px + pw - 20, py + 62), (0, 100, 150), 2)

    for li, line in enumerate(quiz_state["soal"].split("\n")):
        draw_fancy_text(frame, line, W // 2, py + 95 + li * 40, 31, (255, 255, 220), is_center=True)

    cw, ch, gap = 220, 65, 30
    total_w     = 3 * cw + 2 * gap
    start_x     = W // 2 - total_w // 2
    base_y      = py + ph - 120

    hovered = -1
    for i in range(3):
        if start_x + i * (cw + gap) <= smooth_x <= start_x + i * (cw + gap) + cw:
            hovered = i
    quiz_state["selected_choice"] = hovered

    if is_fist_current and hovered >= 0:
        if quiz_state["fist_choice"] == hovered:
            quiz_state["fist_timer"] = min(
                quiz_state["fist_timer"] + 1,
                quiz_state["fist_max"] + 10,
            )
        else:
            quiz_state["fist_choice"] = hovered
            quiz_state["fist_timer"]  = 1
    else:
        quiz_state["fist_timer"] = max(0, quiz_state["fist_timer"] - 2)
        if quiz_state["fist_timer"] == 0:
            quiz_state["fist_choice"] = -1

    fist_confirmed = quiz_state["fist_timer"] >= quiz_state["fist_max"]

    for i, pilihan in enumerate(quiz_state["pilihan"]):
        cx1, cy1      = start_x + i * (cw + gap), base_y
        cx2, cy2      = cx1 + cw, cy1 + ch
        is_fist_here  = (i == quiz_state["fist_choice"] and quiz_state["fist_timer"] > 0)
        is_submitting = is_fist_here and fist_confirmed

        if is_submitting:
            box_c, txt_c, brd_c = (0, 255, 100), (0, 0, 0), (0, 255, 100)
        elif is_fist_here:
            pct   = quiz_state["fist_timer"] / quiz_state["fist_max"]
            box_c = (0, int(40 + 200 * pct), 150)
            txt_c, brd_c = (255, 255, 100), (0, 255, 150)
        elif i == hovered:
            box_c, txt_c, brd_c = (40, 80, 180), (255, 255, 100), (0, 200, 255)
        else:
            box_c, txt_c, brd_c = (30, 40, 70), (200, 200, 200), (80, 80, 120)

        draw_rounded_rect(frame, cx1, cy1, cx2, cy2, box_c, radius=14)
        draw_rounded_rect(frame, cx1, cy1, cx2, cy2, brd_c, radius=14, thickness=2)
        txt = pilihan if len(pilihan) <= 20 else pilihan[:18] + ".."
        draw_fancy_text(frame, txt, (cx1 + cx2) // 2, (cy1 + cy2) // 2, 24, txt_c, is_center=True)
        draw_fancy_text(frame, ["A", "B", "C"][i], cx1 + 15, cy1 + 20, 18, (150, 150, 200))

        if is_fist_here and not fist_confirmed:
            pct      = quiz_state["fist_timer"] / quiz_state["fist_max"]
            bar_fill = int(cw * pct)
            cv2.rectangle(frame, (cx1, cy2 + 5), (cx2, cy2 + 12), (30, 30, 30),   -1)
            cv2.rectangle(frame, (cx1, cy2 + 5), (cx1 + bar_fill, cy2 + 12), (0, 255, 150), -1)

    pulse = 1.0 + math.sin(pygame.time.get_ticks() / 300.0) * 0.08
    draw_fancy_text(
        frame,
        "Arahkan jari ke jawaban  |  Kepal tangan untuk pilih!",
        W // 2, py + ph + 32, 23, (100, 200, 255), is_center=True, pulsing=pulse,
    )

    if quiz_state["wrong_timer"] > 0:
        sisa  = math.ceil(quiz_state["wrong_timer"] / 60)
        bar_w = int(pw * (quiz_state["wrong_timer"] / quiz_state["wrong_max"]))
        cv2.rectangle(frame, (px, py + ph - 6), (px + pw, py + ph), (50, 0, 0), -1)
        cv2.rectangle(frame, (px, py + ph - 6), (px + bar_w, py + ph), (0, 100, 255), -1)
        draw_fancy_text(
            frame,
            f"Yah, salah! Coba lagi dalam {sisa} detik...",
            W // 2, py - 35, 28, (0, 80, 255), is_center=True,
        )

    if quiz_state["show_result"]:
        if quiz_state["result_correct"]:
            draw_fancy_text(frame, "BENAR! Block terbuka! +200 poin!", W // 2, py - 35, 36, (0, 255, 120), is_center=True)
        else:
            draw_fancy_text(frame, "Ups, Salah!", W // 2, py - 35, 36, (0, 60, 255), is_center=True)

    return fist_confirmed and hovered >= 0


# ─────────────────────────────────────────────
#   GAME SETUP
# ─────────────────────────────────────────────

BLOCK_COLORS = [
    (255, 140, 0),
    (0, 180, 255),
    (255, 0, 180),
    (0, 255, 0),
    (200, 200, 50),
    (255, 50, 50),
]

SHAPES = [
    [[1]],
    [[1, 1]],
    [[1], [1]],
    [[1, 1, 1]],
    [[1], [1], [1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [1, 1, 1]],
    [[1, 0], [1, 1]],
    [[0, 1], [1, 1]],
    [[1, 1], [1, 0]],
    [[1, 1], [0, 1]],
    [[1, 1, 1], [1, 0, 0]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 1, 1, 1]],
    [[1], [1], [1], [1]],
    [[1, 0, 0], [1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [0, 0, 1], [1, 1, 1]],
]

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()


def load_sound(file):
    try:
        return pygame.mixer.Sound(file)
    except Exception:
        return None


clear_sound    = load_sound(resource_path("sheeshh.wav"))
drop_sound     = load_sound(resource_path("drop.wav"))
gameover_sound = load_sound(resource_path("9-game-over-jingle.wav"))

if clear_sound:    clear_sound.set_volume(1.0)
if drop_sound:     drop_sound.set_volume(1.0)
if gameover_sound: gameover_sound.set_volume(1.0)

try:
    pygame.mixer.music.load(resource_path("xtremefreddy-game-music-loop-7-145285.mp3"))
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)
except Exception:
    pass

mp_hands = mp.solutions.hands
hands    = mp_hands.Hands(
    max_num_hands=2,
    model_complexity=0,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6,
)

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
try:
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
except Exception:
    pass

DISP_W        = 1280
DISP_H        = 720
GAME_W        = 960
X_OFFSET      = (DISP_W - GAME_W) // 2
GRID          = 8
CELL          = 60
BOARD_X       = X_OFFSET + 240
BOARD_Y       = 60
SMOOTH_FACTOR = 0.75
MAX_PARTICLES = 180

# ─── PERF: pre-allocated buffers ───
DIM_FACTOR    = np.array([0.55, 0.55, 0.55], dtype=np.float32)
DISPLAY_BUF   = np.zeros((DISP_H, DISP_W, 3), dtype=np.uint8)
GAME_AREA_BUF = np.empty((DISP_H, GAME_W, 3), dtype=np.uint8)


def generate_blocks():
    locked_idx = random.randint(0, 2)
    return [
        {
            "shape":    random.choice(SHAPES),
            "x":        X_OFFSET + 150 + i * 230,
            "y":        575,
            "used":     False,
            "color":    random.choice(BLOCK_COLORS),
            "locked":   (i == locked_idx),
            "unlocked": False,
        }
        for i in range(3)
    ]


state = {
    "score":      0,
    "highscore":  load_highscore(),
    "combo":      0,
    "game_state": "menu",
    "game_over":  False,
    "dragging":   False,
    "drag_id":    None,
    "smooth_x":   640,
    "smooth_y":   360,
    "shake_timer":  0,
    "flash_alpha":  0,
    "score_scale":  1.0,
    "board":        [[0] * GRID for _ in range(GRID)],
    "blocks":       [],
    "next_blocks":  [],
    "pinch_grace":  0,
    "tele_sent":    False,
    "congrats_timer": 0,
    "screenshot_hs_pending":    False,
    "screenshot_nilai_pending": False,
    "last_level":   None,
    "paused":       False,
    "pause_debounce": 0,
    "go_lock_timer":  0,
}


def reset_game():
    if state["score"] > state["highscore"]:
        save_highscore(state["score"])
        state["highscore"] = state["score"]
    state.update({
        "board":                    [[0] * GRID for _ in range(GRID)],
        "score":                    0,
        "combo":                    0,
        "game_over":                False,
        "flash_alpha":              0,
        "blocks":                   generate_blocks(),
        "next_blocks":              generate_blocks(),
        "pinch_grace":              0,
        "tele_sent":                False,
        "congrats_timer":           0,
        "screenshot_hs_pending":    False,
        "screenshot_nilai_pending": False,
        "last_level":               None,
        "paused":                   False,
        "pause_debounce":           0,
        "go_lock_timer":            0,
        "dragging":                 False,
        "drag_id":                  None,
    })
    nilai_state.update({"total_soal": 0, "benar": 0, "salah": 0, "riwayat": []})
    quiz_state["soal_ke"]            = 0
    quiz_state["soal_used"]          = []
    quiz_state["consecutive_wrongs"] = 0
    screenshot_timer_state["active"] = False
    tutup_kuis()


def can_place_block(shape, board):
    sh, sw = len(shape), len(shape[0])
    for gy in range(GRID - sh + 1):
        for gx in range(GRID - sw + 1):
            if all(
                not shape[y][x] or board[gy + y][gx + x] == 0
                for y in range(sh) for x in range(sw)
            ):
                return True
    return False


def kirim_laporan_nilai():
    if not CURRENT_PLAYER["id"] or nilai_state["total_soal"] == 0:
        return
    nilai       = get_nilai_persen()
    benar, total = nilai_state["benar"], nilai_state["total_soal"]
    grade = (
        "SEMPURNA!" if nilai >= 90 else
        "BAGUS!"    if nilai >= 75 else
        "CUKUP"     if nilai >= 60 else
        "Perlu Belajar Lagi"
    )
    lines = [
        "─" * 30,
        "LAPORAN NILAI QUIZ🧾",
        f"👤Player: {CURRENT_PLAYER['name']}",
        "─" * 30,
        f"✅Benar : {benar}/{total}",
        f"❌Salah : {total - benar}/{total}",
        f"📝Nilai : {nilai}%  {grade}",
        "─" * 30,
    ]
    if nilai_state["riwayat"]:
        lines.append("Detail Jawaban:")
        for idx, r in enumerate(nilai_state["riwayat"]):
            ikon = "✅" if r["benar"] else "❌"
            s    = r["soal"][:35] + ("..." if len(r["soal"]) > 35 else "")
            lines.append(f"{ikon} [{idx + 1}] {s}")
            if not r["benar"]:
                lines.append(f"   → Kamu: {r['jawaban_player']} | Benar: {r['jawaban_benar']}")
    threading.Thread(target=kirim_pesan_tele, args=("\n".join(lines),)).start()


def trigger_game_over(reason_text=None):
    """mengakhiri permainan secara bersih dan langsung menghentikan jalannya permainan."""
    state["game_over"]      = True
    state["dragging"]       = False
    state["drag_id"]        = None
    state["paused"]         = False
    state["tele_sent"]      = False
    state["go_lock_timer"]  = 25  # block input ~0.4s biar gak langsung re-trigger
    tutup_kuis()
    quiz_state["consecutive_wrongs"] = 0

    # cek highscore dulu, sama seperti jalur "papan penuh".
    # Kalau ini dihilangkan, animasi "NEW HIGHSCORE!!!" dan screenshot
    # rekor baru gak akan pernah muncul waktu kalah lewat salah kuis 2x.
    if state["score"] > state["highscore"]:
        state["congrats_timer"] = 90
    else:
        state["congrats_timer"] = 0

    if reason_text:
        TEXT_EFFECTS.append({
            "x":    DISP_W // 2,
            "y":    DISP_H // 2 - 40,
            "text": reason_text,
            "life": 60,
            "color": (0, 80, 255),
        })
    for _ in range(40):
        if len(PARTICLES) >= MAX_PARTICLES:
            break
        PARTICLES.append({
            "x":     DISP_W // 2,
            "y":     DISP_H // 2,
            "vx":    random.uniform(-10, 10),
            "vy":    random.uniform(-12, -2),
            "color": (0, 60, 255),
            "life":  random.randint(25, 55),
            "size":  random.randint(4, 9),
        })
    if gameover_sound:
        try:
            gameover_sound.play()
        except Exception:
            pass


# ─────────────────────────────────────────────
#   MAIN LOOP
# ─────────────────────────────────────────────

reset_game()
PARTICLES     = []
TEXT_EFFECTS  = []
FRAME_COUNTER    = 0
LAST_HAND_RESULT = None

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)

    FRAME_COUNTER += 1
    if FRAME_COUNTER % 2 == 0 or LAST_HAND_RESULT is None:
        small     = cv2.resize(frame, (320, 240))
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        rgb_small.flags.writeable = False
        result           = hands.process(rgb_small)
        LAST_HAND_RESULT = result
    else:
        result = LAST_HAND_RESULT

    # ─── PERF: reuse pre-allocated buffers ───
    display_frame = DISPLAY_BUF
    display_frame[:] = 0
    cv2.resize(frame, (GAME_W, DISP_H), dst=GAME_AREA_BUF)
    cv2.multiply(GAME_AREA_BUF, DIM_FACTOR, dst=GAME_AREA_BUF, dtype=cv2.CV_8U)
    display_frame[:, X_OFFSET: X_OFFSET + GAME_W] = GAME_AREA_BUF

    current_pinch = False
    is_fist       = False
    is_thumbs_up  = False
    is_pinky_up   = False

    if state["pause_debounce"] > 0:
        state["pause_debounce"] -= 1
    if state["go_lock_timer"] > 0:
        state["go_lock_timer"] -= 1

    if result.multi_hand_landmarks:
        #Deteksi Pause "T"
        if len(result.multi_hand_landmarks) == 2:
            h1, h2 = result.multi_hand_landmarks[0], result.multi_hand_landmarks[1]

            def get_orient(h):
                dx = abs(h.landmark[9].x - h.landmark[0].x)
                dy = abs(h.landmark[9].y - h.landmark[0].y)
                # Syarat lurus diperketat dari 1.4 jadi 2.0 biar ga gampang bocor
                return "H" if dx > dy * 2.0 else "V" if dy > dx * 2.0 else "N"

            o1, o2 = get_orient(h1), get_orient(h2)

            # Jarak kedua tangan harus bener-bener deket buat ngebentuk huruf "T"
            dist_hands = math.hypot(h1.landmark[9].x - h2.landmark[9].x, h1.landmark[9].y - h2.landmark[9].y)

            if {o1, o2} == {"H", "V"} and dist_hands < 0.25 and state["pause_debounce"] == 0 and not state["game_over"]:
                state["paused"]         = not state["paused"]
                state["pause_debounce"] = 30

        hand = result.multi_hand_landmarks[0]
        idx  = hand.landmark[8]
        thm  = hand.landmark[4]
        tx   = int(((idx.x + thm.x) / 2) * GAME_W) + X_OFFSET
        ty   = int(((idx.y + thm.y) / 2) * DISP_H)
        state["smooth_x"] += (tx - state["smooth_x"]) * SMOOTH_FACTOR
        state["smooth_y"] += (ty - state["smooth_y"]) * SMOOTH_FACTOR

        dist = math.hypot(idx.x - thm.x, idx.y - thm.y)
        if dist < (0.05 if state["dragging"] else 0.04):
            current_pinch = True

        # --- Gunakan Jarak ke Pergelangan Tangan (Wrist) ---
        wx, wy = hand.landmark[0].x, hand.landmark[0].y

        # Jari terlipat JIKA jarak ujung jari ke pergelangan LEBIH DEKAT dibanding ruas tengahnya
        idx_folded   = math.hypot(hand.landmark[8].x - wx, hand.landmark[8].y - wy) < math.hypot(hand.landmark[6].x - wx, hand.landmark[6].y - wy)
        mid_folded   = math.hypot(hand.landmark[12].x - wx, hand.landmark[12].y - wy) < math.hypot(hand.landmark[10].x - wx, hand.landmark[10].y - wy)
        ring_folded  = math.hypot(hand.landmark[16].x - wx, hand.landmark[16].y - wy) < math.hypot(hand.landmark[14].x - wx, hand.landmark[14].y - wy)
        pinky_folded = math.hypot(hand.landmark[20].x - wx, hand.landmark[20].y - wy) < math.hypot(hand.landmark[18].x - wx, hand.landmark[18].y - wy)
        # --------------------------------------------------------------

        # TANGAN MENGEPAL (FIST): Ke-4 jari terlipat
        is_fist = idx_folded and mid_folded and ring_folded and pinky_folded

        # METAL (🤘): Telunjuk & Kelingking lurus, Tengah & Manis terlipat
        is_metal = not idx_folded and mid_folded and ring_folded and not pinky_folded

        # OK GESTURE (👌): Jempol & Telunjuk nempel (cubit), 3 jari lainnya lurus
        dist_thumb_idx = math.hypot(hand.landmark[8].x - hand.landmark[4].x, hand.landmark[8].y - hand.landmark[4].y)
        is_ok_gesture  = (dist_thumb_idx < 0.05) and not mid_folded and not ring_folded and not pinky_folded

        if state["game_state"] == "menu":
            # FIX 1 & 2: Wajib masukin PIN Telegram dulu baru boleh ngepal buat start game.
            if is_fist and CURRENT_PLAYER["id"] is not None:
                state["game_state"] = "game"
        elif (
            state["game_over"]
            and state["congrats_timer"] <= 0
            and not screenshot_timer_state["active"]
            and state["go_lock_timer"] == 0
        ):
            if is_ok_gesture: # Gestur OK 👌 (Menggantikan Jempol)
                reset_game()
            elif is_metal:    # Gestur Metal 🤘 (Menggantikan Kelingking)
                state["game_state"] = "menu"
                reset_game()

    if current_pinch:
        state["pinch_grace"] = 3
        pinch = True
    elif state["pinch_grace"] > 0:
        state["pinch_grace"] -= 1
        pinch = True if state["dragging"] else False
    else:
        pinch = False

    if state["game_state"] == "game":

        # ── GAME OVER SCREEN ──
        if state["game_over"]:
            if state["congrats_timer"] > 0:
                pulse = 1.0 + math.sin(state["congrats_timer"] * 0.3) * 0.2
                draw_fancy_text(display_frame, "NEW HIGHSCORE!!!", DISP_W // 2, DISP_H // 2, 80, (0, 255, 255), True, pulsing=pulse)
                state["congrats_timer"] -= 1
                if state["congrats_timer"] == 0:
                    mulai_countdown_screenshot("highscore")
                    if get_nilai_persen() >= 95:
                        state["screenshot_nilai_pending"] = True
            else:
                draw_fancy_text(display_frame, "GAME OVER!",         DISP_W // 2, 220, 90, (0, 0, 255),   True)
                draw_fancy_text(display_frame, f"SKOR AKHIR: {state['score']}", DISP_W // 2, 310, 45, (0, 255, 255), True)
                lvl = get_level_info(state["score"])
                draw_fancy_text(display_frame, f"Level: {lvl['nama']}", DISP_W // 2, 365, 35, lvl["warna"], True)
                draw_crown_logo(display_frame, DISP_W // 2 - 200, 415, 30, (0, 215, 255))
                draw_fancy_text(
                    display_frame,
                    f"HIGHSCORE: {max(state['highscore'], state['score'])}",
                    DISP_W // 2 - 150, 415, 35, (255, 215, 0),
                )
                if nilai_state["total_soal"] > 0:
                    nilai = get_nilai_persen()
                    draw_fancy_text(
                        display_frame,
                        f"Nilai Kuis: {nilai}%  ({nilai_state['benar']}/{nilai_state['total_soal']} benar)",
                        DISP_W // 2, 465, 28, (100, 255, 200), True,
                    )
                if not screenshot_timer_state["active"]:
                    draw_fancy_text(display_frame, "OK (CUBIT): RESTART  |  METAL: MENU UTAMA", DISP_W // 2, 535, 25, (255, 255, 0), is_center=True)
                    if not state["tele_sent"]:
                        if state["score"] <= state["highscore"] and CURRENT_PLAYER["id"]:
                            pesan = (
                                f"Game Over!\nPlayer: {CURRENT_PLAYER['name']}\n"
                                f"Skor: {state['score']}\nHighscore: {state['highscore']}\n"
                                f"Level: {get_level_info(state['score'])['nama']}"
                            )
                            threading.Thread(target=kirim_pesan_tele, args=(pesan,)).start()
                        if get_nilai_persen() >= 95:
                            mulai_countdown_screenshot("nilai_sempurna")
                        kirim_laporan_nilai()
                        state["tele_sent"] = True

            if screenshot_timer_state["active"]:
                screenshot_timer_state["countdown_frames"] -= 1
                if screenshot_timer_state["countdown_frames"] <= 0:
                    tipe      = screenshot_timer_state["type"]
                    path_foto = os.path.abspath(f"{tipe}.jpg")
                    nilai_pct = get_nilai_persen() if tipe == "nilai_sempurna" else None
                    framed    = draw_neon_frame(display_frame, tipe, state["score"], CURRENT_PLAYER["name"], nilai_pct)
                    try:
                        cv2.imwrite(path_foto, framed)
                    except Exception as e:
                        print(f"[System Error] Gagal simpan foto: {e}")

                    if tipe == "highscore":
                        save_highscore(state["score"])
                        state["highscore"] = state["score"]
                        if CURRENT_PLAYER["id"]:
                            msg = (
                                f"REKOR BARU TEMBUS!\nPlayer: {CURRENT_PLAYER['name']}\n"
                                f"Skor Baru: {state['score']}\nMengalahkan rekor lama!"
                            )
                            threading.Thread(target=kirim_foto_tele, args=(path_foto, msg)).start()
                    elif tipe == "nilai_sempurna" and CURRENT_PLAYER["id"]:
                        msg = (
                            f"WOW! {CURRENT_PLAYER['name']} dapat nilai SEMPURNA {get_nilai_persen()}%!\n"
                            f"Semua soal dikerjakan dengan LUAR BIASA!"
                        )
                        threading.Thread(target=kirim_foto_tele, args=(path_foto, msg)).start()

                    screenshot_timer_state["active"] = False
                    if tipe == "highscore" and state["screenshot_nilai_pending"]:
                        state["screenshot_nilai_pending"] = False
                        mulai_countdown_screenshot("nilai_sempurna")
                    if not state["tele_sent"]:
                        kirim_laporan_nilai()
                        state["tele_sent"] = True
                else:
                    draw_screenshot_countdown(display_frame)

        # ── GAMEPLAY ──
        else:
            if not state["paused"]:

                # Wrong-timer countdown
                if quiz_state["active"] and quiz_state["wrong_timer"] > 0:
                    quiz_state["wrong_timer"] -= 1
                    if quiz_state["wrong_timer"] == 0:
                        mulai_kuis(quiz_state["block_idx"])
                        quiz_state["fist_choice"] = -1
                        quiz_state["fist_timer"]  = 0

                # Shake & score scale
                shake_amp = min(15, state["combo"] * 2 + 5) if state["shake_timer"] > 0 else 0
                sx = random.randint(-shake_amp, shake_amp) if shake_amp else 0
                sy = random.randint(-shake_amp, shake_amp) if shake_amp else 0
                if state["shake_timer"] > 0:   state["shake_timer"] -= 1
                if state["score_scale"] > 1.0: state["score_scale"] -= 0.05

                # Pick up block
                if pinch and not state["dragging"] and not quiz_state["active"]:
                    for i, b in enumerate(state["blocks"]):
                        if not b["used"] and math.hypot(state["smooth_x"] - (b["x"] + 70), state["smooth_y"] - (b["y"] + 70)) < 130:
                            if b["locked"]:
                                mulai_kuis(i)
                                quiz_state["fist_choice"] = -1
                                quiz_state["fist_timer"]  = 0
                            else:
                                state["dragging"] = True
                                state["drag_id"]  = i
                            break

                # Drag block
                if state["dragging"] and not quiz_state["active"]:
                    b     = state["blocks"][state["drag_id"]]
                    shape = b["shape"]
                    b["x"] = int(state["smooth_x"] - (len(shape[0]) * CELL) // 2)
                    b["y"] = int(state["smooth_y"] - (len(shape)    * CELL) // 2)
                    gx    = round((b["x"] - BOARD_X) / CELL)
                    gy    = round((b["y"] - BOARD_Y) / CELL)

                    valid_space = False
                    if 0 <= gx <= GRID - len(shape[0]) and 0 <= gy <= GRID - len(shape):
                        valid_space = all(
                            not shape[y][x] or state["board"][gy + y][gx + x] == 0
                            for y in range(len(shape)) for x in range(len(shape[0]))
                        )
                        if valid_space:
                            temp_board = [row[:] for row in state["board"]]
                            for y in range(len(shape)):
                                for x in range(len(shape[0])):
                                    if shape[y][x]:
                                        temp_board[gy + y][gx + x] = 1
                            pred_rows = [r for r in range(GRID) if all(temp_board[r][c] != 0 for c in range(GRID))]
                            pred_cols = [c for c in range(GRID) if all(temp_board[r][c] != 0 for r in range(GRID))]
                            glow_thic = 3 + int(math.sin(pygame.time.get_ticks() / 100.0) * 3)
                            for r in pred_rows:
                                ry = BOARD_Y + r * CELL + sy
                                cv2.rectangle(display_frame, (BOARD_X + sx, ry),     (BOARD_X + GRID * CELL + sx,     ry + CELL), b["color"], glow_thic + 2)
                                cv2.rectangle(display_frame, (BOARD_X + sx + 2, ry + 2), (BOARD_X + GRID * CELL + sx - 2, ry + CELL - 2), (255, 255, 255), 2)
                            for c in pred_cols:
                                rx = BOARD_X + c * CELL + sx
                                cv2.rectangle(display_frame, (rx, BOARD_Y + sy),     (rx + CELL, BOARD_Y + GRID * CELL + sy),     b["color"], glow_thic + 2)
                                cv2.rectangle(display_frame, (rx + 2, BOARD_Y + sy + 2), (rx + CELL - 2, BOARD_Y + GRID * CELL + sy - 2), (255, 255, 255), 2)
                            dark_c = tuple(max(0, c - 120) for c in b["color"])
                            for y in range(len(shape)):
                                for x in range(len(shape[0])):
                                    if shape[y][x]:
                                        rx = BOARD_X + (gx + x) * CELL + sx
                                        ry = BOARD_Y + (gy + y) * CELL + sy
                                        draw_crystal_block(display_frame, rx, ry, CELL, dark_c)
                                        cv2.rectangle(display_frame, (rx, ry), (rx + CELL, ry + CELL), b["color"], 2)

                    # Drop block
                    if not pinch:
                        if 0 <= gx <= GRID - len(shape[0]) and 0 <= gy <= GRID - len(shape) and valid_space:
                            state["score"]       += sum(row.count(1) for row in shape) * 50
                            state["score_scale"]  = 1.3
                            new_level = get_level_info(state["score"])
                            if state["last_level"] and state["last_level"]["nama"] != new_level["nama"]:
                                TEXT_EFFECTS.append({
                                    "x":     DISP_W // 2,
                                    "y":     DISP_H // 2 - 50,
                                    "text":  f"NAIK LEVEL! {new_level['nama']}",
                                    "life":  80,
                                    "color": new_level["warna"],
                                })
                                for _ in range(30):
                                    if len(PARTICLES) >= MAX_PARTICLES:
                                        break
                                    PARTICLES.append({
                                        "x":     DISP_W // 2,
                                        "y":     DISP_H // 2,
                                        "vx":    random.uniform(-12, 12),
                                        "vy":    random.uniform(-14, -4),
                                        "color": new_level["warna"],
                                        "life":  random.randint(25, 55),
                                        "size":  random.randint(5, 11),
                                    })
                            state["last_level"] = new_level
                            for y in range(len(shape)):
                                for x in range(len(shape[0])):
                                    if shape[y][x]:
                                        state["board"][gy + y][gx + x] = b["color"]
                            b["used"] = True
                            if drop_sound:
                                try:
                                    drop_sound.play()
                                except Exception:
                                    pass

                            rows          = [r for r in range(GRID) if all(state["board"][r][c] != 0 for c in range(GRID))]
                            cols          = [c for c in range(GRID) if all(state["board"][r][c] != 0 for r in range(GRID))]
                            total_cleared = len(rows) + len(cols)
                            if total_cleared > 0:
                                state["combo"] += 1
                                bonus           = total_cleared * 500 * state["combo"]
                                state["score"] += bonus
                                state["shake_timer"] = 15
                                if total_cleared >= 3:
                                    state["flash_alpha"] = 100
                                if clear_sound:
                                    clear_sound.play()
                                for r in rows:
                                    for c in range(GRID):
                                        cc = state["board"][r][c] or b["color"]
                                        for _ in range(5):
                                            if len(PARTICLES) >= MAX_PARTICLES:
                                                break
                                            PARTICLES.append({
                                                "x":     BOARD_X + c * CELL + CELL // 2,
                                                "y":     BOARD_Y + r * CELL + CELL // 2,
                                                "vx":    random.uniform(-8, 8),
                                                "vy":    random.uniform(-8, 8),
                                                "color": cc,
                                                "life":  random.randint(15, 35),
                                                "size":  random.randint(4, 10),
                                            })
                                        state["board"][r][c] = 0
                                for c in cols:
                                    for r in range(GRID):
                                        if state["board"][r][c] != 0:
                                            cc = state["board"][r][c]
                                            for _ in range(5):
                                                if len(PARTICLES) >= MAX_PARTICLES:
                                                    break
                                                PARTICLES.append({
                                                    "x":     BOARD_X + c * CELL + CELL // 2,
                                                    "y":     BOARD_Y + r * CELL + CELL // 2,
                                                    "vx":    random.uniform(-8, 8),
                                                    "vy":    random.uniform(-8, 8),
                                                    "color": cc,
                                                    "life":  random.randint(15, 35),
                                                    "size":  random.randint(4, 10),
                                                })
                                            state["board"][r][c] = 0
                                TEXT_EFFECTS.append({
                                    "x":     BOARD_X + 80,
                                    "y":     BOARD_Y + 150,
                                    "text":  f"COMBO x{state['combo']}! +{bonus}",
                                    "life":  30,
                                    "color": (0, 255, 255),
                                })
                            else:
                                state["combo"] = 0

                            if all(bl["used"] for bl in state["blocks"]):
                                state["blocks"]      = state["next_blocks"]
                                state["next_blocks"] = generate_blocks()
                            if not any(can_place_block(bl["shape"], state["board"]) for bl in state["blocks"] if not bl["used"]):
                                state["game_over"]    = True
                                state["go_lock_timer"] = 25
                                if state["score"] > state["highscore"]:
                                    state["congrats_timer"] = 90
                                    for _ in range(120):
                                        if len(PARTICLES) >= MAX_PARTICLES:
                                            break
                                        PARTICLES.append({
                                            "x":     DISP_W // 2,
                                            "y":     DISP_H,
                                            "vx":    random.uniform(-16, 16),
                                            "vy":    random.uniform(-24, -10),
                                            "color": random.choice(BLOCK_COLORS),
                                            "life":  random.randint(45, 85),
                                            "size":  random.randint(5, 12),
                                        })
                                if gameover_sound:
                                    gameover_sound.play()
                        else:
                            b["x"] = X_OFFSET + 150 + state["drag_id"] * 230
                            b["y"] = 575
                        state["dragging"] = False

            else:
                sx, sy = 0, 0

            # ── RENDER BOARD ──
            cv2.rectangle(
                display_frame,
                (BOARD_X - 6 + sx, BOARD_Y - 6 + sy),
                (BOARD_X + GRID * CELL + 6 + sx, BOARD_Y + GRID * CELL + 6 + sy),
                (0, 200, 200), 3,
            )
            for y in range(GRID):
                for x in range(GRID):
                    bx, by = BOARD_X + x * CELL + sx, BOARD_Y + y * CELL + sy
                    cv2.rectangle(display_frame, (bx, by), (bx + CELL, by + CELL), (40, 40, 40), 1)
                    if state["board"][y][x]:
                        draw_crystal_block(display_frame, bx + 2, by + 2, CELL - 4, state["board"][y][x])

            # ── RENDER BLOCKS ──
            for i, b in enumerate(state["blocks"]):
                if b["used"]:
                    continue
                is_hovered       = math.hypot(state["smooth_x"] - (b["x"] + 70), state["smooth_y"] - (b["y"] + 70)) < 130
                is_dragging_this = state["dragging"] and state["drag_id"] == i
                sc = 1.0 if is_dragging_this else (0.75 if is_hovered and not state["dragging"] else 0.6)
                cs = int(CELL * sc)

                for y, row in enumerate(b["shape"]):
                    for x, v in enumerate(row):
                        if not v:
                            continue
                        dx, dy = int(b["x"] + x * cs), int(b["y"] + y * cs)
                        if b["locked"]:
                            dark_c = tuple(max(0, c - 130) for c in b["color"])
                            draw_crystal_block(display_frame, dx, dy, cs, dark_c)
                        else:
                            draw_crystal_block(display_frame, dx, dy, cs, b["color"])
                            if is_hovered and not state["dragging"]:
                                cv2.rectangle(display_frame, (dx, dy), (dx + cs, dy + cs), (0, 255, 255), 4)

                bw, bh    = len(b["shape"][0]), len(b["shape"])
                center_bx = int(b["x"] + (bw * cs) // 2)
                center_by = int(b["y"] + (bh * cs) // 2)

                if b["locked"]:
                    cv2.circle(display_frame, (center_bx, center_by), int(cs * 0.5), (0, 0, 0),       -1)
                    cv2.circle(display_frame, (center_bx, center_by), int(cs * 0.5), (255, 200, 0),    2)
                    draw_lock_icon(display_frame, center_bx, center_by - int(cs * 0.1), int(cs * 0.55))
                    pulse = 1.0 + math.sin(pygame.time.get_ticks() / 200.0) * 0.15
                    draw_fancy_text(display_frame, "PINCH!", center_bx, center_by + int(cs * 0.42), 18, (255, 220, 0), is_center=True, pulsing=pulse)
                elif b.get("unlocked"):
                    draw_fancy_text(display_frame, "V", center_bx, center_by, 22, (0, 255, 150), is_center=True)

            # ── RENDER KUIS ──
            if quiz_state["active"] and quiz_state["wrong_timer"] == 0:
                should_submit = draw_quiz_popup(display_frame, state["smooth_x"], False if state["paused"] else is_fist)
                if should_submit and not quiz_state["show_result"] and not state["paused"]:
                    chosen = quiz_state["selected_choice"]
                    if chosen >= 0:
                        pilihan_dipilih = quiz_state["pilihan"][chosen]
                        is_benar        = (pilihan_dipilih == quiz_state["jawaban_benar"])
                        nilai_state["total_soal"] += 1
                        if is_benar:
                            nilai_state["benar"] += 1
                        else:
                            nilai_state["salah"] += 1
                        nilai_state["riwayat"].append({
                            "soal":           quiz_state["soal"],
                            "jawaban_player": pilihan_dipilih,
                            "jawaban_benar":  quiz_state["jawaban_benar"],
                            "benar":          is_benar,
                        })
                        quiz_state["show_result"]    = True
                        quiz_state["result_correct"] = is_benar
                        quiz_state["fist_choice"]    = -1
                        quiz_state["fist_timer"]     = 0

                        if is_benar:
                            quiz_state["consecutive_wrongs"] = 0
                            if 0 <= quiz_state["block_idx"] < len(state["blocks"]):
                                state["blocks"][quiz_state["block_idx"]]["locked"]   = False
                                state["blocks"][quiz_state["block_idx"]]["unlocked"] = True
                            TEXT_EFFECTS.append({
                                "x":     BOARD_X + 80,
                                "y":     BOARD_Y + 200,
                                "text":  "BENAR! +200 Poin!",
                                "life":  50,
                                "color": (0, 255, 100),
                            })
                            state["score"] += 200
                            tutup_kuis()
                        else:
                            quiz_state["consecutive_wrongs"] += 1
                            if quiz_state["consecutive_wrongs"] >= 2:
                                # ── SALAH 2X BERTURUT-TURUT → GAME OVER ──
                                trigger_game_over("SALAH 2X! GAME OVER!")
                            else:
                                quiz_state["wrong_timer"] = quiz_state["wrong_max"]
                                quiz_state["show_result"] = False
            elif quiz_state["active"] and quiz_state["wrong_timer"] > 0:
                draw_quiz_popup(display_frame, state["smooth_x"], False)


            if state["game_over"]:
                pass
            else:
                # ── FLASH EFFECT ──
                if state["flash_alpha"] > 0:
                    fov = display_frame.copy()
                    cv2.rectangle(fov, (0, 0), (DISP_W, DISP_H), (200, 255, 255), -1)
                    cv2.addWeighted(fov, state["flash_alpha"] / 255.0, display_frame, 1.0 - state["flash_alpha"] / 255.0, 0, display_frame)
                    state["flash_alpha"] = max(0, state["flash_alpha"] - 25)

                # ── HUD ──
                draw_fancy_text(display_frame, f"SKOR: {state['score']}", X_OFFSET + 20, 50, 45, pulsing=state["score_scale"])
                draw_crown_logo(display_frame, X_OFFSET + 20, 90, 20, (0, 215, 255))
                draw_fancy_text(display_frame, f"BEST: {max(state['highscore'], state['score'])}", X_OFFSET + 55, 90, 25, (255, 215, 0))
                if state["combo"] > 1:
                    draw_fancy_text(display_frame, f"COMBO: x{state['combo']}", X_OFFSET + 20, 130, 30, (0, 255, 255))
                lvl  = get_level_info(state["score"])
                prog = get_level_progress(state["score"])
                draw_fancy_text(display_frame, lvl["nama"], X_OFFSET + 20, 165, 22, lvl["warna"])
                cv2.rectangle(display_frame, (X_OFFSET + 20, 178), (X_OFFSET + 180, 188), (50, 50, 50), -1)
                cv2.rectangle(display_frame, (X_OFFSET + 20, 178), (X_OFFSET + 20 + int(160 * prog), 188), lvl["warna"], -1)
                if nilai_state["total_soal"] > 0:
                    nilai   = get_nilai_persen()
                    n_color = (0, 255, 150) if nilai >= 75 else (0, 150, 255) if nilai >= 50 else (0, 60, 255)
                    draw_fancy_text(display_frame, f"Nilai: {nilai}%",                               X_OFFSET + GAME_W - 260, 50, 28, n_color)
                    draw_fancy_text(display_frame, f"({nilai_state['benar']}/{nilai_state['total_soal']} benar)", X_OFFSET + GAME_W - 260, 85, 22, (180, 180, 180))

                for t in TEXT_EFFECTS[:]:
                    draw_fancy_text(display_frame, t["text"], t["x"], t["y"], 35, t.get("color", (0, 255, 255)), is_center=True)
                    t["y"]    -= 4
                    t["life"] -= 1
                    if t["life"] <= 0:
                        TEXT_EFFECTS.remove(t)

                # ── PAUSE OVERLAY ──
                if state["paused"]:
                    pov = display_frame.copy()
                    cv2.rectangle(pov, (0, 0), (DISP_W, DISP_H), (0, 0, 0), -1)
                    cv2.addWeighted(pov, 0.65, display_frame, 0.35, 0, display_frame)
                    draw_fancy_text(display_frame, "GAME PAUSED",                  DISP_W // 2, DISP_H // 2 - 30, 70, (0, 255, 255), is_center=True)
                    draw_fancy_text(display_frame, "Gunakan Gestur T untuk Resume", DISP_W // 2, DISP_H // 2 + 40, 25, (255, 255, 255), is_center=True)

    # ── MENU SCREEN ──
    else:
        cek_pairing_telegram()
        draw_fancy_text(display_frame, "GESTURE BLOCK BLAST", DISP_W // 2, 220, 65, is_center=True)
        if CURRENT_PLAYER["id"] is None:
            draw_fancy_text(display_frame, "Buka @BBgesture_Bot di Tele Anda",  DISP_W // 2, 300, 30, (255, 255, 255), is_center=True)
            draw_fancy_text(display_frame, "Ketik: [Nickname] [Token]",        DISP_W // 2, 350, 32, (255, 255, 255), is_center=True)
            draw_fancy_text(display_frame, f"TOKEN: {ACTIVATION_TOKEN}",       DISP_W // 2, 410, 45, (0, 255, 255),   is_center=True)
            draw_fancy_text(display_frame, "Menunggu koneksi pemain...",        DISP_W // 2, 480, 25, (100, 100, 100), is_center=True)
        else:
            draw_fancy_text(display_frame, f"PLAYER: {CURRENT_PLAYER['name']} (CONNECTED)", DISP_W // 2, 340, 35, (0, 255, 0),     is_center=True)
            draw_fancy_text(display_frame, "Kepal tangan untuk mulai!",                      DISP_W // 2, 430, 30, (255, 255, 255), is_center=True)

    # ── PARTICLES ──
    for p in PARTICLES[:]:
        cv2.rectangle(display_frame, (int(p["x"]), int(p["y"])), (int(p["x"] + p["size"]), int(p["y"] + p["size"])), p["color"], -1)
        p["x"]    += p["vx"]
        p["y"]    += p["vy"]
        p["vy"]   += 0.4
        p["life"] -= 1
        if p["life"] <= 0:
            PARTICLES.remove(p)

    # ── CURSOR ──
    cx, cy       = int(state["smooth_x"]), int(state["smooth_y"])
    cursor_color = (0, 255, 80) if is_fist else (0, 255, 255)
    cursor_r     = 18 if is_fist else 12
    cv2.circle(display_frame, (cx, cy), cursor_r, cursor_color, 3 if is_fist else 2)
    cv2.line(display_frame, (cx - 22, cy),           (cx - cursor_r - 2, cy),  cursor_color, 2)
    cv2.line(display_frame, (cx + cursor_r + 2, cy),  (cx + 22, cy),            cursor_color, 2)
    cv2.line(display_frame, (cx, cy - 22),            (cx, cy - cursor_r - 2),  cursor_color, 2)
    cv2.line(display_frame, (cx, cy + cursor_r + 2),  (cx, cy + 22),            cursor_color, 2)
    if is_fist:
        draw_fancy_text(display_frame, "FIST", cx + 25, cy, 20, (0, 255, 80))

    cv2.imshow("Gesture Block Blast", display_frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
pygame.quit()


