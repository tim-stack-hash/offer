"""Password-protected, read-only web dashboard for bot administrators."""

from __future__ import annotations

import hmac
import os
from math import ceil

from flask import Flask, Response, abort, make_response, render_template, request, send_file
from dotenv import load_dotenv

from bot.database import (
	export_user_activity_csv,
	export_user_activity_history_csv,
	export_users_csv,
	initialize_user_database,
)
from bot.database.web_admin import (
	get_web_activity_counts,
	get_web_click_history,
	get_web_dashboard_summary,
	get_web_users,
)

PAGE_SIZE = 50
MAX_PAGE_NUMBER = 10_000
MAX_SEARCH_LENGTH = 100


def _unauthorized_response() -> Response:
	"""Returns a browser HTTP Basic authentication challenge."""
	response = make_response("Требуется авторизация администратора.", 401)
	response.headers["WWW-Authenticate"] = 'Basic realm="Bot Admin", charset="UTF-8"'
	return response


def create_app(
	username: str | None = None,
	password: str | None = None,
) -> Flask:
	"""Creates the read-only dashboard and requires HTTP Basic authentication."""
	admin_username = username if username is not None else os.getenv("WEB_ADMIN_USERNAME", "")
	admin_password = password if password is not None else os.getenv("WEB_ADMIN_PASSWORD", "")
	if not admin_username.strip():
		raise RuntimeError("Set WEB_ADMIN_USERNAME to enable the web admin panel")
	if len(admin_password) < 16:
		raise RuntimeError("WEB_ADMIN_PASSWORD must contain at least 16 characters")

	initialize_user_database()
	app = Flask(__name__, template_folder="templates")

	@app.before_request
	def require_admin_authentication() -> Response | None:
		credentials = request.authorization
		provided_username = credentials.username if credentials and credentials.username else ""
		provided_password = credentials.password if credentials and credentials.password else ""
		username_matches = hmac.compare_digest(
			provided_username.encode("utf-8"),
			admin_username.encode("utf-8"),
		)
		password_matches = hmac.compare_digest(
			provided_password.encode("utf-8"),
			admin_password.encode("utf-8"),
		)
		if not (username_matches and password_matches):
			return _unauthorized_response()
		return None

	@app.after_request
	def set_security_headers(response: Response) -> Response:
		response.headers["Cache-Control"] = "no-store"
		response.headers["X-Content-Type-Options"] = "nosniff"
		response.headers["Referrer-Policy"] = "no-referrer"
		response.headers["X-Frame-Options"] = "DENY"
		response.headers["Content-Security-Policy"] = (
			"default-src 'self'; img-src 'self' data:; style-src 'self'; "
			"form-action 'self'; frame-ancestors 'none'; base-uri 'none'"
		)
		return response

	@app.get("/")
	def dashboard() -> str:
		view = request.args.get("view", "users")
		if view not in ("users", "activity", "history"):
			abort(404)

		try:
			page = min(MAX_PAGE_NUMBER, max(1, int(request.args.get("page", "1"))))
		except ValueError:
			page = 1
		search = request.args.get("q", "").strip()[:MAX_SEARCH_LENGTH]
		offset = (page - 1) * PAGE_SIZE
		summary = get_web_dashboard_summary()
		data: dict[str, object] = {
			"view": view,
			"search": search,
			"page": page,
			"page_size": PAGE_SIZE,
			"summary": summary,
			"rows": [],
			"total": 0,
			"page_count": 1,
		}

		if view == "users":
			total, rows = get_web_users(search, PAGE_SIZE, offset)
			data.update(rows=rows, total=total, page_count=max(1, ceil(total / PAGE_SIZE)))
		elif view == "activity":
			data.update(rows=get_web_activity_counts())
		else:
			total, rows = get_web_click_history(search, PAGE_SIZE, offset)
			data.update(rows=rows, total=total, page_count=max(1, ceil(total / PAGE_SIZE)))
		return render_template("admin.html", **data)

	@app.get("/export/users.csv")
	def export_users() -> Response:
		return send_file(
			export_users_csv(),
			mimetype="text/csv; charset=utf-8",
			as_attachment=True,
			download_name="bot_users.csv",
		)

	@app.get("/export/activity.csv")
	def export_activity() -> Response:
		return send_file(
			export_user_activity_csv(),
			mimetype="text/csv; charset=utf-8",
			as_attachment=True,
			download_name="user_activity.csv",
		)

	@app.get("/export/history.csv")
	def export_history() -> Response:
		return send_file(
			export_user_activity_history_csv(),
			mimetype="text/csv; charset=utf-8",
			as_attachment=True,
			download_name="user_activity_history.csv",
		)

	return app


def main() -> None:
	"""Starts Waitress on loopback; put a TLS reverse proxy in front for internet access."""
	from waitress import serve

	load_dotenv()
	try:
		port = int(os.getenv("WEB_ADMIN_PORT", "8080"))
	except ValueError as error:
		raise RuntimeError("WEB_ADMIN_PORT must be a number between 1 and 65535") from error
	if not 1 <= port <= 65535:
		raise RuntimeError("WEB_ADMIN_PORT must be a number between 1 and 65535")

	serve(create_app(), host="127.0.0.1", port=port)


load_dotenv()
app = create_app()


if __name__ == "__main__":
	main()
