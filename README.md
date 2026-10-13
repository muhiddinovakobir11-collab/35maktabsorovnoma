# 🏛️ 35-Maktab So'rovnoma va Diagnostika Portali (2026)

Ushbu loyiha [sorovnoma35maktab.onrender.com](https://sorovnoma35maktab.onrender.com/) saytining to'liq va takomillashtirilgan nusxasi bo'lib, **Telegram Desktop / Downloads** papkasidagi rasmiy maktab psixologik-diagnostik so'rovnomalari asosida ishlab chiqilgan.

---

## 🎯 Asosiy Imkoniyatlar

### 1. 🎓 O'quvchilar So'rovnoma Tizimi (`/`)
* **Sinfga qarab avtomatik moslashuv**: O'quvchi o'z sinfini (5-A dan 11-I gacha) tanlashi bilan tegishli rasmiy test avtomatik yuklanadi:
  * 🟢 **5–6-sinflar uchun**: «Mening qiziqishlarim va kelajakdagi kasbim» (15 ta keng qamrovli savol, sevimli fanlar, 3 ta kelajak kasbi, to'garaklar taklifi).
  * 🔵 **7-sinf uchun**: «Tashkilotchilik qobiliyatini aniqlash testi» (20 ta savol, 20 ballik tizim, avtomatik yetakchilik darajasini aniqlash: Yuqori / O'rtacha / Past).
  * 🟣 **8-sinf uchun**: «Qiziqishlar, qobiliyatlar va intilishlarni aniqlash metodikasi» (45 ta savol, 9 ta psixologik shkala: Sport, Tashkilotchilik, Matematik, Texnika, Artistik, Muloqot, Musiqa, Tasviriy san'at, Filologiya).
  * 🟠 **9-sinflar (va yuqori sinflar) uchun**: «Qiziqishlar xaritasi metodikasi» (A.E. Golomshtok & G.V. Resapkina, 50 ta savol, 10 ta kasbiy soha bo'yicha chuqur tahlil).
* **Ko'p tillilik (Bilingual)**: 🇺🇿 O'zbekcha va 🇷🇺 Ruscha variantlar to'liq mavjud.
* **Tezkor natija modali**: O'quvchi testni tugatishi bilanoq ekranda o'z balli, yetakchi iqtidori va tavsiyalar ko'rsatiladi.

### 2. 👨‍🏫 Sinf Rahbari Portali (`/oqituvchi`)
* Sinf rahbarlari o'z sinfini tanlab:
  * Qatnashgan o'quvchilar soni va foizini ko'rish;
  * Sinf bo'yicha o'rtacha tashkilotchilik balli va yetakchi qobiliyatlarni tahlil qilish;
  * Har bir o'quvchining shaxsiy javoblarini modalda batafsil ko'rish;
  * **Sinf bo'yicha tayyor Excel hisobotini** yuklab olish (`.xlsx`);
  * Maktab hujjatlari uchun **A4 formatda to'g'ridan-to'g'ri chop etish**.

### 3. 🔒 Bosh Admin Portali (`/admin`)
* **Kirish paroli**: `admin2026`
* **Umumiy statistika kartalari**: Jami anketalar, 5-6 sinflar, 7-sinflar, 8-sinflar, 9-sinflar kesimida.
* **765+ ta oldingi natijalar integratsiyasi**: Oldingi Excel bazasidagi barcha ma'lumotlar saqlangan.
* **Filtrlash va qidiruv**:
  * Real vaqt rejimida F.I.Sh., kasb yoki qobiliyat bo'yicha qidiruv;
  * Sinflar (5-A ... 11-I) bo'yicha filter;
  * Til (O'zbek / Rus) bo'yicha filter;
  * Darajalar (Yuqori, O'rtacha, Past) bo'yicha filter.
* **O'quvchi dosyesi (ko'rish)**: Shkalalar ballari, qiziqishlar, kelajak kasbi va takliflar to'liq tahlili.
* **Qo'shish, tahrirlash va o'chirish** imkoniyati.
* **QR-kod va havola ulashish**: Telegram guruhlariga yuborish uchun tayyor havola.
* **Eksport**: Barcha ma'lumotlarni ko'p varaqli (`openpyxl`) chiroyli uslubdagi `.xlsx` faylga eksport qilish.

### 4. 📊 Tahliliy Grafika Sahifasi (`/admin/stats`)
* Sinflar va guruhlar bo'yicha qatnashish foizlari diagrammalari.

---

## 🚀 Qanday ishga tushiriladi?

### 1-usul (Windows `run.bat` orqali):
Loyiha papkasidagi [`run.bat`](file:///C:/Users/user/.gemini/antigravity/scratch/maktab35_sorovnoma/run.bat) faylini sichqoncha bilan ikki marta bosing.

### 2-usul (PowerShell orqali):
```powershell
cd C:\Users\user\.gemini\antigravity\scratch\maktab35_sorovnoma
.\.venv\Scripts\python.exe app.py
```

Server ishga tushgach:
* Asosiy so'rovnoma: [http://localhost:5000](http://localhost:5000)
* Sinf rahbarlari portali: [http://localhost:5000/oqituvchi](http://localhost:5000/oqituvchi)
* Admin paneli: [http://localhost:5000/admin](http://localhost:5000/admin) (Parol: `admin2026`)
