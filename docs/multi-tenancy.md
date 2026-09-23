# Multi-Tenancy Architecture

**Status:** Current
**Last Updated:** 2026-09-23

## Overview

RehabYangu uses a shared-database, shared-schema multi-tenant model with PostgreSQL Row-Level Security (RLS) for isolation.

## Why Shared Schema

| Consideration | Shared Schema + RLS | Schema-per-Tenant |
|---|---|---|
| Migrations | One run for all tenants | N runs |
| Connection pooling | Simple | Complex |
| Cost at pilot scale | Low | Higher |
| Cross-tenant analytics | Easy | Requires aggregation |
| Enterprise isolation | Migrate later if needed | Native |

## How Tenant Context Flows

1. User enters workspace slug on login (e.g. serenity).
2. Frontend sends X-Tenant: serenity on every API request.
3. Backend resolves the tenant in TenantTokenObtainPairView.get_tenant().
4. JWT is issued with tenant_id in the payload.
5. On every subsequent request, TenantJWTAuthentication reads tenant_id and sets request.tenant.
6. TenantRLSMiddleware wraps the request in a transaction and calls set_rls_context(tenant_id), setting PostgreSQL session variable app.tenant_id.
7. RLS policies on every tenant-scoped table filter by tenant_id = current_setting('app.tenant_id')::bigint.

## RLS Policy Structure

Every tenant-owned table has a policy like:

```sql
CREATE POLICY tenant_isolation ON public.patients_patient
  USING (tenant_id = public.rehabyangu_current_tenant_id()
         OR public.rehabyangu_is_platform_admin())
  WITH CHECK (tenant_id = public.rehabyangu_current_tenant_id()
              OR public.rehabyangu_is_platform_admin());
FORCE ROW LEVEL SECURITY is set. The application connects as rehabyangu_app, which has no BYPASSRLS.
Database Roles
Role	Purpose	Privileges
rehabyangu	Owner — migrations, schema changes	Superuser, BYPASSRLS
rehabyangu_app	Application runtime	NOSUPERUSER, no BYPASSRLS, SELECT/INSERT/UPDATE/DELETE
Membership Enforcement

    Login without a membership: token endpoint returns 403.

    Authenticated request after membership is deleted: next request returns 401.

Verifying Isolation
bash

# Without tenant context — expect 0
docker exec -e PGPASSWORD=rehabyangu_app_dev rehabyangu_db psql -U rehabyangu_app -d rehabyangu -c \
  "BEGIN; SELECT set_config('app.tenant_id','',true); SELECT count(*) FROM patients_patient; ROLLBACK;"

# With tenant 1 context — expect actual count
docker exec -e PGPASSWORD=rehabyangu_app_dev rehabyangu_db psql -U rehabyangu_app -d rehabyangu -c \
  "BEGIN; SELECT set_config('app.tenant_id','1',true); SELECT count(*) FROM patients_patient; ROLLBACK;"

