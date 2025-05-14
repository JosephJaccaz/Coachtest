
import streamlit as st
import openai
from langdetect import detect
import smtplib
from email.mime.text import MIMEText
import io
import matplotlib.pyplot as plt
import numpy as np
import re


st.set_page_config(page_title="Speech Coach IA", page_icon="🎤")

# Logo
st.markdown(
    '''
    <div style='text-align: center; margin-bottom: 30px;'>
        <img src='https://www.thejob.ch/wp-content/themes/corris2014/images/corris_logo.svg' width='200'>
    </div>
    ''',
    unsafe_allow_html=True
)

# 🌍 Sélecteur de langue
langue_choisie = st.selectbox(
    "Choisis ta langue / Wähle deine Sprache / Scegli la tua lingua",
    options=["fr", "de", "it"],
    format_func=lambda x: {"fr": "Français 🇫🇷", "de": "Deutsch 🇩🇪", "it": "Italiano 🇮🇹"}[x]
)

# Textes localisés
textes = {
    "fr": {
        "titre": "🎤 Speech Coach IA",
        "intro": "Bienvenue ! Upload ici un speech pour savoir s’il colle aux standards vus en formation.",
        "upload_label": "📁 Dépose ici ton fichier audio (MP3 ou WAV uniquement)",
        "email_label": "✉️ Adresse e-mail du·de la Dialogueur·euse (pour recevoir le feedback)",
        "info_format": "⚠️ Pour l’instant, seuls les fichiers MP3 et WAV sont pris en charge.",
        "transcription_label": "📝 Transcription générée :"
    },
    "de": {
        "titre": "🎤 Speech Coach IA",
        "intro": "Willkommen! Lade hier deine Sprachaufnahme hoch, um ein Feedback zu erhalten.",
        "upload_label": "📁 Hier deine Audiodatei hochladen (nur MP3 oder WAV)",
        "email_label": "✉️ E-Mail-Adresse des Fundraisers (für den Erhalt des Feedbacks)",
        "info_format": "⚠️ Aktuell werden nur MP3- und WAV-Dateien unterstützt.",
        "transcription_label": "📝 Transkription:"
    },
    "it": {
        "titre": "🎤 Speech Coach IA",
        "intro": "Benvenuto! Carica qui il tuo speech per ricevere un feedback.",
        "upload_label": "📁 Carica il tuo file audio (solo MP3 o WAV)",
        "email_label": "✉️ Indirizzo e-mail del dialogatore (per ricevere il feedback)",
        "info_format": "⚠️ Al momento sono supportati solo file MP3 e WAV.",
        "transcription_label": "📝 Trascrizione generata:"
    }
}
t = textes[langue_choisie]

# Interface
st.title(t["titre"])
st.write(t["intro"])
user_email = st.text_input(t["email_label"], key="email")
audio_file = st.file_uploader(t["upload_label"], type=["mp3", "wav"], key="audio")
st.markdown(t["info_format"])

openai.api_key = st.secrets["openai_key"]

def format_feedback_as_html(feedback_text, langue):
    html = feedback_text
    html = html.replace("✓", "<span style='color:green; font-weight:bold;'>✓</span>")
    html = html.replace("⚠️", "<span style='color:red; font-weight:bold;'>⚠️</span>")
    html = html.replace("Suggestion d'amélioration", "<span style='color:#007BFF; font-weight:bold;'>Suggestion d'amélioration</span>")
    html = html.replace("Verbesserungsvorschlag", "<span style='color:#007BFF; font-weight:bold;'>Verbesserungsvorschlag</span>")
    html = html.replace("Suggerimento di miglioramento", "<span style='color:#007BFF; font-weight:bold;'>Suggerimento di miglioramento</span>")
    html = html.replace("**", "")
    paragraphs = html.split("\n")
    html_body = ""
    for line in paragraphs:
        line = line.strip()
        if not line:
            continue
        if line.startswith(("🟢", "📊", "🔍", "🎯", "🤝", "💢", "🌱", "🚀", "➡️", "📝")):
            html_body += f"<p style='margin:20px 0 6px 0; font-weight:bold;'>{line}</p>"
        elif line.startswith("🎯 **Conclusions et perspectives**"):
            html_body += "<hr style='margin:24px 0; border:none; border-top:2px solid #eee;'>"
            html_body += f"<p style='margin:20px 0 6px 0; font-weight:bold;'>{line}</p>"
        else:
            html_body += f"<p style='margin:4px 0;'>{line}</p>"

    if langue == "de":
        intro = "<p>Hallo 👋<br>Hier ist dein persönliches Feedback zur Analyse deines Sprach-Pitchs :</p><br>"
        signature = "<p style='color:gray;'>--<br>Speech Coach IA 🧠<br>Ein Werkzeug mit Herz – für Fundraiser und Trainer:innen.</p>"
    elif langue == "it":
        intro = "<p>Ciao 👋<br>Ecco il tuo feedback personalizzato sull’analisi del tuo pitch vocale :</p><br>"
        signature = "<p style='color:gray;'>--<br>Speech Coach IA 🧠<br>Uno strumento creato con cura per dialogatori e formatori.</p>"
    else:
        intro = "<p>Bonjour 👋<br>Voici ton feedback personnalisé suite à l’analyse de ton pitch vocal :</p><br>"
        signature = "<p style='color:gray;'>--<br>Speech Coach IA 🧠<br>Un outil conçu avec soin pour les dialogueurs et leurs formateurs.</p>"

    if langue == "fr":
        signature += "<p style='font-size:12px; color:#aaa;'>PS : Ce feedback a été généré avec amour, café ☕ et un soupçon de GPT par Joseph 💻</p>"

    return f"""
    <div style='font-family: Verdana, sans-serif; font-size: 15px; color:#000;'>
        {intro}
        {html_body}
        {signature}
    </div>
    """
def draw_gauge(score):
    import matplotlib.pyplot as plt
    import numpy as np

    fig, ax = plt.subplots(figsize=(3.8, 1.8), subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location('S')  # Met le 0 (score faible) en bas
    ax.set_theta_direction(1)        # Sens antihoraire (rouge à gauche, vert à droite)

    # Zones colorées
    zones = [
        (0, 2, 'darkred'),
        (2, 4, 'red'),
        (4, 6, 'orange'),
        (6, 8, 'yellowgreen'),
        (8, 10, 'green')
    ]

    for start, end, color in zones:
        theta1 = np.interp(start, [0, 10], [0, np.pi])
        theta2 = np.interp(end, [0, 10], [0, np.pi])
        ax.barh(1, width=theta2 - theta1, left=theta1, height=0.35, color=color, edgecolor='white')

    # Aiguille
    angle = np.interp(score, [0, 10], [0, np.pi])
    ax.plot([angle, angle], [0, 1], color='black', lw=2.5)

    # Clean style
    ax.set_axis_off()
    ax.set_ylim(0, 1.05)
    plt.title("Score sur 10", y=1.15, fontsize=12)
    st.pyplot(fig)


def interpret_note(score):
    if score >= 9:
        return "🟢 Adhésion pure – discours exemplaire ✅"
    elif score >= 7:
        return "🟢 Sincère mais perfectible – quelques ajustements possibles"
    elif score >= 5:
        return "🟠 Équilibre fragile – attention à certaines formulations ⚠️"
    elif score >= 3:
        return "🔴 Tonalité douteuse – trop émotionnel ou insistant 🚨"
    else:
        return "⛔ Manipulation forte – à corriger d’urgence ❌"


if user_email and audio_file is not None:
    st.success(f"✅ Fichier reçu : {audio_file.name}")

    with st.spinner("⏳ Transcription en cours avec Whisper..."):
        audio_bytes = audio_file.read()
        audio_io = io.BytesIO(audio_bytes)
        audio_io.name = audio_file.name
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_io,
            response_format="text"
        )

    st.success("✅ Transcription terminée. Analyse en cours...")

    langue_detectee = detect(transcript)
    st.info(f"🗣️ Langue détectée : {langue_detectee.upper()}")

    # Définir le prompt selon la langue choisie
    if langue_choisie == "fr":
        prompt_intro = """Tu es un coach expert en rhétorique, spécialisé dans la formation de dialogueurs pour des ONG.

Tu t'adresses ici directement à un·e dialogueur·euse qui vient d'enregistrer un **speech** d'entraînement. Ton rôle est de lui faire un retour complet, clair et motivant.

Tu dois évaluer à la fois la qualité du contenu, la structure du discours et l’émotion transmise dans la voix.

Tu dois être exigeant, pour que la personne qui t'envoie un speech ait un jugement honnête. Si c'est pourri ou qu'une partie du speech est absente, tu dois le dire et ce n'est pas okay

Ta réponse doit être structurée **exactement** selon ce plan :

---

🟢 **Résumé global**

Commence par un petit résumé général de ton speech (2 à 3 phrases maximum). L’idée est de donner une première impression générale sur le speech.

---

📊 **Note sur 10**

Donne une note sur 10 pour ta performance globale (clarté, structure, émotion, impact). Soit exigeant.
Ex : “7/10 – Tu poses une intention très claire dès le départ, mais la partie ‘problème’ est un peu rapide.”

---

🔍 **Analyse détaillée (par étapes)**

Dans cette partie, analyse objectivement le speech selon les 7 étapes du discours classique d’un·e dialogueur·euse. Tu peux ici revenir à un ton plus neutre (sans tutoiement).

🎯 1. Accroche (qui doit transmettre de la curiosité et ou de la sympathie, il faut éviter les questions fermées avec une durée de temps comme "salut, tu as deux minutes" ou "je m'excuse de te déranger") 
🤝 2. Introduction  (qui doit inspirer de la confiance, il faut qu'on ait l'impression d'un dialogue, avec des questions pour savoir que fait la personne (fictive) dans la vie)
💢 3. Problème  (qui doit transmettre de l'empathie et de l'indignation, il faut expliquer le problème, et que cela n'est pas normal qu'il existe)
🌱 4. Solution  (qui doit transmettre de l'espoir, montrer que ce problème n'est pas insoluble, il faut se remettre à sourire et avoir un ton enjoué)
🚀 5. Succès  (qui doit transmettre de l'envie : montrer que cela est concret et que dans le passé, l'association a eu des succès)
➡️ 6. Transition  (qui doit être une phrase affirmative très simple, qui guide la personne et fait le lien entre le speech rempli d'émotions et le formulaire)
📝 7. Explication du formulaire (simple, structurée et claire, la terminologie doit être centrée sur un formulaire en deux parties : une partie identité, une partie générosité, que le tout semble simple)

Voici la structure à suivre pour chaque étape :

🎯 **[Nom de la partie]**
- **Présence** : ✓ ou ⚠️
- **Émotion perçue**
- **Résumé**
- **Suggestion d'amélioration**

---

🎯 **Conclusions et perspectives**

Reprends ici le tutoiement.

Ton objectif est d’évaluer si le discours repose sur une méthode d’adhésion sincère ou s’il dévie vers des techniques de manipulation émotionnelle, culpabilisation ou pression implicite.

Identifie et signale précisément les éléments suivants :

Tonalité manipulatrice : emploi excessif de peur, de chantage émotionnel, d’exagérations ou de termes anxiogènes.

Culpabilisation du passant : tournures de phrases qui font sentir au passant qu’il serait "mauvais", "indifférent", ou "complice" s’il ne donne pas.

Langage trop insistant ou directif : absence d’espace pour le choix du passant, formules qui imposent plutôt qu’elles n’invitent.

Respect du libre arbitre : absence de validation du droit du passant à dire non.

Équilibre émotionnel : discours basé sur une énergie positive, sincère et informative, sans mise en scène excessive ni pathos appuyé.

Pour chaque élément problématique, cite le passage exact, explique pourquoi c’est problématique et propose une alternative formulée de manière plus éthique.

Termine par un message chaleureux, encourageant mais motivant et honnête. Félicite l’effort fourni, encourage à continuer, et donne quelques conseils utiles pour améliorer tes prochains speechs.

Tu peux conclure de manière simple, pro et humaine.
"""
    elif langue_choisie == "de":
        prompt_intro = """Du bist ein Rhetorik-Coach, spezialisiert auf die Schulung von Fundraisern für NGOs im Direktkontakt.

Du sprichst hier direkt mit einemeiner Dialogerin, der*die einen Trainings-Speech aufgenommen hat. Deine Aufgabe ist es, ein vollständiges, klares und motivierendes Feedback zu geben.

Du sollst sowohl den Inhalt, den Aufbau als auch die emotionale Wirkung des Speeches bewerten.

Du musst anspruchsvoll sein – die Person, die dir einen Speech schickt, verdient ein ehrliches Urteil. Wenn der Speech schlecht ist oder ein Teil fehlt, musst du das sagen – und es ist nicht in Ordnung.

Deine Antwort muss genau nach folgendem Plan aufgebaut sein:

🟢 Gesamteindruck

Beginne mit einem kurzen allgemeinen Eindruck von deinem Speech (max. 2–3 Sätze). Ziel ist es, einen ersten Gesamteindruck zu vermitteln.

📊 Note (Skala 1–10)

Gib eine Note von 1 bis 10 für die Gesamtleistung (Klarheit, Struktur, Emotion, Wirkung). Sei dabei ehrlich und streng.
Beispiel: „7/10 – Du zeigst von Anfang an eine klare Absicht, aber die Problemphase wirkt zu kurz.“

---

🔍 **Detaillierte Analyse (in 7 Schritten)**

In diesem Abschnitt analysierst du den Speech sachlich und neutral, Schritt für Schritt. Der Ton darf hier distanzierter sein (kein „du“). Die sieben Teile sind:

🎯 1. Einstieg  
🤝 2. Vorstellung  
💢 3. Problem  
🌱 4. Lösung  
🚀 5. Erfolg  
➡️ 6. Übergang  
📝 7. Formular-Erklärung

Für jeden Teil bitte in folgendem Format antworten:

🎯 **[Name des Teils]**  
- **Vorhanden**: ✓ oder ⚠️  
- **Wahrgenommene Emotion**  
- **Zusammenfassung**  
- **Verbesserungsvorschlag**

---

🎯 **Fazit und Perspektiven**

Hier kehrst du zurück zum „du“.

Beende dein Feedback mit einer positiven, ermutigenden Nachricht. Erkenne die Fortschritte an, motiviere zur weiteren Übung und gib ggf. 1–2 Tipps für zukünftige Speeches.

Verabschiede dich freundlich und professionell – wie ein wohlwollender Coach.
"""
    elif langue_choisie == "it":
        prompt_intro = """Sei un coach esperto in retorica, specializzato nella formazione dei dialogatori per ONG nel contatto diretto.

Ti stai rivolgendo direttamente a ununa dialogatoretrice che ha appena registrato uno speech di allenamento. Il tuo compito è fornire un feedback completo, chiaro e motivante.

Devi valutare sia la qualità del contenuto, sia la struttura del discorso, sia le emozioni trasmesse dalla voce.

Devi essere esigente – chi ti invia uno speech ha bisogno di un giudizio onesto. Se lo speech è debole o manca una parte, devi dirlo chiaramente – e non va bene così.

La tua risposta deve essere esattamente strutturata secondo questo schema:

🟢 Panoramica generale

Inizia con un breve riassunto generale del tuo speech (massimo 2–3 frasi). L’idea è offrire una prima impressione complessiva.

📊 Voto da 1 a 10

Dai un voto da 1 a 10 alla performance globale (chiarezza, struttura, emozione, impatto). Sii esigente.
Esempio: “7/10 – L’intenzione iniziale è chiara, ma la parte del problema è troppo veloce.”

---

🔍 **Analisi dettagliata (in 7 fasi)**

In questa sezione, analizza lo speech con tono più neutro e oggettivo. Segui le 7 fasi classiche del discorso del dialogatore:

🎯 1. Approccio  
🤝 2. Introduzione  
💢 3. Problema  
🌱 4. Soluzione  
🚀 5. Successo  
➡️ 6. Transizione  
📝 7. Spiegazione del modulo

Per ogni parte usa questa struttura:

🎯 **[Nome della parte]**  
- **Presenza** : ✓ o ⚠️  
- **Emozione percepita**  
- **Riassunto**  
- **Suggerimento di miglioramento**

---

🎯 **Conclusioni e prospettive**

Ora torna a rivolgerti con il "tu".

Chiudi con un messaggio positivo e incoraggiante. Riconosci l’impegno, valorizza i progressi, e invita a continuare ad allenarsi. Se vuoi, aggiungi 1 o 2 consigli utili per i prossimi speech.

Concludi in modo semplice, professionale e umano – come un buon coach.
"""
    else:
        prompt_intro = "Voici un speech à analyser :"

    prompt = f"""{prompt_intro}

\"\"\"{transcript}\"\"\"
"""

    with st.spinner("💬 Génération du feedback pédagogique..."):
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un coach bienveillant et structuré pour des ONG."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        feedback = response.choices[0].message.content

        # Extraire la note (par ex. "7/10")
        match = re.search(r"(\d(?:\.\d)?)/10", feedback)
        note = float(match.group(1)) if match else None

        if "10/10" in feedback:
            st.balloons()
            st.success("🔥 WOUAH ! 10/10 – Tu viens de casser la baraque avec ce speech 🔥")

    # Affichage feedback et baromètre
    if note:
        st.markdown("### 🎯 Baromètre de performance")
        draw_gauge(note)
        st.markdown(f"**{interpret_note(note)}**")

        with st.expander("ℹ️ Que signifie le baromètre ?"):
            st.markdown("""
- ✅ **Adhésion pure (9–10)** : discours très aligné avec les standards.
- 🙂 **Sincère mais perfectible (7–8)** : bon fond, à peaufiner.
- ⚠️ **Équilibre fragile (5–6)** : vigilance nécessaire.
- 🚨 **Tonalité douteuse (3–4)** : déséquilibre émotionnel.
- ❌ **Manipulation forte (1–2)** : à retravailler en profondeur.
            """)

    st.markdown("---")
    st.markdown(feedback, unsafe_allow_html=True)

    # Envoi par email
    try:
        html_feedback = format_feedback_as_html(feedback, langue_detectee)
        msg = MIMEText(html_feedback, "html", "utf-8")
        msg["Subject"] = "💬 Speech Coach IA : Feedback de ton speech"
        msg["From"] = st.secrets["email_user"]
        msg["To"] = user_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(st.secrets["email_user"], st.secrets["email_password"])
            server.send_message(msg)

        st.success(f"✅ Feedback envoyé automatiquement à {user_email} !")
    except Exception as e:
        st.error(f"❌ Erreur lors de l'envoi : {e}")
