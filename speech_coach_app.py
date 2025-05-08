import streamlit as st
import openai
from langdetect import detect
import smtplib
from email.mime.text import MIMEText

st.set_page_config(page_title="Speech Coach IA", page_icon="🎤")

# Affichage de l’interface localisée

st.markdown(
    "<div style='text-align: center;'><img src='data:image/png;base64,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' width='200'></div>",
    unsafe_allow_html=True
)


# 🌍 Sélecteur de langue manuel en haut de la page
langue_choisie = st.selectbox(
    "Choisis ta langue / Wähle deine Sprache / Scegli la tua lingua",
    options=["fr", "de", "it"],
    format_func=lambda x: {"fr": "Français 🇫🇷", "de": "Deutsch 🇩🇪", "it": "Italiano 🇮🇹"}[x]
)

# 📚 Textes traduits
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

# 🔄 Sélection des textes selon la langue choisie
t = textes[langue_choisie]


st.title(t["titre"])
st.write(t["intro"])
user_email = st.text_input(t["email_label"], key="email")
audio_file = st.file_uploader(t["upload_label"], type=["mp3", "wav"], key="audio")
st.markdown(t["info_format"])


openai.api_key = st.secrets["openai_key"]



def format_feedback_as_html(feedback_text, langue):
    html = feedback_text

    # Mise en couleur ✓ / ⚠️
    html = html.replace("✓", "<span style='color:green; font-weight:bold;'>✓</span>")
    html = html.replace("⚠️", "<span style='color:red; font-weight:bold;'>⚠️</span>")

    # Suggestions d'amélioration en bleu (toutes langues)
    html = html.replace("Suggestion d'amélioration", "<span style='color:#007BFF; font-weight:bold;'>Suggestion d'amélioration</span>")
    html = html.replace("Verbesserungsvorschlag", "<span style='color:#007BFF; font-weight:bold;'>Verbesserungsvorschlag</span>")
    html = html.replace("Suggerimento di miglioramento", "<span style='color:#007BFF; font-weight:bold;'>Suggerimento di miglioramento</span>")

    # Nettoyage des ** (gras Markdown)
    html = html.replace("**", "")

    # Mise en paragraphes avec titres bien visibles
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

    # Intro & signature par langue
    if langue == "de":
        intro = "<p>Hallo 👋<br>Hier ist dein persönliches Feedback zur Analyse deines Sprach-Pitchs :</p><br>"
        signature = "<p style='color:gray;'>--<br>Speech Coach IA 🧠<br>Ein Werkzeug mit Herz – für Fundraiser und Trainer:innen.</p>"
    elif langue == "it":
        intro = "<p>Ciao 👋<br>Ecco il tuo feedback personalizzato sull’analisi del tuo pitch vocale :</p><br>"
        signature = "<p style='color:gray;'>--<br>Speech Coach IA 🧠<br>Uno strumento creato con cura per dialogatori e formatori.</p>"
    else:
        intro = "<p>Bonjour 👋<br>Voici ton feedback personnalisé suite à l’analyse de ton pitch vocal :</p><br>"
        signature = "<p style='color:gray;'>--<br>Speech Coach IA 🧠<br>Un outil conçu avec soin pour les dialogueurs et leurs formateurs.</p>"

    # Easter egg français 😄
    if langue == "fr":
        signature += "<p style='font-size:12px; color:#aaa;'>PS : Ce feedback a été généré avec amour, café ☕ et un soupçon de GPT par Joseph 💻</p>"

    return f"""
    <div style='font-family: Verdana, sans-serif; font-size: 15px; color:#000;'>
        {intro}
        {html_body}
        {signature}
    </div>

    """




if user_email and audio_file is not None:
    st.success(f"✅ Fichier reçu : {audio_file.name}")

    with st.spinner("⏳ Transcription en cours avec Whisper..."):
        import io

        # Lire le fichier audio
        audio_bytes = audio_file.read()
        audio_io = io.BytesIO(audio_bytes)
        audio_io.name = audio_file.name  # Nécessaire pour que l'API détecte le format

        # Transcription via OpenAI (SDK v1.x)
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_io,
            response_format="text"
        )



    st.text_area(t["transcription_label"], transcript, height=300)


    langue_detectee = detect(transcript)
    st.info(f"🗣️ Langue détectée : {langue_detectee.upper()}")

if langue_choisie == "fr":
    prompt_intro = """Tu es un coach expert en rhétorique, spécialisé dans la formation de dialogueurs pour des ONG.

Tu t'adresses ici directement à un·e dialogueur·euse qui vient d'enregistrer un **speech** d'entraînement. Ton rôle est de lui faire un retour complet, clair et motivant.

Tu dois évaluer à la fois la qualité du contenu, la structure du discours et l’émotion transmise dans la voix.

Ta réponse doit être structurée **exactement** selon ce plan :

---

🟢 **Résumé global**

Commence par un petit résumé général de ton speech (2 à 3 phrases maximum), avec bienveillance. L’idée est de donner une première impression générale sur le speech.

---

📊 **Note sur 10**

Donne une note sur 10 pour ta performance globale (clarté, structure, émotion, impact). Sois motivant, pas scolaire.
Ex : “7/10 – Tu poses une intention très claire dès le départ, mais la partie ‘problème’ est un peu rapide.”

---

🔍 **Analyse détaillée (par étapes)**

Dans cette partie, analyse objectivement le speech selon les 7 étapes du discours classique d’un·e dialogueur·euse. Tu peux ici revenir à un ton plus neutre (sans tutoiement).

Voici la structure à suivre pour chaque étape :

🎯 **[Nom de la partie]**
- **Présence** : ✓ ou ⚠️
- **Émotion perçue**
- **Résumé**
- **Suggestion d'amélioration**

---

🎯 **Conclusions et perspectives**

Reprends ici le tutoiement.

Termine par un message chaleureux, encourageant et motivant. Félicite l’effort fourni, encourage à continuer, et donne quelques conseils utiles pour améliorer tes prochains speechs.

Tu peux conclure de manière simple, pro et humaine.
"""

elif langue_choisie == "de":
    prompt_intro = """Du bist ein Rhetorik-Coach, spezialisiert auf die Schulung von Fundraisern für NGOs im Direktkontakt.

Du sprichst hier direkt mit einem neuen Dialoger oder einer neuen Dialogerin, der oder die einen **Speech** zur Übung aufgenommen hat. Deine Aufgabe ist es, ein vollständiges, klares und motivierendes Feedback zu geben.

Du sollst sowohl den Inhalt, den Aufbau als auch die emotionale Wirkung des Speeches bewerten.

Deine Antwort soll **genau** nach folgendem Schema aufgebaut sein:

---

🟢 **Gesamteindruck**

Beginne mit einem kurzen, wohlwollenden Gesamtkommentar zu deinem Speech (2–3 Sätze). Sprich die Person direkt mit „du“ an.

---

📊 **Note (Skala 1–10)**

Gib eine motivierende Note auf einer Skala von 1 bis 10, basierend auf der Gesamtleistung (Klarheit, Struktur, Emotion, Wirkung).  
Beispiel: „7/10 – Du zeigst von Anfang an eine klare Absicht, aber die Problemphase wirkt noch etwas kurz.“

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

Ti rivolgi direttamente a un nuovo dialogatore o dialogatrice che ha appena registrato uno **speech** di allenamento. Il tuo compito è fornire un feedback completo, chiaro e motivante.

Devi valutare la qualità del contenuto, la struttura del discorso e le emozioni trasmesse nella voce.

La tua risposta deve essere **esattamente** strutturata secondo questo schema:

---

🟢 **Panoramica generale**

Inizia con un breve commento generale (2–3 frasi) sul tuo speech. Sii gentile e incoraggiante, e rivolgiti direttamente con il "tu".

---

📊 **Voto da 1 a 10**

Dai un voto da 1 a 10 che rifletta la performance complessiva (chiarezza, struttura, emozione, impatto). Il voto deve essere stimolante, non scolastico.  
Esempio: “7/10 – Hai mostrato una buona intenzione fin dall'inizio, ma la parte del problema è stata un po’ veloce.”

---

🔍 **Analisi dettagliata (in 7 fasi)**

In questa sezione, analizza lo speech con tono più neutro e oggettivo. Segui le 7 fasi classiche del discorso del dialogatore:

🎯 1. Gancio  
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


        if "10/10" in feedback:
            st.balloons()
            st.success("🔥 WOUAH ! 10/10 – Tu viens de casser la baraque avec ce speech 🔥")


    st.markdown(feedback, unsafe_allow_html=True)

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
