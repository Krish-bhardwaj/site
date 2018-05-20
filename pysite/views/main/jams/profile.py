import datetime

from flask import redirect, request, url_for
from werkzeug.exceptions import BadRequest

from pysite.base_route import RouteView
from pysite.decorators import csrf
from pysite.mixins import DBMixin, OauthMixin


class JamsProfileView(RouteView, DBMixin, OauthMixin):
    path = "/jams/profile"
    name = "jams.profile"

    table_name = "code_jam_participants"

    def get(self):
        if not self.user_data:
            return redirect(url_for("discord.login"))

        participant = self.db.get(self.table_name, self.user_data["user_id"])

        if not participant:
            participant = {"id": self.user_data["user_id"]}

        form = request.args.get("form")

        if form:
            try:
                form = int(form)
            except ValueError:
                pass  # Someone trying to have some fun I guess

        return self.render(
            "main/jams/profile.html", participant=participant, form=form
        )

    @csrf
    def post(self):
        if not self.user_data:
            return redirect(url_for("discord.login"))

        participant = self.db.get(self.table_name, self.user_data["user_id"])

        if not participant:
            participant = {"id": self.user_data["user_id"]}

        dob = request.form.get("dob")
        github_username = request.form.get("github_username")
        timezone = request.form.get("timezone")

        if not dob or not github_username or not timezone:
            return BadRequest()

        # Convert given datetime strings into actual objects, adding timezones to keep rethinkdb happy
        dob = datetime.datetime.strptime(dob, "%Y-%m-%d")
        dob = dob.replace(tzinfo=datetime.timezone.utc)

        participant["dob"] = dob
        participant["github_username"] = github_username
        participant["timezone"] = timezone

        self.db.insert(self.table_name, participant, conflict="replace")

        form = request.args.get("form")

        if form:
            try:
                form = int(form)
            except ValueError:
                pass  # Someone trying to have some fun I guess
            else:
                return redirect(url_for("main.jams.join", jam=form))

        return self.render(
            "main/jams/profile.html", participant=participant, done=True
        )