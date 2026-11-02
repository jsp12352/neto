from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from pathlib import Path
import json
import os
from functools import wraps
from security import apply_security_headers

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("NETO_SECRET", "change-this-secret-before-deploying"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,
)
app.secret_key = app.config["SECRET_KEY"]
DATA_FILE = Path("data.json")
OWNER_USERNAME = os.environ.get("NETO_OWNER_USERNAME", "killme")
OWNER_PASSWORD = os.environ.get("NETO_OWNER_PASSWORD", "999988887777")
STAFF_USERNAME = os.environ.get("NETO_STAFF_USERNAME", "staffneto")
STAFF_PASSWORD = os.environ.get("NETO_STAFF_PASSWORD", "03030202")

DEFAULT_DATA = {
    "services": [
        {"icon": "⌘", "name": "Sites web", "description": "Des sites modernes, rapides et adaptés à tes besoins.", "details": "Site vitrine, portfolio, landing page et e-commerce.", "image": "/static/images/661194-shinystar.png"},
        {"icon": "◈", "name": "Bots Discord", "description": "Des bots personnalisés pour automatiser et gérer ton serveur.", "details": "Commandes, tickets, modération et systèmes sur mesure.", "image": "/static/images/829331-discord-staff.png"},
        {"icon": "⌁", "name": "Développement sur mesure", "description": "Des outils conçus autour de ton idée.", "details": "Applications, tableaux de bord et intégrations.", "image": "/static/images/671606-codeexpert.png"},
        {"icon": "↗", "name": "Automatisation", "description": "Moins de tâches répétitives, plus de temps pour tes projets.", "details": "Automatisation de tâches et connexions entre outils.", "image": "/static/images/9928-black-fire.gif"},
        {"icon": "✳", "name": "Conseil & accompagnement", "description": "Un coup de main pour transformer une idée en projet concret.", "details": "Organisation, choix techniques et accompagnement.", "image": "/static/images/52143-trainee.png"},
        {"icon": "⌘", "name": "Aide au lancement", "description": "Un cadre clair pour démarrer ton projet numérique.", "details": "Conseils, plan d'action et mise en ligne.", "image": "/static/images/173461-staff.png"}
    ],
    "projects": [],
    "plans": [
        {"name": "Créer un site web", "price": "À partir de 15€", "description": "Nous créons un site web de A à Z, simple, propre et prêt à être lancé.", "features": ["Page simple", "Design responsive", "Formulaire de contact"]},
        {"name": "Créer un bot Discord", "price": "À partir de 10€", "description": "Nous créons un bot Discord complet, utile et prêt à fonctionner.", "features": ["Commandes personnalisées", "Modération", "Accompagnement"]},
        {"name": "Développement sur mesure", "price": "À partir de 20€", "description": "Tu as une idée ? On la transforme en outil concret, site ou bot.", "features": ["Solutions sur mesure", "Automatisations", "Intégrations"]},
        {"name": "Conseil & accompagnement", "price": "À partir de 8€", "description": "Des conseils utiles et un accompagnement pour avancer dans ton projet.", "features": ["Aide dans tes projets", "Conseils techniques", "Suivi personnalisé"]},
        {"name": "Automatisation", "price": "À partir de 5€", "description": "On automatise les tâches répétitives pour gagner du temps.", "features": ["Tâches répétitives", "Connexion entre outils", "Scripts personnalisés"]},
        {"name": "Aide au lancement", "price": "À partir de 2€", "description": "On t’aide à lancer et configurer tes scripts et outils.", "features": ["Lancement de scripts", "Configuration", "Support"]}
    ],
    "faqs": [
        {"question": "Combien de temps faut-il pour créer un site ?", "answer": "Le délai dépend du projet. Un site simple peut être livré en 7 à 15 jours, alors qu'un projet plus complet demande plus de travail."},
        {"question": "Pouvez-vous aussi créer un bot Discord ?", "answer": "Oui. Nous concevons des bots Discord pour la modération, le support client, les tickets, l'automatisation et les commandes personnalisées."},
        {"question": "Travaillez-vous sur mesure ?", "answer": "Oui. Chaque projet est étudié selon vos besoins, vos objectifs et votre budget pour proposer une solution adaptée."},
        {"question": "Quels services sont inclus après la livraison ?", "answer": "Nous pouvons vous accompagner sur la mise en ligne, la configuration, la maintenance et les améliorations continues selon votre besoin."}
    ],
    "testimonials": [
        {"name": "Sophie M.", "role": "Cliente - boutique e-commerce", "quote": "NETO a su transformer notre idée en un site propre, rapide et très professionnel."},
        {"name": "Yanis R.", "role": "Community manager", "quote": "Le bot Discord que nous avons reçu a simplifié la gestion de la communauté et réduit le temps de modération."},
        {"name": "Amélie D.", "role": "Auto-entrepreneure", "quote": "Le service était clair, rapide et très orienté résultat. On a vite compris ce qu'on voulait."}
    ],
    "settings": {
        "brand": "NETO",
        "hero_tag": "Votre partenaire numérique",
        "hero_title": "Transformez vos idées en projets concrets.",
        "hero_subtitle": "NETO vous accompagne dans la création de sites web, de bots Discord et d'outils sur mesure pour faire avancer vos projets.",
        "cta_primary": "Démarrer mon projet",
        "cta_secondary": "Voir nos réalisations",
        "footer_text": "Vos idées. Notre expertise.",
        "maintenance_mode": False,
        "contact_enabled": True,
        "show_prices": True,
        "theme_color": "#7044f5",
        "announcement_enabled": False,
        "announcement_title": "NETO",
        "announcement_text": "Bienvenue chez NETO — on crée des projets qui font la différence."
    },
    "messages": [],
    "leads": []
}

def load_data():
    if not DATA_FILE.exists():
        save_data(DEFAULT_DATA)
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return json.loads(json.dumps(DEFAULT_DATA))

    merged = json.loads(json.dumps(DEFAULT_DATA))
    for key, value in data.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key].update(value)
        else:
            merged[key] = value
    if "settings" not in merged or not isinstance(merged["settings"], dict):
        merged["settings"] = json.loads(json.dumps(DEFAULT_DATA["settings"]))
    return merged

def save_data(data):
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def staff_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("staff"):
            return redirect(url_for("staff_login"))
        return fn(*args, **kwargs)
    return wrapper


def owner_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.context_processor
def inject_site_data():
    return {"site_data": load_data()}

@app.after_request
def add_security_headers(response):
    return apply_security_headers(response)

@app.before_request
def enforce_site_security():
    public_endpoints = {"static", "home", "contact", "project_detail", "login", "staff_login", "logout", "staff_logout"}
    if request.endpoint in public_endpoints:
        return None
    if session.get("admin") or session.get("staff"):
        return None
    data = load_data()
    settings = data.get("settings", {})
    if settings.get("maintenance_mode"):
        return render_template("maintenance.html"), 503
    return None

@app.route("/")
def home():
    data = load_data()
    return render_template("index.html", data=data)

@app.route("/projet/<int:project_id>")
def project_detail(project_id):
    projects = load_data()["projects"]
    if project_id < 0 or project_id >= len(projects):
        abort(404)
    return render_template("project.html", project=projects[project_id])

@app.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    subject = request.form.get("subject", "").strip()
    message = request.form.get("message", "").strip()
    if not name or not email or not message:
        flash("Remplis ton nom, ton e-mail et ton message.", "error")
        return redirect(url_for("home") + "#contact")
    data = load_data()
    lead = {"name": name[:100], "email": email[:200], "subject": subject[:150], "message": message[:3000], "type": "contact"}
    data.setdefault("messages", []).append(lead)
    data.setdefault("leads", []).append(lead)
    save_data(data)
    flash("Message enregistré. Configure un service e-mail si tu veux recevoir une notification.", "success")
    return redirect(url_for("home") + "#contact")

@app.route("/admin/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == STAFF_USERNAME and password == STAFF_PASSWORD:
            session.clear()
            session["staff"] = True
            session["staff_user"] = username
            return redirect(url_for("staff_panel"))

        if username == OWNER_USERNAME and password == OWNER_PASSWORD:
            session.clear()
            session["admin"] = True
            session["owner_user"] = username
            return redirect(url_for("admin"))

        flash("Identifiant ou mot de passe incorrect.", "error")
    return render_template("login.html")

@app.route("/admin/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/staff/logout")
def staff_logout():
    session.pop("staff", None)
    session.pop("staff_user", None)
    return redirect(url_for("home"))

@app.route("/staff/login", methods=["GET", "POST"])
def staff_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username == STAFF_USERNAME and password == STAFF_PASSWORD:
            session["staff"] = True
            session["staff_user"] = username
            return redirect(url_for("staff_panel"))
        flash("Identifiants staff incorrects.", "error")
    return render_template("staff_login.html")

@app.route("/staff")
@staff_required
def staff_panel():
    return render_template("staff.html", data=load_data())

@app.route("/staff/settings", methods=["POST"])
@owner_required
def staff_update_settings():
    data = load_data()
    settings = data.setdefault("settings", {})
    settings["brand"] = request.form.get("brand", settings.get("brand", "NETO")).strip()[:40] or "NETO"
    settings["hero_tag"] = request.form.get("hero_tag", settings.get("hero_tag", "Votre partenaire numérique")).strip()[:80]
    settings["hero_title"] = request.form.get("hero_title", settings.get("hero_title", "Transformez vos idées en projets concrets.")).strip()[:120]
    settings["hero_subtitle"] = request.form.get("hero_subtitle", settings.get("hero_subtitle", "")).strip()[:250]
    settings["cta_primary"] = request.form.get("cta_primary", settings.get("cta_primary", "Démarrer mon projet")).strip()[:40]
    settings["cta_secondary"] = request.form.get("cta_secondary", settings.get("cta_secondary", "Voir nos réalisations")).strip()[:40]
    settings["footer_text"] = request.form.get("footer_text", settings.get("footer_text", "Vos idées. Notre expertise.")).strip()[:80]
    settings["theme_color"] = request.form.get("theme_color", settings.get("theme_color", "#7044f5")).strip()[:20]
    settings["maintenance_mode"] = request.form.get("maintenance_mode") == "on"
    settings["contact_enabled"] = request.form.get("contact_enabled") == "on"
    settings["show_prices"] = request.form.get("show_prices") == "on"
    save_data(data)
    flash("Paramètres du site enregistrés.", "success")
    return redirect(url_for("staff_panel"))

@app.route("/staff/service/add", methods=["POST"])
@owner_required
def staff_add_service():
    data = load_data()
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    image = request.form.get("image", "").strip()
    if not name or not description:
        flash("Nom et description obligatoires.", "error")
        return redirect(url_for("admin"))
    data["services"].append({
        "name": name[:80],
        "description": description[:180],
        "details": request.form.get("details", "").strip()[:200],
        "image": image[:200] or "/static/images/661194-shinystar.png"
    })
    save_data(data)
    flash("Service ajouté.", "success")
    return redirect(url_for("admin"))

@app.route("/staff/service/delete/<int:service_id>", methods=["POST"])
@owner_required
def staff_delete_service(service_id):
    data = load_data()
    if 0 <= service_id < len(data["services"]):
        data["services"].pop(service_id)
        save_data(data)
        flash("Service supprimé.", "success")
    return redirect(url_for("admin"))

@app.route("/staff/plan/add", methods=["POST"])
@owner_required
def staff_add_plan():
    data = load_data()
    name = request.form.get("name", "").strip()
    price = request.form.get("price", "").strip()
    description = request.form.get("description", "").strip()
    if not name or not price:
        flash("Nom et prix obligatoires.", "error")
        return redirect(url_for("admin"))
    data["plans"].append({
        "name": name[:80],
        "price": price[:50],
        "description": description[:200],
        "features": ["Option 1", "Option 2", "Option 3"]
    })
    save_data(data)
    flash("Offre ajoutée.", "success")
    return redirect(url_for("admin"))

@app.route("/staff/plan/delete/<int:plan_id>", methods=["POST"])
@owner_required
def staff_delete_plan(plan_id):
    data = load_data()
    if 0 <= plan_id < len(data["plans"]):
        data["plans"].pop(plan_id)
        save_data(data)
        flash("Offre supprimée.", "success")
    return redirect(url_for("admin"))

@app.route("/staff/project/add", methods=["POST"])
@owner_required
def staff_add_project():
    data = load_data()
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()
    link = request.form.get("link", "").strip()
    if not title or not description:
        flash("Titre et description obligatoires.", "error")
        return redirect(url_for("admin"))
    data["projects"].append({
        "title": title[:120],
        "category": category[:80] or "Projet",
        "description": description[:600],
        "link": link[:500]
    })
    save_data(data)
    flash("Projet ajouté.", "success")
    return redirect(url_for("admin"))

@app.route("/staff/project/delete/<int:project_id>", methods=["POST"])
@owner_required
def staff_delete_project(project_id):
    data = load_data()
    if 0 <= project_id < len(data["projects"]):
        data["projects"].pop(project_id)
        save_data(data)
        flash("Projet supprimé.", "success")
    return redirect(url_for("admin"))

@app.route("/staff/maintenance", methods=["POST"])
@staff_required
def staff_toggle_maintenance():
    data = load_data()
    data.setdefault("settings", {})["maintenance_mode"] = request.form.get("maintenance_mode") == "on"
    save_data(data)
    flash("État maintenance enregistré.", "success")
    return redirect(url_for("staff_panel"))

@app.route("/staff/contact", methods=["POST"])
@staff_required
def staff_toggle_contact():
    data = load_data()
    data.setdefault("settings", {})["contact_enabled"] = request.form.get("contact_enabled") == "on"
    save_data(data)
    flash("Paramètres de contact enregistrés.", "success")
    return redirect(url_for("staff_panel"))

@app.route("/admin/reset", methods=["POST"])
@owner_required
def owner_reset_data():
    save_data(DEFAULT_DATA)
    flash("Le site a été réinitialisé par le propriétaire.", "success")
    return redirect(url_for("admin"))

@app.route("/staff/faq/add", methods=["POST"])
@owner_required
def staff_add_faq():
    data = load_data()
    question = request.form.get("question", "").strip()
    answer = request.form.get("answer", "").strip()
    if not question or not answer:
        flash("Question et réponse obligatoires.", "error")
        return redirect(url_for("admin"))
    data.setdefault("faqs", []).append({"question": question[:160], "answer": answer[:500]})
    save_data(data)
    flash("Question FAQ ajoutée.", "success")
    return redirect(url_for("admin"))

@app.route("/staff/faq/delete/<int:faq_id>", methods=["POST"])
@owner_required
def staff_delete_faq(faq_id):
    data = load_data()
    if 0 <= faq_id < len(data.get("faqs", [])):
        data["faqs"].pop(faq_id)
        save_data(data)
        flash("FAQ supprimée.", "success")
    return redirect(url_for("admin"))

@app.route("/staff/testimonial/add", methods=["POST"])
@owner_required
def staff_add_testimonial():
    data = load_data()
    name = request.form.get("name", "").strip()
    role = request.form.get("role", "").strip()
    quote = request.form.get("quote", "").strip()
    if not name or not quote:
        flash("Nom et témoignage obligatoires.", "error")
        return redirect(url_for("admin"))
    data.setdefault("testimonials", []).append({"name": name[:80], "role": role[:120] or "Client", "quote": quote[:400]})
    save_data(data)
    flash("Témoignage ajouté.", "success")
    return redirect(url_for("admin"))

@app.route("/staff/testimonial/delete/<int:testimonial_id>", methods=["POST"])
@owner_required
def staff_delete_testimonial(testimonial_id):
    data = load_data()
    if 0 <= testimonial_id < len(data.get("testimonials", [])):
        data["testimonials"].pop(testimonial_id)
        save_data(data)
        flash("Témoignage supprimé.", "success")
    return redirect(url_for("admin"))

@app.route("/admin")
@admin_required
def admin():
    return render_template("admin.html", data=load_data())

@app.route("/owner")
@admin_required
def owner_panel():
    return render_template("admin.html", data=load_data())

@app.route("/admin/settings", methods=["POST"])
@admin_required
def owner_update_settings():
    data = load_data()
    settings = data.setdefault("settings", {})
    settings["brand"] = request.form.get("brand", settings.get("brand", "NETO")).strip()[:40] or "NETO"
    settings["hero_tag"] = request.form.get("hero_tag", settings.get("hero_tag", "Votre partenaire numérique")).strip()[:80]
    settings["hero_title"] = request.form.get("hero_title", settings.get("hero_title", "Transformez vos idées en projets concrets.")).strip()[:120]
    settings["hero_subtitle"] = request.form.get("hero_subtitle", settings.get("hero_subtitle", "")).strip()[:250]
    settings["cta_primary"] = request.form.get("cta_primary", settings.get("cta_primary", "Démarrer mon projet")).strip()[:40]
    settings["cta_secondary"] = request.form.get("cta_secondary", settings.get("cta_secondary", "Voir nos réalisations")).strip()[:40]
    settings["footer_text"] = request.form.get("footer_text", settings.get("footer_text", "Vos idées. Notre expertise.")).strip()[:80]
    settings["theme_color"] = request.form.get("theme_color", settings.get("theme_color", "#7044f5")).strip()[:20]
    settings["maintenance_mode"] = request.form.get("maintenance_mode") == "on"
    settings["contact_enabled"] = request.form.get("contact_enabled") == "on"
    settings["show_prices"] = request.form.get("show_prices") == "on"
    settings["announcement_enabled"] = request.form.get("announcement_enabled") == "on"
    settings["announcement_title"] = request.form.get("announcement_title", settings.get("announcement_title", "NETO")).strip()[:30] or "NETO"
    settings["announcement_text"] = request.form.get("announcement_text", settings.get("announcement_text", "Bienvenue chez NETO")).strip()[:180]
    save_data(data)
    flash("Paramètres du site enregistrés.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/service/add", methods=["POST"])
@admin_required
def owner_add_service():
    data = load_data()
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    image = request.form.get("image", "").strip()
    if not name or not description:
        flash("Nom et description obligatoires.", "error")
        return redirect(url_for("admin"))
    data["services"].append({"name": name[:80], "description": description[:180], "details": request.form.get("details", "").strip()[:200], "image": image[:200] or "/static/images/661194-shinystar.png"})
    save_data(data)
    flash("Service ajouté.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/service/delete/<int:service_id>", methods=["POST"])
@admin_required
def owner_delete_service(service_id):
    data = load_data()
    if 0 <= service_id < len(data["services"]):
        data["services"].pop(service_id)
        save_data(data)
        flash("Service supprimé.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/faq/add", methods=["POST"])
@admin_required
def owner_add_faq():
    data = load_data()
    q = request.form.get("question", "").strip()
    a = request.form.get("answer", "").strip()
    if not q or not a:
        flash("Question et réponse obligatoires.", "error")
        return redirect(url_for("admin"))
    data.setdefault("faqs", []).append({"question": q[:160], "answer": a[:500]})
    save_data(data)
    flash("FAQ ajoutée.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/faq/delete/<int:faq_id>", methods=["POST"])
@admin_required
def owner_delete_faq(faq_id):
    data = load_data()
    if 0 <= faq_id < len(data.get("faqs", [])):
        data["faqs"].pop(faq_id)
        save_data(data)
        flash("FAQ supprimée.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/testimonial/add", methods=["POST"])
@admin_required
def owner_add_testimonial():
    data = load_data()
    name = request.form.get("name", "").strip()
    role = request.form.get("role", "").strip()
    quote = request.form.get("quote", "").strip()
    if not name or not quote:
        flash("Nom et témoignage obligatoires.", "error")
        return redirect(url_for("admin"))
    data.setdefault("testimonials", []).append({"name": name[:80], "role": role[:120] or "Client", "quote": quote[:400]})
    save_data(data)
    flash("Témoignage ajouté.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/testimonial/delete/<int:testimonial_id>", methods=["POST"])
@admin_required
def owner_delete_testimonial(testimonial_id):
    data = load_data()
    if 0 <= testimonial_id < len(data.get("testimonials", [])):
        data["testimonials"].pop(testimonial_id)
        save_data(data)
        flash("Témoignage supprimé.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/lead/delete/<int:lead_id>", methods=["POST"])
@admin_required
def owner_delete_lead(lead_id):
    data = load_data()
    if 0 <= lead_id < len(data.get("leads", [])):
        data["leads"].pop(lead_id)
        save_data(data)
        flash("Demande supprimée.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/project", methods=["POST"])
@admin_required
def add_project():
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()
    link = request.form.get("link", "").strip()
    if not title or not description:
        flash("Le titre et la description sont obligatoires.", "error")
        return redirect(url_for("admin"))
    data = load_data()
    data["projects"].append({"title": title[:120], "category": category[:80], "description": description[:1000], "link": link[:500]})
    save_data(data)
    flash("Réalisation ajoutée.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/project/delete/<int:project_id>", methods=["POST"])
@admin_required
def delete_project(project_id):
    data = load_data()
    if 0 <= project_id < len(data["projects"]):
        data["projects"].pop(project_id)
        save_data(data)
        flash("Réalisation supprimée.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/plan", methods=["POST"])
@admin_required
def update_plan():
    data = load_data()
    idx = request.form.get("index", type=int)
    if idx is not None and 0 <= idx < len(data["plans"]):
        data["plans"][idx]["price"] = request.form.get("price", "").strip()[:80]
        save_data(data)
        flash("Tarif mis à jour.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/message/delete/<int:message_id>", methods=["POST"])
@admin_required
def delete_message(message_id):
    data = load_data()
    if 0 <= message_id < len(data["messages"]):
        data["messages"].pop(message_id)
        save_data(data)
    return redirect(url_for("admin"))

@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
