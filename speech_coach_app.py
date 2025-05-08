import streamlit as st
import openai
from langdetect import detect
import smtplib
from email.mime.text import MIMEText

st.set_page_config(page_title="Speech Coach IA", page_icon="🎤")
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

# Affichage de l’interface localisée
st.title(t["titre"])
st.write(t["intro"])
user_email = st.text_input(t["email_label"])
audio_file = st.file_uploader(t["upload_label"], type=["mp3", "wav"])
st.markdown(t["info_format"])

openai.api_key = st.secrets["openai_key"]

user_email = st.text_input("✉️ Adresse e-mail du·de la Dialogueur·euse (pour recevoir le feedback)")
audio_file = st.file_uploader("📁 Dépose ici ton fichier audio (MP3 ou WAV uniquement)", type=["mp3", "wav"])
st.markdown("⚠️ Pour l’instant, seuls les fichiers `.mp3` et `.wav` sont pris en charge. Si tu utilises un enregistreur vocal, exporte en `.mp3`.")


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
