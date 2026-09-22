# Subscription operations

Subscription state is evaluated by one idempotent command:

```bash
cd backend
python3 manage.py check_subscriptions
```

Run this command at least daily in production (for example, from a cron job or
the deployment scheduler). The command itself owns lifecycle transitions and
notification de-duplication; do not implement equivalent date checks in a web
request handler or scheduler.

The standard packages can safely be seeded or updated with:

```bash
python3 manage.py seed_subscription_plans
```

MRR is expected monthly value for active paid tenants only. Trial, overdue, and
suspended tenants are deliberately excluded; payment records remain the source
for historical payment reporting.
