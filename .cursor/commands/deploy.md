# Deploy the dashboard

Publish the current dashboard. Do this only when this command is run.

Amplify Hosting serves static files and Node servers. This dashboard is a Python Flask app, so the live site runs on Elastic Beanstalk. Do not create an Amplify app for it, and do not try to move it onto Amplify Hosting.

## Deploy

From the repo root, with network permission:

```bash
.venv/bin/python tools/deploy_dashboard.py
```

The script reads `.env` on this machine, uploads the source, and updates the `animevs-dashboard` environment in us-east-2. It does not print secret values except a brand-new sign-in password, the first time that password is created.

## Safety

- Do not commit `.env`, and do not print `MONGO_LOGIN`, `DISCORD_TOKEN`, `OPENAI_API`, `SUPABASE_SERVICE_KEY`, or `DASHBOARD_SECRET`.
- Do not commit, push, or force-push as part of this command.
- Do not change git config.
- If the script says the environment is unhealthy, read the Beanstalk events and the instance logs, fix the cause, and run the script again. Do not terminate the environment unless it is stuck Terminating.
- Leave the sign-in password in `.env`. The public site requires it because saves go to the live game database.

## Reply

Tell the user whether the deploy finished, the version label, and the https address the script printed. Repeat `DASHBOARD_PASSWORD` only when the script just created it. `animevsplus.me` is not registered, so do not point the site at that name.
