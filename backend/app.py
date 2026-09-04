import logging

from email_service import enviar_email_experiencia
from flask import Flask, jsonify, request
from flask_cors import CORS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

app = Flask(__name__)

# Em produção substitua "*" pelo domínio real do frontend
CORS(app, origins="*")

CAMPOS_OBRIGATORIOS = ["nome", "empresa", "email", "mensagem"]


@app.route("/api/contato", methods=["POST"])
def contato():
    dados = request.get_json(silent=True) or {}

    faltando = [c for c in CAMPOS_OBRIGATORIOS if not str(dados.get(c, "")).strip()]
    if faltando:
        return jsonify({"erro": f"Campos obrigatórios ausentes: {', '.join(faltando)}"}), 400

    try:
        enviar_email_experiencia(dados)
        return jsonify({"ok": True}), 200
    except Exception:
        logging.exception("Falha ao enviar e-mail de contato")
        return jsonify({"erro": "Falha ao enviar. Tente novamente mais tarde."}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
