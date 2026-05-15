from flask import jsonify, render_template, request


def register_routes(app):
    @app.route("/")
    def index():
        import app as _top_app

        return render_template("index.html", demo_mode=_top_app.DEMO_MODE)

    @app.route("/api/history")
    def api_history():
        import app as _top_app

        return jsonify(_top_app.load_history())

    @app.route("/api/chat", methods=["POST"])
    def api_chat():
        import app as _top_app

        data = request.get_json() or {}
        message = (data.get("message") or "").strip()
        if not message:
            return jsonify({"error": "empty message"}), 400

        _top_app.save_message("user", message)

        if _top_app.DEMO_MODE:
            reply = _top_app.fake_reply(message)
            _top_app.save_message("assistant", reply)
            return jsonify({"reply": reply, "demo": True})

        # Build a concise conversation context (last 10 messages)

        print(f"Received message: {message}")
        history = _top_app.load_history()
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        for m in history[-10:]:
            messages.append({"role": m["role"], "content": m["content"]})

        try:
            resp = _top_app.get_client().chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
            )
            reply = resp.choices[0].message.content.strip()
        except Exception:
            reply = _top_app.fake_reply(message)
            _top_app.save_message("assistant", reply)
            return jsonify({"reply": reply, "demo": True})

        _top_app.save_message("assistant", reply)
        return jsonify({"reply": reply})
