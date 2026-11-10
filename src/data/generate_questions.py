import json

with open('/home/antigravity/medterm-estrategia/src/data/termsCatalog.js', 'r', encoding='utf-8') as f:
    content = f.read()
    json_str = content[content.find('['):content.rfind(']')+1]
    terms = json.loads(json_str)

terms_by_id = {t['id']: t for t in terms}
terms_by_name = {t['term'].lower(): t for t in terms}

questions = []
used_stems = set()

# Helper para balancear gabaritos (A, B, C, D)
letters = ['A', 'B', 'C', 'D']

def add_q(q):
    stem_norm = q['stem'].strip().lower()
    if stem_norm in used_stems:
        raise ValueError(f"Stem duplicado: {q['stem']}")
    used_stems.add(stem_norm)
    questions.append(q)

# -------------------------------------------------------------
# BLOCO 1: Q001 a Q110 (110 Questões: Definição Direta "Termo -> Significado")
# -------------------------------------------------------------
for i, t in enumerate(terms):
    num = i + 1
    qid = f"Q{num:03d}"
    correct_letter = letters[i % 4]
    
    # Selecionar 3 distratores inteligentes da lista
    distractors_pool = [x for x in terms if x['id'] != t['id']]
    # priorizar os de sistema parecido ou id próximo
    distractors_sorted = sorted(distractors_pool, key=lambda x: (x['system'] != t['system'], abs(x['id'] - t['id'])))
    d1, d2, d3 = distractors_sorted[0], distractors_sorted[1], distractors_sorted[2]
    
    opts_map = {}
    remaining_dist = [d1, d2, d3]
    
    for l in letters:
        if l == correct_letter:
            opts_map[l] = {
                "letter": l,
                "text": t['definition'],
                "explanation": f"Gabarito correto. {t['term']} caracteriza-se clinicamente por: {t['definition']} Origem etimológica: {t['etymology']}."
            }
        else:
            d = remaining_dist.pop(0)
            opts_map[l] = {
                "letter": l,
                "text": d['definition'],
                "explanation": f"Incorreta. Esta é a definição semiológica exata de «{d['term']}», e não de {t['term']}."
            }
            
    stem = f"No exame semiológico e na prática clínica, o termo técnico «{t['term']}» refere-se a:"
    
    q = {
        "id": qid,
        "number": num,
        "termId": t['id'],
        "term": t['term'],
        "system": t['system'],
        "angle": "Definição Direta",
        "difficulty": "Essencial",
        "stem": stem,
        "options": [opts_map['A'], opts_map['B'], opts_map['C'], opts_map['D']],
        "correctLetter": correct_letter,
        "etymologyNote": t['etymology'],
        "pearl": f"Pérola Estratégia MED: Lembre-se de que {t['term']} tem como essência clínica «{t['clinicalSummary']}». Atenção para não confundir com {t['confusableWith']}."
    }
    add_q(q)

# -------------------------------------------------------------
# BLOCO 2: Q111 a Q220 (110 Questões: Termo Reverso "Significado -> Termo")
# -------------------------------------------------------------
for i, t in enumerate(terms):
    num = 110 + i + 1
    qid = f"Q{num:03d}"
    correct_letter = letters[(i + 1) % 4]
    
    distractors_pool = [x for x in terms if x['id'] != t['id']]
    distractors_sorted = sorted(distractors_pool, key=lambda x: (x['system'] != t['system'], abs(x['id'] - t['id'])))
    d1, d2, d3 = distractors_sorted[1], distractors_sorted[2], distractors_sorted[3]
    
    opts_map = {}
    remaining_dist = [d1, d2, d3]
    
    for l in letters:
        if l == correct_letter:
            opts_map[l] = {
                "letter": l,
                "text": t['term'],
                "explanation": f"Gabarito correto. «{t['term']}» é a terminologia técnica exata para {t['definition'].lower()}."
            }
        else:
            d = remaining_dist.pop(0)
            opts_map[l] = {
                "letter": l,
                "text": d['term'],
                "explanation": f"Incorreta. «{d['term']}» designa especificamente {d['definition'].lower()}."
            }
            
    stem = f"A manifestação clínica caracterizada por «{t['definition']}» recebe a denominação técnica de:"
    
    q = {
        "id": qid,
        "number": num,
        "termId": t['id'],
        "term": t['term'],
        "system": t['system'],
        "angle": "Termo Reverso",
        "difficulty": "Essencial",
        "stem": stem,
        "options": [opts_map['A'], opts_map['B'], opts_map['C'], opts_map['D']],
        "correctLetter": correct_letter,
        "etymologyNote": t['etymology'],
        "pearl": f"Pérola Prática: Ao registrar em prontuário, a síntese técnica correta para este achado semiológico é «{t['term']}»."
    }
    add_q(q)

# -------------------------------------------------------------
# BLOCO 3: Q221 a Q330 (110 Questões: Diagnóstico Diferencial & Pares Confusos)
# -------------------------------------------------------------
for i, t in enumerate(terms):
    num = 220 + i + 1
    qid = f"Q{num:03d}"
    correct_letter = letters[(i + 2) % 4]
    
    confusables = [x.strip() for x in t['confusableWith'].split(',') if x.strip()]
    first_conf = confusables[0] if confusables else "outros termos semiológicos"
    
    stem = f"Em semiologia médica, para distinguir rigorosamente «{t['term']}» de «{first_conf}», assinale o achado exclusivo de {t['term']}:"
    
    chosen_distractors = []
    seen_texts = {f"{t['term']}: {t['clinicalSummary']}.".strip().lower()}
    
    # Tentar primeiro o confusable direto se for diferente
    d_first = terms_by_name.get(first_conf.lower())
    if d_first and d_first['id'] != t['id']:
        cand_text = f"{d_first['term']}: {d_first['clinicalSummary']}.".strip().lower()
        if cand_text not in seen_texts:
            seen_texts.add(cand_text)
            chosen_distractors.append(d_first)
            
    for step in range(1, len(terms)):
        candidate = terms[(i + step * 11) % len(terms)]
        if candidate['id'] != t['id']:
            cand_text = f"{candidate['term']}: {candidate['clinicalSummary']}.".strip().lower()
            if cand_text not in seen_texts:
                seen_texts.add(cand_text)
                chosen_distractors.append(candidate)
                if len(chosen_distractors) == 3:
                    break
                    
    d1, d2, d3 = chosen_distractors[0], chosen_distractors[1], chosen_distractors[2]
    
    opts_map = {}
    remaining_dist = [d1, d2, d3]
    
    for l in letters:
        if l == correct_letter:
            opts_map[l] = {
                "letter": l,
                "text": f"{t['term']}: {t['clinicalSummary']}.",
                "explanation": f"Gabarito correto. O elemento diferencial definidor de {t['term']} reside em: {t['definition']}."
            }
        else:
            d = remaining_dist.pop(0)
            opts_map[l] = {
                "letter": l,
                "text": f"{d['term']}: {d['clinicalSummary']}.",
                "explanation": f"Incorreta. Esta descrição corresponde estritamente ao quadro semiológico de {d['term']}."
            }
            
    q = {
        "id": qid,
        "number": num,
        "termId": t['id'],
        "term": t['term'],
        "system": t['system'],
        "angle": "Pares Confusos",
        "difficulty": "Médio",
        "stem": stem,
        "options": [opts_map['A'], opts_map['B'], opts_map['C'], opts_map['D']],
        "correctLetter": correct_letter,
        "etymologyNote": t['etymology'],
        "pearl": f"Pegadinha Clássica de Prova Prática: Nunca confunda {t['term']} com {first_conf}. Lembre-se: {t['clinicalSummary']}!"
    }
    add_q(q)

# -------------------------------------------------------------
# BLOCO 4: Q331 a Q440 (110 Questões: Morfologia Médica & Etimologia dos 110 Termos)
# -------------------------------------------------------------
for i, t in enumerate(terms):
    num = 330 + i + 1
    qid = f"Q{num:03d}"
    correct_letter = letters[(i + 3) % 4]
    
    stem = f"Considerando a formação mórfica e etimológica dos vocábulos médicos, os elementos constitutivos de «{t['term']}» significam:"
    
    # Selecionar 3 termos cujas etimologias sejam estritamente distintas entre si e do termo t
    chosen_distractors = []
    seen_texts = {t['etymology'].strip().lower()}
    
    # percorrer com offset baseado no índice
    for step in range(1, len(terms)):
        candidate = terms[(i + step * 7) % len(terms)]
        c_etym = candidate['etymology'].strip().lower()
        if c_etym not in seen_texts:
            seen_texts.add(c_etym)
            chosen_distractors.append(candidate)
            if len(chosen_distractors) == 3:
                break
                
    e1, e2, e3 = chosen_distractors[0], chosen_distractors[1], chosen_distractors[2]
    
    opts_map = {}
    remaining_dist = [e1, e2, e3]
    
    for l in letters:
        if l == correct_letter:
            opts_map[l] = {
                "letter": l,
                "text": t['etymology'],
                "explanation": f"Gabarito correto. A etimologia exata de {t['term']} deriva de {t['etymology']}, justificando seu significado semiológico."
            }
        else:
            d = remaining_dist.pop(0)
            opts_map[l] = {
                "letter": l,
                "text": d['etymology'],
                "explanation": f"Incorreta. Esta é a decomposição etimológica de «{d['term']}» ({d['definition']})."
            }
            
    q = {
        "id": qid,
        "number": num,
        "termId": t['id'],
        "term": t['term'],
        "system": t['system'],
        "angle": "Etimologia",
        "difficulty": "Médio",
        "stem": stem,
        "options": [opts_map['A'], opts_map['B'], opts_map['C'], opts_map['D']],
        "correctLetter": correct_letter,
        "etymologyNote": t['etymology'],
        "pearl": f"Macete de Memorização: Dominar os formantes ({t['etymology']}) permite deduzir qualquer questão sobre {t['term']} sem decorar."
    }
    add_q(q)

# -------------------------------------------------------------
# BLOCO 5: Q441 a Q500 (60 Questões: Semiologia Integrada & Sinais Vitais Rápidos)
# -------------------------------------------------------------
vital_topics = [
    # 1. Normocardia vs Taqui vs Bradi
    ("Em relação à frequência cardíaca em repouso no adulto, a faixa fisiológica de «Normocardia» compreende:",
     "Cardiovascular & Sinais Vitais", "Normocardia", "norma + kardia + -ia",
     [("60 a 100 batimentos por minuto.", "Correta. Valores entre 60 e 100 bpm caracterizam a normocardia em adultos em repouso."),
      ("50 a 90 batimentos por minuto.", "Incorreta. 50 bpm já é considerado bradicardia em adultos sedentários."),
      ("70 a 110 batimentos por minuto.", "Incorreta. Valores acima de 100 bpm em repouso já configuram taquicardia."),
      ("40 a 80 batimentos por minuto.", "Incorreta. Faixa abaixo do padrão fisiológico normal de repouso.")]),
      
    # 2. Bradicardia
    ("A frequência cardíaca de repouso no adulto é classificada como «Bradicardia» quando:",
     "Cardiovascular & Sinais Vitais", "Bradicardia", "bradys + kardia",
     [("Inferior a 60 batimentos por minuto.", "Correta. FC < 60 bpm define rigorosamente bradicardia."),
      ("Inferior a 50 batimentos por minuto.", "Incorreta. O ponto de corte semiológico clássico é 60 bpm."),
      ("Entre 60 e 70 batimentos por minuto.", "Incorreta. Esta faixa encontra-se dentro da normocardia."),
      ("Inferior a 40 batimentos por minuto apenas.", "Incorreta. FC < 40 bpm é bradicardia grave, mas < 60 já é bradicardia.")]),

    # 3. Taquicardia
    ("Na avaliação dos sinais vitais, constata-se «Taquicardia» quando a frequência cardíaca de repouso é:",
     "Cardiovascular & Sinais Vitais", "Taquicardia", "tachys + kardia",
     [("Superior a 100 batimentos por minuto.", "Correta. FC > 100 bpm em repouso define taquicardia no adulto."),
      ("Superior a 90 batimentos por minuto.", "Incorreta. Até 100 bpm ainda é considerado limite de normocardia."),
      ("Superior a 120 batimentos por minuto apenas.", "Incorreta. Acima de 100 bpm já há taquicardia clínica."),
      ("Entre 80 e 100 batimentos por minuto.", "Incorreta. Esta faixa é estritamente normocárdica.")]),

    # 4. Bradisfigmia vs Bradicardia
    ("O conceito semiológico de «Bradisfigmia» refere-se pontualmente a:",
     "Cardiovascular & Pulsos", "Bradisfigmia", "bradys + sphygmos",
     [("Frequência de pulso periférico inferior a 60 pulsações por minuto.", "Correta. Bradisfigmia avalia a frequência do pulso arterial periférico."),
      ("Frequência cardíaca central auscultada na ponta do coração.", "Incorreta. A ausculta cardíaca apical avalia bradicardia, não pulso periférico."),
      ("Diferença de amplitude entre os pulsos radiais direito e esquerdo.", "Incorreta. A assimetria de pulso é outra alteração semiológica."),
      ("Parada momentânea dos batimentos cardíacos.", "Incorreta. Parada transitória denomina-se assistolia ou pausa sinusal.")]),

    # 5. Eupneia
    ("No padrão respiratório normal do adulto em repouso («Eupneia»), a frequência respiratória fisiológica é:",
     "Cardiorrespiratório & Sinais Vitais", "Eupneia", "eu- + pnoia",
     [("12 a 20 incursões respiratórias por minuto.", "Correta. Padrão eupneico adulto oscila entre 12 e 20 irpm."),
      ("8 a 12 incursões respiratórias por minuto.", "Incorreta. Valores abaixo de 12 irpm caracterizam bradipneia."),
      ("16 a 28 incursões respiratórias por minuto.", "Incorreta. Acima de 20 irpm já configura taquipneia."),
      ("20 a 30 incursões respiratórias por minuto.", "Incorreta. Faixa taquipneica patológica.")]),

    # 6. Bradipneia
    ("Classifica-se o padrão ventilatório do adulto como «Bradipneia» quando a frequência respiratória é:",
     "Cardiorrespiratório & Sinais Vitais", "Bradipneia", "bradys + pnoia",
     [("Menor que 12 incursões respiratórias por minuto.", "Correta. FR < 12 irpm define bradipneia no adulto."),
      ("Menor que 16 incursões respiratórias por minuto.", "Incorreta. 12 a 16 irpm é fisiológico."),
      ("Menor que 8 incursões respiratórias por minuto apenas.", "Incorreta. FR < 8 é depressão respiratória grave, mas < 12 já é bradipneia."),
      ("Entre 12 e 14 incursões respiratórias por minuto.", "Incorreta. 12 a 14 irpm é padrão normal eupneico.")]),

    # 7. Taquipneia
    ("O achado semiológico de «Taquipneia» no adulto em repouso estabelece-se com frequência respiratória:",
     "Cardiorrespiratório & Sinais Vitais", "Taquipneia", "tachys + pnoia",
     [("Superior a 20 incursões respiratórias por minuto.", "Correta. FR > 20 irpm define taquipneia no adulto."),
      ("Superior a 16 incursões respiratórias por minuto.", "Incorreta. Até 20 irpm ainda é considerado normal."),
      ("Superior a 30 incursões respiratórias por minuto apenas.", "Incorreta. Ponto de corte é 20 irpm."),
      ("Entre 14 e 18 incursões respiratórias por minuto.", "Incorreta. Esta é a faixa normal de eupneia.")]),

    # 8. Ortopneia
    ("A queixa de paciente que refere necessidade de dormir apoiado em três travesseiros para respirar traduz:",
     "Cardiorrespiratório", "Ortopneia", "orthos + pnoia",
     [("Ortopneia.", "Correta. Dispneia ao decúbito horizontal aliviada pela elevação do tronco define ortopneia."),
      ("Trepopneia.", "Incorreta. Trepopneia é dispneia em decúbito lateral específico."),
      ("Platipneia.", "Incorreta. Platipneia é dispneia na posição ereta que melhora ao deitar."),
      ("Apneia obstrutiva.", "Incorreta. Apneia é a parada respiratória completa.")]),

    # 9. Assepsia vs Antissepsia
    ("A higienização cirúrgica e o uso de clorexidina nas mãos do profissional de saúde constituem exemplo de:",
     "Procedimentos & Biossegurança", "Antissepsia", "anti- + sepsis",
     [("Antissepsia.", "Correta. Aplicação de agentes germicidas em tecidos vivos é antissepsia."),
      ("Assepsia.", "Incorreta. Assepsia é o conjunto de métodos em superfícies inanimadas para evitar contaminação."),
      ("Esterilização.", "Incorreta. Esterilização destrói todas as formas de vida microbiana em materiais inanimados."),
      ("Desinfecção de alto nível.", "Incorreta. Desinfecção aplica-se a artigos inanimados.")]),

    # 10. Assepsia
    ("A utilização de campos cirúrgicos estéreis e autoclave para instrumentalização médica visa primariamente garantir:",
     "Procedimentos & Biossegurança", "Assepsia", "a- + sepsis",
     [("Assepsia do campo operatório.", "Correta. A manutenção de meio inanimado livre de microrganismos é a assepsia."),
      ("Antissepsia profilática dos tecidos.", "Incorreta. Antissepsia ocorre no tecido vivo do paciente/equipe."),
      ("Cura de infecção instalada.", "Incorreta. Visa prevenir a inoculação de germes exógenos."),
      ("Degermação tecidual ativa.", "Incorreta. Degermação refere-se à remoção mecânica em pele viva.")]),

    # 11. Sinais Flogísticos (4 clássicos de Celso)
    ("Os quatro sinais flogísticos clássicos descritos por Cornélio Celso na tétrade da inflamação aguda são:",
     "Tegumentar & Inflamatório", "Sinais flogísticos", "phlogistos (inflamado)",
     [("Rubor, Calor, Tumor (edema) e Dor.", "Correta. Esta é a célebre tétrade celciana da inflamação aguda."),
      ("Palidez, Frio, Cianose e Anestesia.", "Incorreta. Correspondem a sinais de isquemia tecidual aguda."),
      ("Icterícia, Prurido, Acolia e Colúria.", "Incorreta. Correspondem à síndrome colestática."),
      ("Pápula, Vesícula, Bolha e Pústula.", "Incorreta. São lesões dermatológicas elementares primárias.")]),

    # 12. 5º sinal de Virchow
    ("Na evolução do estudo da inflamação, Rudolf Virchow acrescentou à tétrade de Celso o quinto sinal flogístico:",
     "Tegumentar & Inflamatório", "Sinais flogísticos", "Functio laesa",
     [("Perda de função (functio laesa).", "Correta. A perda funcional é o quinto sinal inflamatório de Virchow."),
      ("Necrose liquefativa.", "Incorreta. Necrose é morte celular irreversível."),
      ("Supuração ativa.", "Incorreta. Supuração é formação de abscesso purulento."),
      ("Febre sistêmica.", "Incorreta. Febre é manifestação sistêmica da resposta inflamatória.")]),

    # 13. Cacifo / Sinal de Godet
    ("Ao comprimir com o polegar o terço distal da tíbia de paciente edemaciado e observar depressão duradoura, afere-se:",
     "Tegumentar & Exame Físico", "Cacifo", "caccabus",
     [("Sinal de Godet ou cacifo positivo.", "Correta. O afundamento persistente no edema tecidual caracteriza o sinal de Godet (cacifo)."),
      ("Sinal de Homans positivo.", "Incorreta. Homans é dor na panturrilha à dorsiflexão do pé na TVP."),
      ("Sinal de Giordano positivo.", "Incorreta. Giordano é dor à punho-percussão lombar na pielonefrite."),
      ("Sinal de Blumberg positivo.", "Incorreta. Blumberg é dor à descompressão súbita no abdome peritoneal.")]),

    # 14. Anúria
    ("Em paciente internado em UTI com sonda vesical, define-se «Anúria» quando o débito urinário em 24 horas for:",
     "Geniturinário & Nefrologia", "Anúria", "an- + ouron",
     [("Inferior a 100 mL nas 24 horas.", "Correta. Volume < 100 mL/24h é a definição clássica de anúria."),
      ("Inferior a 400 mL nas 24 horas.", "Incorreta. Volume entre 100 e 400 mL/24h define oligúria."),
      ("Zero absoluto durante 48 horas obrigatoriamente.", "Incorreta. Abaixo de 100 mL/24h já se estabelece anúria."),
      ("Entre 100 e 200 mL nas 24 horas.", "Incorreta. Esta faixa encaixa-se em oligúria grave.")]),

    # 15. Oligúria
    ("No adulto, a classificação de «Oligúria» fundamenta-se na aferição de um volume urinário em 24 horas inferior a:",
     "Geniturinário & Sinais Vitais", "Oligúria", "oligos + ouron",
     [("400 a 500 mL por dia.", "Correta. Diurese < 400-500 mL/24h (ou < 0,5 mL/kg/h) caracteriza oligúria."),
      ("100 mL por dia.", "Incorreta. Menor que 100 mL/24h já configura anúria."),
      ("1.000 mL por dia.", "Incorreta. 1.000 mL/dia é um volume urinário normal."),
      ("800 mL por dia.", "Incorreta. Volume fisiologicamente aceitável em baixa ingestão hídrica.")]),

    # 16. Poliúria
    ("O volume urinário é tecnicamente rotulado como «Poliúria» quando a excreção líquida nas 24 horas supera:",
     "Geniturinário & Sinais Vitais", "Poliúria", "polys + ouron",
     [("2.500 a 3.000 mL por dia.", "Correta. Diurese > 2.500-3.000 mL/24h estabelece o quadro de poliúria."),
      ("1.500 mL por dia.", "Incorreta. 1.500 mL/dia é a média fisiológica padrão do adulto."),
      ("2.000 mL por dia.", "Incorreta. Volume ainda dentro do limite superior normal."),
      ("4.000 mL por dia apenas.", "Incorreta. Acima de 2.500 mL já se diagnostica poliúria.")]),

    # 17. Polaciúria vs Poliúria
    ("Diferencia-se «Polaciúria» de «Poliúria» pelo fato de que na polaciúria ocorre:",
     "Geniturinário", "Polaciúria", "pollakis + ouron",
     [("Aumento na frequência das micções, mantendo volume total diário normal ou baixo.", "Correta. Polaciúria é ir várias vezes ao banheiro urinar pouco volume."),
      ("Aumento maciço no volume urinário total excretado em 24 horas.", "Incorreta. Este é o conceito exato de poliúria."),
      ("Presença de bactérias e pus macroscópico na urina.", "Incorreta. Presença de pus é piúria."),
      ("Perda involuntária de urina durante a tosse.", "Incorreta. Caracteriza incontinência urinária de esforço.")]),

    # 18. Nictúria vs Enurese
    ("O paciente que acorda conscientemente diversas vezes à noite para urinar apresenta:",
     "Geniturinário", "Nictúria", "nyx + ouron",
     [("Nictúria.", "Correta. Micção noturna voluntária e consciente que interrompe o sono é nictúria."),
      ("Enurese.", "Incorreta. Enurese é a micção involuntária e inconsciente que molha a cama."),
      ("Polaciúria isolada.", "Incorreta. Quando ocorre predominantemente no período noturno, o termo é nictúria."),
      ("Disúria noturna.", "Incorreta. Disúria refere-se à dor ou ardor miccional.")]),

    # 19. Disúria
    ("A sensação dolorosa, em queimação ou desconforto durante a micção recebe o nome técnico de:",
     "Geniturinário & Urgências", "Disúria", "dys- + ouron",
     [("Disúria.", "Correta. Dor ou desconforto à micção define disúria."),
      ("Tenesmo vesical.", "Incorreta. Tenesmo é espasmo doloroso com sensação de esvaziamento incompleto."),
      ("Estrangúria.", "Incorreta. Estrangúria é micção lenta, gota a gota e com espasmos extremos."),
      ("Piúria.", "Incorreta. Piúria é a presença de pus na urina.")]),

    # 20. Piúria
    ("A presença macroscópica de pus ou grande quantidade de leucócitos no sedimento urinário denomina-se:",
     "Geniturinário & Nefrologia", "Piúria", "pyon + ouron",
     [("Piúria.", "Correta. Pus na urina define piúria."),
      ("Hematúria.", "Incorreta. Hematúria é presença de sangue na urina."),
      ("Colúria.", "Incorreta. Colúria é urina escura cor de coca-cola por bilirrubina conjugada."),
      ("Proteinúria.", "Incorreta. Proteinúria é eliminação excessiva de proteínas.")]),

    # 21. Hematúria
    ("A visualização direta de sangue na urina ou detecção de eritrócitos ao exame microscópico é denominada:",
     "Geniturinário & Urgências", "Hematúria", "haima + ouron",
     [("Hematúria.", "Correta. Presença de sangue na urina é hematúria."),
      ("Mioglobinúria.", "Incorreta. Mioglobinúria é excreção de mioglobina muscular."),
      ("Hemoptise.", "Incorreta. Hemoptise é sangue das vias aéreas inferiores expelido com tosse."),
      ("Hematoquezia.", "Incorreta. Hematoquezia é sangue nas fezes.")]),

    # 22. Hematêmese vs Hemoptise
    ("Ao atender paciente que eliminou sangue com a tosse, com aspecto espumoso e avermelhado, o registro técnico deve ser:",
     "Cardiorrespiratório & Hemorragia", "Hemoptise", "haima + ptysis",
     [("Hemoptise.", "Correta. Sangue eliminado pelo trato respiratório com tosse é hemoptise."),
      ("Hematêmese.", "Incorreta. Hematêmese é sangue eliminado pelo vômito (trato digestivo)."),
      ("Epistaxe.", "Incorreta. Epistaxe é sangramento das cavidades nasais."),
      ("Melena.", "Incorreta. Melena é sangue digerido eliminado nas fezes.")]),

    # 23. Hematêmese
    ("O vômito com sangue escurecido em aspecto de «borra de café» decorrente de sangramento gástrico denomina-se:",
     "Gastrointestinal & Hemorragia", "Hematêmese", "haima + emesis",
     [("Hematêmese.", "Correta. Vômito hemático proveniente do trato gastrointestinal alto é hematêmese."),
      ("Hemoptise.", "Incorreta. Sangue proveniente dos brônquios/pulmões."),
      ("Sialorreia.", "Incorreta. Sialorreia é salivação excessiva."),
      ("Eructação.", "Incorreta. Eructação é eliminação de gases pela boca.")]),

    # 24. Melena
    ("A eliminação retal de fezes pretas, pegajosas como piche e extremamente fétidas traduz:",
     "Gastrointestinal & Hemorragia", "Melena", "melas",
     [("Melena.", "Correta. Sangue digerido de hemorragia digestiva alta resulta em melena."),
      ("Hematoquezia.", "Incorreta. Hematoquezia é sangue vermelho vivo nas fezes."),
      ("Enterorragia.", "Incorreta. Enterorragia é sangue rutilante abundante pelo ânus."),
      ("Esteatorreia.", "Incorreta. Esteatorreia é gordura nas fezes.")]),

    # 25. Hematoquezia vs Enterorragia
    ("A eliminação anal de fezes com raias de sangue vermelho vivo exteriorizadas junto ao bolo fecal denomina-se:",
     "Gastrointestinal & Hemorragia", "Hematoquezia", "haima + chezo",
     [("Hematoquezia.", "Correta. Sangue vivo misturado ou sobre as fezes é hematoquezia."),
      ("Melena.", "Incorreta. Melena são fezes pretas e pastosas."),
      ("Hematêmese.", "Incorreta. Hematêmese é vômito de sangue."),
      ("Disenteria.", "Incorreta. Disenteria é síndrome infecciosa com fezes diarreicas muco-sanguinolentas.")]),

    # 26. Disfagia vs Odinofagia
    ("Diferencia-se «Disfagia» de «Odinofagia» porque na odinofagia o paciente apresenta primordialmente:",
     "Gastrointestinal & Otorrino", "Odinofagia", "odyne + phagein",
     [("Dor ou queimação durante o ato de engolir.", "Correta. Odinofagia é a deglutição dolorosa."),
      ("Engasgo mecânico por estenose esofágica sem dor.", "Incorreta. Dificuldade de trânsito é disfagia motora ou mecânica."),
      ("Impossibilidade completa de falar.", "Incorreta. Perda da fala é afasia ou afonia."),
      ("Sensação de boca seca.", "Incorreta. Boca seca é xerostomia.")]),

    # 27. Pirose
    ("A queixa clínica de sensação de queimação retroesternal que sobe do estômago em direção à garganta traduz:",
     "Gastrointestinal", "Pirose", "pyr (fogo)",
     [("Pirose.", "Correta. Azia ou sensação de queimação retroesternal ascendente é pirose."),
      ("Dispepsia.", "Incorreta. Dispepsia é termo amplo para indigestão/desconforto epigástrico."),
      ("Epigastralgia.", "Incorreta. Epigastralgia é dor focal no epigástrio."),
      ("Regurgitação.", "Incorreta. Regurgitação é a volta passiva de conteúdo alimentar.")]),

    # 28. Regurgitação vs Êmese
    ("O retorno passivo de alimentos do estômago à boca, sem náusea e sem contração da musculatura abdominal, caracteriza:",
     "Gastrointestinal", "Regurgitação", "re- + gurgitare",
     [("Regurgitação.", "Correta. Retorno passivo sem esforço motor nem náusea prévia é regurgitação."),
      ("Êmese.", "Incorreta. Vômito envolve contração ativa do diafragma e prensa abdominal."),
      ("Dispepsia.", "Incorreta. Dispepsia é síndrome de má digestão."),
      ("Sialorreia.", "Incorreta. Sialorreia é hipersecreção salivar.")]),

    # 29. Disquesia vs Tenesmo
    ("A sensação incômoda de evacuação incompleta com espasmo e esforço contínuo doloroso no reto recebe o nome de:",
     "Gastrointestinal & Procto", "Tenesmo", "teinesmos",
     [("Tenesmo retal.", "Correta. Desejo doloroso e espasmódico de evacuar com sensação de reto não esvaziado."),
      ("Disquesia.", "Incorreta. Disquesia é o ato de defecação difícil/dolorosa."),
      ("Fecaloma.", "Incorreta. Fecaloma é a massa fecal endurecida impactada."),
      ("Meteorismo.", "Incorreta. Meteorismo é excesso de gás intra-abdominal.")]),

    # 30. Fecaloma
    ("A massa endurecida de fezes petrificadas que fica retida na ampola retal gerando obstrução mecânica denomina-se:",
     "Gastrointestinal & Procto", "Fecaloma", "faecalis + -oma",
     [("Fecaloma.", "Correta. Concreção fecal volumosa e petrificada no reto."),
      ("Tenesmo.", "Incorreta. Tenesmo é sintoma subjetivo de urgência espasmódica."),
      ("Disquesia.", "Incorreta. Dificuldade evacuatória geral."),
      ("Esteatorreia.", "Incorreta. Presença de gordura fecal.")]),

    # 31. Mácula vs Pápula
    ("Na semiologia dermatológica, a lesão elementar plana caracterizada exclusivamente por alteração de cor é:",
     "Tegumentar & Dermatologia", "Mácula", "macula (mancha)",
     [("Mácula.", "Correta. Lesão plana sem relevo ou espessamento palpável."),
      ("Pápula.", "Incorreta. Pápula é sólida e elevada (< 1 cm)."),
      ("Pústula.", "Incorreta. Pústula contém exsudato purulento."),
      ("Vesícula.", "Incorreta. Vesícula contém líquido seroso.")]),

    # 32. Pápula vs Vesícula
    ("Uma lesão elementar da pele circunscrita, sólida e elevada medindo menos de 1 cm classifica-se como:",
     "Tegumentar & Dermatologia", "Pápula", "papula",
     [("Pápula.", "Correta. Lesão elevada sólida superficial menor que 1 cm."),
      ("Mácula.", "Incorreta. Mácula é plana, sem elevação."),
      ("Vesícula.", "Incorreta. Vesícula é de conteúdo líquido seroso."),
      ("Pústula.", "Incorreta. Pústula possui conteúdo purulento.")]),

    # 33. Vesícula vs Bolha
    ("Lesão cutânea elevada de conteúdo líquido claro e seroso com diâmetro inferior a 1 cm denomina-se:",
     "Tegumentar & Dermatologia", "Vesícula", "vesicula",
     [("Vesícula.", "Correta. Bolhinha de líquido claro < 1 cm."),
      ("Bolha ou flictena.", "Incorreta. Bolha tem diâmetro superior a 1 cm."),
      ("Pústula.", "Incorreta. Pústula contém líquido purulento."),
      ("Pápula.", "Incorreta. Pápula é uma lesão sólida.")]),

    # 34. Pústula
    ("A lesão dermatológica elementar circunscrita e elevada cujo conteúdo é purulento (pus) medindo < 1 cm é uma:",
     "Tegumentar & Dermatologia", "Pústula", "pustula",
     [("Pústula.", "Correta. Elevação superficial com pus < 1 cm."),
      ("Abscesso.", "Incorreta. Abscesso é coleção purulenta profunda encapsulada."),
      ("Vesícula.", "Incorreta. Conteúdo de vesícula é seroso transparente."),
      ("Mácula.", "Incorreta. Mácula é lesão plana sem conteúdo líquido.")]),

    # 35. Abscesso
    ("A coleção delimitada de pus que se forma em tecidos profundos gerando destruição tecidual localizada chama-se:",
     "Tegumentar & Inflamatório", "Abscesso", "abs- + cedere",
     [("Abscesso.", "Correta. Coleção purulenta tecidual delimitada."),
      ("Pústula.", "Incorreta. Pústula é lesão superficial menor que 1 cm."),
      ("Flegmão.", "Incorreta. Flegmão é inflamação purulenta difusa não delimitada."),
      ("Calázio.", "Incorreta. Calázio é granuloma lipogranulomatoso de glândula meibomiana.")]),

    # 36. Calázio vs Hordéolo
    ("O nódulo palpebral indolor e crônico decorrente de obstrução de glândula de Meibômio é tecnicamente o:",
     "Neurologia & Oftalmologia", "Calázio", "chalazion",
     [("Calázio.", "Correta. Granuloma lipídico crônico e indolor da pálpebra."),
      ("Hordéolo (terçol).", "Incorreta. Hordéolo é abscesso agudo, doloroso e avermelhado."),
      ("Ptose palpebral.", "Incorreta. Ptose é a queda motora da pálpebra."),
      ("Lagoftalmo.", "Incorreta. Lagoftalmo é a incapacidade de fechar a pálpebra.")]),

    # 37. Ptose palpebral vs Lagoftalmo
    ("A impossibilidade de fechar completamente as pálpebras, típica da paralisia do nervo facial, recebe o nome de:",
     "Neurologia & Oftalmologia", "Lagoftalmo", "lagos + ophthalmos",
     [("Lagoftalmo.", "Correta. Olho que permanece aberto por déficit do músculo orbicular."),
      ("Ptose palpebral.", "Incorreta. Ptose é a queda da pálpebra (olho que não abre direito)."),
      ("Ablepsia.", "Incorreta. Ablepsia é cegueira / perda da acuidade visual."),
      ("Madarose.", "Incorreta. Madarose é perda dos pelos dos cílios e sobrancelhas.")]),

    # 38. Ptose palpebral
    ("A queda involuntária da pálpebra superior decorrente de disfunção do músculo levantador da pálpebra denomina-se:",
     "Neurologia & Oftalmologia", "Ptose palpebral", "ptosis",
     [("Ptose palpebral.", "Correta. Queda da pálpebra superior."),
      ("Lagoftalmo.", "Incorreta. Incapacidade de fechar o olho."),
      ("Madarose.", "Incorreta. Queda dos cílios."),
      ("Ablepsia.", "Incorreta. Perda da visão.")]),

    # 39. Ablepsia vs Amaurose
    ("O termo semiológico «Ablepsia» é sinônimo técnico de:",
     "Neurologia & Oftalmologia", "Ablepsia", "a- + bleps- + -ia",
     [("Cegueira ou perda da visão.", "Correta. Ablepsia define cegueira total ou parcial."),
      ("Visão dupla.", "Incorreta. Visão dupla é diplopia."),
      ("Fotofobia.", "Incorreta. Aversão à luz é fotofobia."),
      ("Queda da pálpebra.", "Incorreta. Queda palpebral é ptose palpebral.")]),

    # 40. Madarose vs Alopecia
    ("A perda ou queda localizada exclusivamente dos fios dos cílios e das sobrancelhas é clinicamente denominada:",
     "Tegumentar & Oftalmologia", "Madarose", "madaros",
     [("Madarose.", "Correta. Perda seletiva dos pelos dos cílios e sobrancelhas."),
      ("Alopecia.", "Incorreta. Alopecia é perda generalizada de cabelos/pelos corporais."),
      ("Hirsutismo.", "Incorreta. Hirsutismo é excesso de pelos."),
      ("Ptose palpebral.", "Incorreta. Ptose é queda da pálpebra.")]),

    # 41. Midríase vs Miose
    ("Pupilas com diâmetro superior a 5 mm em repouso recebem a designação semiológica de:",
     "Neurologia & Oftalmologia", "Midríase", "mydriasis",
     [("Midríase.", "Correta. Dilatação pupilar aumentada."),
      ("Miose.", "Incorreta. Miose é diâmetro pupilar contraído (< 2 mm)."),
      ("Anisocoria.", "Incorreta. Anisocoria é assimetria entre as pupilas."),
      ("Isocoria.", "Incorreta. Isocoria é simetria pupilar normal.")]),

    # 42. Miose
    ("A constrição intensa do diâmetro pupilar para valores inferiores a 2 mm é definida como:",
     "Neurologia & Oftalmologia", "Miose", "myein",
     [("Miose.", "Correta. Contração excessiva da pupila."),
      ("Midríase.", "Incorreta. Dilatação pupilar > 4-5 mm."),
      ("Escotoma.", "Incorreta. Ponto cego no campo visual."),
      ("Diplopia.", "Incorreta. Visão dupla.")]),

    # 43. Anisocoria vs Isocoria
    ("Ao examinar paciente com trauma cranioencefálico e notar pupila direita de 6 mm e esquerda de 2 mm, registra-se:",
     "Neurologia & Oftalmologia", "Anisocoria", "an- + isos + kore",
     [("Anisocoria.", "Correta. Desigualdade no diâmetro das pupilas."),
      ("Isocoria.", "Incorreta. Isocoria é igualdade entre as pupilas."),
      ("Miose bilateral.", "Incorreta. Apenas a esquerda está miótica."),
      ("Midríase bilateral.", "Incorreta. Apenas a direita está midriática.")]),

    # 44. Isocoria
    ("Quando ambas as pupilas apresentam o mesmo diâmetro e reagem igualmente ao estímulo luminoso, o achado é:",
     "Neurologia & Oftalmologia", "Isocoria", "isos + kore",
     [("Isocoria.", "Correta. Pupilas simétricas de diâmetros idênticos."),
      ("Anisocoria.", "Incorreta. Pupilas de tamanhos desiguais."),
      ("Nistagmo.", "Incorreta. Movimentos oscilatórios rápidos."),
      ("Ablepsia.", "Incorreta. Ausência de visão.")]),

    # 45. Diplopia
    ("A queixa do paciente que relata enxergar duas imagens de um único objeto estático é definida como:",
     "Neurologia & Oftalmologia", "Diplopia", "diploos + ops",
     [("Diplopia.", "Correta. Percepção visual dupla de um mesmo objeto."),
      ("Escotoma.", "Incorreta. Ponto cego no campo de visão."),
      ("Fotofobia.", "Incorreta. Aversão dolorosa à luz."),
      ("Amaurose.", "Incorreta. Perda visual total.")]),

    # 46. Escotoma
    ("A presença de uma mancha escura focal no campo de visão, preservando o restante da visão periférica, traduz:",
     "Neurologia & Oftalmologia", "Escotoma", "skotos + -oma",
     [("Escotoma.", "Correta. Área circunscrita de déficit visual focal."),
      ("Ablepsia.", "Incorreta. Perda visual completa do olho."),
      ("Lagoftalmo.", "Incorreta. Incapacidade de fechar o olho."),
      ("Diplopia.", "Incorreta. Visão dupla.")]),

    # 47. Nistagmo
    ("Movimentos involuntários rápidos e rítmicos dos globos oculares em sentido horizontal ou vertical denominam-se:",
     "Neurologia & Oftalmologia", "Nistagmo", "nystazein",
     [("Nistagmo.", "Correta. Oscilações rítmicas e involuntárias dos olhos."),
      ("Ataxia.", "Incorreta. Ataxia é incoordenação motora geral."),
      ("Vertigem.", "Incorreta. Vertigem é ilusão rotatória de movimento."),
      ("Diplopia.", "Incorreta. Diplopia é visão dupla.")]),

    # 48. Vertigem vs Tontura
    ("A queixa do paciente que relata que «o quarto está rodando ao seu redor» ao deitar na cama é tecnicamente:",
     "Neurologia & Otorrino", "Vertigem", "vertere (girar)",
     [("Vertigem objetiva.", "Correta. Sensação ilusória rotatória em que o ambiente gira ao redor do paciente."),
      ("Lipotimia.", "Incorreta. Lipotimia é sensação de quase desmaio com fraqueza."),
      ("Síncope.", "Incorreta. Síncope exige perda transitória da consciência."),
      ("Astenia.", "Incorreta. Astenia é fraqueza corporal generalizada.")]),

    # 49. Lipotimia vs Síncope
    ("Diferencia-se a «Lipotimia» da «Síncope» porque na lipotimia:",
     "Neurologia & Cardiovascular", "Lipotimia", "leipein + thymos",
     [("Não há perda real da consciência, apenas sensação de desmaio iminente.", "Correta. Lipotimia é o pré-desmaio sem apagamento cerebral."),
      ("Ocorre perda completa e prolongada da consciência com coma.", "Incorreta. Isto caracterizaria coma ou síncope complicada."),
      ("Há parada cardiorrespiratória irreversível.", "Incorreta. Não há parada cardíaca."),
      ("Ocorre déficit motor focal definitivo.", "Incorreta. Déficit motor persistente sugere AVC.")]),

    # 50. Síncope
    ("A perda súbita, breve e transitória da consciência com queda da postura corporal e recuperação espontânea e rápida é:",
     "Neurologia & Cardiovascular", "Síncope", "synkope",
     [("Síncope.", "Correta. Desmaio com perda rápida de consciência por hipoperfusão cerebral temporária."),
      ("Lipotimia.", "Incorreta. Na lipotimia o indivíduo não perde a consciência."),
      ("Coma.", "Incorreta. Coma é estado prolongado de inconsciência não recuperável prontamente."),
      ("Letargia.", "Incorreta. Letargia é sonolência profunda responsiva a estímulos.")]),

    # 51. Afasia vs Disartria
    ("Paciente com AVC que compreende ordens mas apresenta fraqueza na língua e fala pastosa e arrastada tem:",
     "Neurologia & Fono", "Disartria", "dys- + arthron",
     [("Disartria.", "Correta. Dificuldade motora e mecânica de articulação das palavras."),
      ("Afasia de Broca.", "Incorreta. Afasia envolve disfunção cortical de linguagem e gramática."),
      ("Afasia de Wernicke.", "Incorreta. Afasia de Wernicke acomete a compreensão."),
      ("Disfagia.", "Incorreta. Disfagia é alteração da deglutição.")]),

    # 52. Afasia
    ("A perda ou prejuízo da capacidade de elaborar ou compreender a linguagem verbal devido a lesão cerebral é:",
     "Neurologia & Cognição", "Afasia", "a- + phasis",
     [("Afasia.", "Correta. Distúrbio neurológico primário da função linguística cortical."),
      ("Disartria.", "Incorreta. Disartria é alteração estritamente muscular/motora fonoarticulatória."),
      ("Disfonia.", "Incorreta. Disfonia é rouquidão por alteração nas cordas vocais."),
      ("Abulia.", "Incorreta. Abulia é diminuição patológica da vontade.")]),

    # 53. Hemiplegia vs Paraplegia
    ("A paralisia motora completa que acomete o hemicorpo direito (membro superior e membro inferior do mesmo lado) é:",
     "Neurologia & Motor", "Hemiplegia", "hemi- + plege",
     [("Hemiplegia.", "Correta. Paralisia de um lado longitudinal do corpo."),
      ("Paraplegia.", "Incorreta. Paraplegia acomete os dois membros inferiores exclusivamente."),
      ("Tetraplegia.", "Incorreta. Tetraplegia acomete os quatro membros."),
      ("Monoplegia.", "Incorreta. Monoplegia acomete apenas um membro isolado.")]),

    # 54. Paraplegia
    ("A paralisia motora que abole os movimentos voluntários de ambos os membros inferiores por lesão medular é a:",
     "Neurologia & Motor", "Paraplegia", "para- + plege",
     [("Paraplegia.", "Correta. Paralisia bilateral de membros inferiores."),
      ("Hemiplegia.", "Incorreta. Paralisia unilateral hemicorporal."),
      ("Tetraplegia.", "Incorreta. Paralisia dos quatro membros."),
      ("Paresia facial.", "Incorreta. Fraqueza da mímica facial.")]),

    # 55. Parestesia vs Hipoestesia
    ("A queixa de sensação espontânea de «alfinetadas», formigamento ou dormência sem qualquer estímulo tátil define:",
     "Neurologia & Sensibilidade", "Parestesia", "para- + aisthesis",
     [("Parestesia.", "Correta. Sensação tátil espontânea anormal (formigamento/agulhadas)."),
      ("Hipoestesia.", "Incorreta. Hipoestesia é a diminuição da sensibilidade ao toque aplicado."),
      ("Anestesia.", "Incorreta. Anestesia é perda total da sensibilidade."),
      ("Hiperestesia.", "Incorreta. Hiperestesia é exagero doloroso da resposta sensorial.")]),

    # 56. Hipoestesia
    ("A diminuição da sensibilidade superficial térmica, dolorosa ou tátil identificada ao exame neurológico denomina-se:",
     "Neurologia & Sensibilidade", "Hipoestesia", "hypo- + aisthesis",
     [("Hipoestesia.", "Correta. Sensibilidade cutânea diminuída."),
      ("Parestesia.", "Incorreta. Parestesia é formigamento espontâneo."),
      ("Astenia.", "Incorreta. Astenia é fraqueza muscular geral."),
      ("Ataxia.", "Incorreta. Ataxia é perda da coordenação motora.")]),

    # 57. Ataxia
    ("A incoordenação motora durante a marcha e perda do equilíbrio na ausência de fraqueza muscular primária traduz:",
     "Neurologia & Motor", "Ataxia", "a- + taxis",
     [("Ataxia.", "Correta. Incoordenação cerebelar ou proprioceptiva dos movimentos voluntários."),
      ("Apraxia.", "Incorreta. Apraxia é incapacidade de executar atos motores aprendidos previamente."),
      ("Claudicação.", "Incorreta. Claudicação é mancar por dor isquêmica."),
      ("Hemiplegia.", "Incorreta. Hemiplegia é paralisia unilateral.")]),

    # 58. Edema vs Anasarca vs Ascite
    ("O acúmulo de líquido livre patológico restrito ao espaço peritoneal do abdome é especificamente denominado:",
     "Gastrointestinal & Abdominal", "Ascite", "askites",
     [("Ascite.", "Correta. Líquido livre na cavidade peritoneal abdominal."),
      ("Anasarca.", "Incorreta. Anasarca é edema generalizado corporal."),
      ("Derrame pleural.", "Incorreta. Derrame pleural é líquido na cavidade torácica."),
      ("Cacifo.", "Incorreta. Cacifo é o sinal semiológico de depressão dérmica.")]),

    # 59. Anasarca
    ("A condição clínica de edema volumoso e disseminado por todo o corpo associado a derrames cavitários múltiplos é a:",
     "Geral & Cardiovascular", "Anasarca", "ana- + sarx",
     [("Anasarca.", "Correta. Edema generalizado de subcutâneo e serosas."),
      ("Ascite isolada.", "Incorreta. Ascite localiza-se apenas no peritônio."),
      ("Caquexia.", "Incorreta. Caquexia é perda profunda de peso e massa magra."),
      ("Elefantíase.", "Incorreta. Elefantíase é linfedema crônico grave obstrutivo.")]),

    # 60. Caquexia vs Marasmo
    ("O emagrecimento severo com atrofia muscular e consumpção generalizada decorrente de neoplasia avançada expressa:",
     "Geral & Metabólico", "Caquexia", "kakos + hexis",
     [("Caquexia.", "Correta. Síndrome consuntiva metabólica associada a doenças crônicas graves."),
      ("Bulimia.", "Incorreta. Bulimia é compulsão alimentar com purgação."),
      ("Astenia isolada.", "Incorreta. Astenia é sintoma de cansaço sem necessariamente consumpção."),
      ("Obesidade sarcopênica.", "Incorreta. Na caquexia há perda profunda de gordura e peso.")])
]

for i, (stem_raw, sys_raw, term_raw, etym_raw, opt_tuples) in enumerate(vital_topics):
    num = 440 + i + 1
    qid = f"Q{num:03d}"
    correct_letter = letters[i % 4]
    
    # Reordenar opções para bater com correct_letter
    correct_tuple = opt_tuples[0]
    distractor_tuples = opt_tuples[1:]
    
    opts_map = {}
    dist_idx = 0
    for l in letters:
        if l == correct_letter:
            opts_map[l] = {
                "letter": l,
                "text": correct_tuple[0],
                "explanation": f"Gabarito correto. {correct_tuple[1]}"
            }
        else:
            d = distractor_tuples[dist_idx]
            dist_idx += 1
            opts_map[l] = {
                "letter": l,
                "text": d[0],
                "explanation": f"Incorreta. {d[1]}"
            }
            
    q = {
        "id": qid,
        "number": num,
        "termId": terms_by_name.get(term_raw.lower(), {'id': 999})['id'],
        "term": term_raw,
        "system": sys_raw,
        "angle": "Semiologia Integrada",
        "difficulty": "Essencial",
        "stem": stem_raw,
        "options": [opts_map['A'], opts_map['B'], opts_map['C'], opts_map['D']],
        "correctLetter": correct_letter,
        "etymologyNote": etym_raw,
        "pearl": f"Pérola Estratégia MED: Questão padrão de prova prática! Lembre-se sempre de correlacionar o valor numérico ou a manifestação física com o termo correto."
    }
    add_q(q)

print(f"Total de questões geradas: {len(questions)}")
assert len(questions) == 500, f"Esperado 500 questões, obtido {len(questions)}"

with open('/home/antigravity/medterm-estrategia/src/data/questionsBank.js', 'w', encoding='utf-8') as f:
    f.write('export const QUESTIONS_BANK = ' + json.dumps(questions, ensure_ascii=False, indent=2) + ';\n')

print("Arquivo questionsBank.js gerado com 500 questões únicas e rigorosamente comentadas!")
