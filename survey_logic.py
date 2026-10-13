import os
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def load_survey_data(grade):
    filename = f"survey_{grade}.json"
    if grade in ["5", "6", "5-6"]:
        filename = "survey_5_6.json"
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def process_submission(form_data):
    """
    Processes form submission according to grade.
    Returns processed entry dict ready for database insertion,
    along with student feedback.
    """
    fish = form_data.get('fish', '').strip()
    sinf = form_data.get('sinf', '').strip()
    sinf_group = form_data.get('sinf_group', '').strip()
    test_type = form_data.get('test_type', '').strip()
    til = form_data.get('til', 'uz').strip()
    fingerprint = form_data.get('fingerprint', '').strip()
    answers = form_data.get('answers', {})

    if not sinf_group:
        from database import parse_sinf_group
        sinf_group = parse_sinf_group(sinf)

    if not test_type:
        if sinf_group in ['5', '6', '5-6']:
            test_type = 'survey_5_6'
        elif sinf_group == '7':
            test_type = 'survey_7'
        elif sinf_group == '8':
            test_type = 'survey_8'
        elif sinf_group == '9':
            test_type = 'survey_9'
        else:
            test_type = 'survey_9'

    entry = {
        'fish': fish,
        'sinf': sinf,
        'sinf_group': sinf_group,
        'test_type': test_type,
        'til': til,
        'fingerprint': fingerprint,
        'answers': answers,
        'score': 0.0,
        'level': '',
        'dominant_scales': '',
        'scale_scores': {},
        'fanlar': '',
        'togaraklar': '',
        'iqtidor': '',
        'kasb': '',
        'startap': 'Yo\'q',
        'yangi_togaraklar': '',
        'takliflar': ''
    }

    feedback = {}

    if test_type == 'survey_7':
        # 7-sinf Tashkilotchilik testi
        positive_7 = [1, 2, 3, 5, 7, 8, 9, 13, 15, 17, 19]
        score = 0.0
        for i in range(1, 21):
            ans = str(answers.get(f'q_{i}', '')).lower()
            if i in positive_7:
                if ans in ['ha', 'да']:
                    score += 1.0
                elif ans in ['bazan', 'иногда']:
                    score += 0.5
            else:
                if ans in ['yoq', 'нет']:
                    score += 1.0
                elif ans in ['bazan', 'иногда']:
                    score += 0.5

        entry['score'] = score
        if score >= 15.0:
            level = "Yuqori daraja" if til == 'uz' else "Высокий уровень"
            desc = "Yuqori darajadagi tashkilotchilik qobiliyati. Sizda yetakchilik, do‘stlaringizni ergashtira olish va yangi tadbirlarni rejalashtirish iqtidori kuchli!" if til == 'uz' else "Высокий уровень организаторских способностей. У вас отличные лидерские качества и умение вести за собой команду!"
        elif score >= 13.0:
            level = "O‘rtacha daraja" if til == 'uz' else "Средний уровень"
            desc = "Tashkilotchilik qobiliyatingiz o‘rtacha darajada. Jamoaviy ishlarda faol ishtirok etib, yetakchilik ko‘nikmalaringizni yanada oshirishingiz mumkin." if til == 'uz' else "Средний уровень организаторских способностей. Вы хорошо работаете в коллективе и можете развивать лидерский потенциал."
        else:
            level = "Past daraja" if til == 'uz' else "Низкий уровень"
            desc = "Tashkilotchilik ko‘rsatkichi biroz pastroq. Siz ko‘proq mustaqil, ijodiy yoki chuqur tahliliy ishlarga moyilsiz. Muloqot va jamoaviy to‘garaklar sizga yordam beradi." if til == 'uz' else "Низкий уровень организаторских способностей. Вам комфортнее в индивидуальной работе, но командные проекты помогут развить уверенность."

        entry['level'] = level
        entry['dominant_scales'] = f"{level} ({score} ball)"
        entry['takliflar'] = desc

        feedback = {
            'title': "Tashkilotchilik qobiliyati testi natijasi" if til == 'uz' else "Результат теста организаторских способностей",
            'score': score,
            'max_score': 20,
            'level': level,
            'description': desc,
            'badge': "Liderlik va Tashkilotchilik" if score >= 15 else ("Faol jamoatchi" if score >= 13 else "Ijodiy tahlilchi")
        }

    elif test_type == 'survey_8':
        # 8-sinf 9 ta shkala
        scales_def = [
            ("sport", "Жисмоний (спорт)", "Физические (спорт)", [1, 10, 19, 28, 37]),
            ("tashkilotchi", "Ташкилотчилик", "Организаторские", [2, 11, 20, 29, 38]),
            ("matematik", "Математик (мантиқий)", "Математические (логика)", [3, 12, 21, 30, 39]),
            ("texnika", "Конструкторлик ва техника", "Конструирование и техника", [4, 13, 22, 31, 40]),
            ("artistic", "Саҳнавий-артистик", "Артистические", [5, 14, 23, 32, 41]),
            ("kommunikativ", "Коммуникатив (мулоқот)", "Коммуникативные", [6, 15, 24, 33, 42]),
            ("musiqiy", "Мусиқий санъат", "Музыкальные", [7, 16, 25, 34, 43]),
            ("tasviriy", "Бадиий-тасвирий", "Художественные", [8, 17, 26, 35, 44]),
            ("filologik", "Филологик (тил-адабиёт)", "Филологические", [9, 18, 27, 36, 45]),
        ]
        scale_scores = {}
        for s_id, s_uz, s_ru, q_nums in scales_def:
            s_pts = 0
            for q_n in q_nums:
                ans = str(answers.get(f'q_{q_n}', '')).lower()
                if ans in ['ha', 'да', '+', '1', 'true']:
                    s_pts += 1
            scale_scores[s_id] = {
                'name': s_uz if til == 'uz' else s_ru,
                'score': s_pts,
                'max': 5
            }

        # Sort top scales
        sorted_scales = sorted(scale_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        top_scales = [f"{s[1]['name']} ({s[1]['score']}/5)" for s in sorted_scales if s[1]['score'] >= 3]
        if not top_scales and sorted_scales:
            top_scales = [f"{sorted_scales[0][1]['name']} ({sorted_scales[0][1]['score']}/5)"]

        entry['scale_scores'] = scale_scores
        entry['score'] = sorted_scales[0][1]['score'] if sorted_scales else 0
        entry['dominant_scales'] = ", ".join(top_scales[:3])
        entry['level'] = f"Yetakchi: {sorted_scales[0][1]['name']}" if til == 'uz' else f"Ведущее: {sorted_scales[0][1]['name']}"

        feedback = {
            'title': "8-sinf Qobiliyat va qiziqishlar diagnostikasi" if til == 'uz' else "Диагностика способностей и интересов (8 класс)",
            'top_scales': top_scales[:3],
            'scale_scores': scale_scores,
            'description': f"Sizning eng yuqori qobiliyatingiz: {sorted_scales[0][1]['name']}. Maktab to‘garaklari va kasb tanlashda ushbu yo‘nalishga e’tibor qaratish tavsiya etiladi." if til == 'uz' else f"Ваша ведущая склонность: {sorted_scales[0][1]['name']}. Рекомендуется развивать эти навыки в профильных кружках.",
            'badge': sorted_scales[0][1]['name']
        }

    elif test_type == 'survey_9':
        # 9-sinf Qiziqishlar xaritasi (10 shkala)
        scales_def = [
            ("fizika_matematika", "Физика ва математика", "Физика и математика", [1, 11, 21, 31, 41]),
            ("kimyo_biologiya", "Химия ва биология", "Химия и биология", [2, 12, 22, 32, 42]),
            ("radiotexnika", "Радиотехника ва электроника", "Радиотехника и электроника", [3, 13, 23, 33, 43]),
            ("mexanika", "Механика ва конструктирлаш", "Механика и конструирование", [4, 14, 24, 34, 44]),
            ("geografiya", "География ва геология", "География и геология", [5, 15, 25, 35, 45]),
            ("adabiyot_sanat", "Адабиёт ва санъат", "Литература и искусство", [6, 16, 26, 36, 46]),
            ("tarix_siyosat", "Тарих ва сиёсат", "История и политика", [7, 17, 27, 37, 47]),
            ("pedagogika_tibbiyot", "Педагогика ва тиббиёт", "Педагогика и медицина", [8, 18, 28, 38, 48]),
            ("tadbirkorlik", "Тадбиркорлик ва бизнес", "Предпринимательство и бизнес", [9, 19, 29, 39, 49]),
            ("sport_harbiy", "Спорт ва ҳарбий соҳа", "Спорт и военное дело", [10, 20, 30, 40, 50]),
        ]
        scale_scores = {}
        for s_id, s_uz, s_ru, q_nums in scales_def:
            s_pts = 0
            for q_n in q_nums:
                ans = str(answers.get(f'q_{q_n}', '')).lower()
                if ans in ['ha', 'да', '+', '1', 'true']:
                    s_pts += 1
            scale_scores[s_id] = {
                'name': s_uz if til == 'uz' else s_ru,
                'score': s_pts,
                'max': 5,
                'level': "Yuqori" if s_pts >= 4 else ("O'rtacha" if s_pts == 3 else "Past")
            }

        sorted_scales = sorted(scale_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        top_scales = [f"{s[1]['name']} ({s[1]['score']}/5)" for s in sorted_scales if s[1]['score'] >= 3]
        if not top_scales and sorted_scales:
            top_scales = [f"{sorted_scales[0][1]['name']} ({sorted_scales[0][1]['score']}/5)"]

        entry['scale_scores'] = scale_scores
        entry['score'] = sorted_scales[0][1]['score'] if sorted_scales else 0
        entry['dominant_scales'] = ", ".join(top_scales[:3])
        entry['level'] = f"Yetakchi kasbiy soha: {sorted_scales[0][1]['name']}" if til == 'uz' else f"Ведущая сфера: {sorted_scales[0][1]['name']}"

        feedback = {
            'title': "9-sinf Kasbiy qiziqishlar xaritasi natijasi" if til == 'uz' else "Карта профессиональных интересов (9 класс)",
            'top_scales': top_scales[:3],
            'scale_scores': scale_scores,
            'description': f"Sizning kelajak kasbiy moyilligingiz: {sorted_scales[0][1]['name']}. Litsey/kollej va OTM tanlashda mazkur soha bo‘yicha ixtisoslashish yuqori muvaffaqiyat keltiradi!" if til == 'uz' else f"Ваша профессиональная предрасположенность: {sorted_scales[0][1]['name']}. Рекомендуется ориентироваться на эту область при выборе лицея/колледжа и вуза!",
            'badge': sorted_scales[0][1]['name']
        }

    else:
        # 5-6 sinf «Mening qiziqishlarim va kelajakdagi kasbim»
        fanlar_ans = answers.get('q_1', [])
        if isinstance(fanlar_ans, list):
            entry['fanlar'] = ", ".join(fanlar_ans)
        else:
            entry['fanlar'] = str(fanlar_ans)

        togarak_ans = answers.get('q_9', [])
        if isinstance(togarak_ans, list):
            entry['togaraklar'] = ", ".join(togarak_ans)
        else:
            entry['togaraklar'] = str(togarak_ans)

        qobiliyat_ans = answers.get('q_3', [])
        if isinstance(qobiliyat_ans, list):
            entry['iqtidor'] = ", ".join(qobiliyat_ans)
        else:
            entry['iqtidor'] = str(qobiliyat_ans)

        # Kasblar (q_6)
        kasb1 = answers.get('q_6_1', '').strip()
        kasb2 = answers.get('q_6_2', '').strip()
        kasb3 = answers.get('q_6_3', '').strip()
        all_kasblar = [k for k in [kasb1, kasb2, kasb3] if k]
        entry['kasb'] = ", ".join(all_kasblar)

        entry['dominant_scales'] = entry['iqtidor'] or entry['fanlar']
        entry['yangi_togaraklar'] = str(answers.get('q_10', '')).strip()
        entry['takliflar'] = str(answers.get('q_14', '') or answers.get('q_15', '')).strip()
        entry['level'] = "Qiziqish va kasbiy moyillik aniqlandi" if til == 'uz' else "Интересы и склонности определены"

        feedback = {
            'title': "5–6-sinf So‘rovnomasi muvaffaqiyatli saqlandi!" if til == 'uz' else "Опрос для 5–6 классов успешно сохранен!",
            'top_scales': [entry['dominant_scales']] if entry['dominant_scales'] else [],
            'kasb': entry['kasb'],
            'description': f"Sizning qiziqishlaringiz va maqsadlaringiz maktab ma’muriyati tomonidan inobatga olinadi. Orzuingizdagi kasbga ({entry['kasb'] or 'tanlagan kasbingizga'}) yetishishingizda muvaffaqiyat tilaymiz!" if til == 'uz' else "Ваши интересы и стремления приняты школьной администрацией. Желаем успехов в достижении вашей мечты!",
            'badge': "Yosh iqtidor egasi" if til == 'uz' else "Юный талант"
        }

    return entry, feedback
