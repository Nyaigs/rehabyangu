# Phase 3 — EMR backend verification

The API uses tenant-bound JWTs. `ADMIN_ACCESS` needs the `role.read`
permission in order to inspect the audit log. `CLINICIAN_ACCESS` needs
`patient.write`, `clinical.read`, and `clinical.write`; `NURSE_ACCESS` needs
`clinical.read` only.

```bash
cd backend
../backend/venv/bin/python manage.py migrate
../backend/venv/bin/python manage.py test clinical
```

Set the endpoint, tenant, and three tenant-scoped bearer tokens:

```bash
export API=http://localhost:8000/api
export TENANT=demo
export ADMIN_ACCESS='replace-with-a-rehab-admin-access-token'
export CLINICIAN_ACCESS='replace-with-a-clinician-access-token'
export NURSE_ACCESS='replace-with-a-nurse-access-token'
```

Create the patient, retaining the returned `id` as `PATIENT_ID`:

```bash
curl -sS -X POST "$API/patients/" \
  -H "Authorization: Bearer $CLINICIAN_ACCESS" -H "X-Tenant: $TENANT" \
  -H 'Content-Type: application/json' \
  -d '{"first_name":"Amina","last_name":"Otieno","date_of_birth":"1990-01-01","gender":"F","phone":"+254700000001","address":"Nairobi","emergency_contact_name":"John Otieno","emergency_contact_phone":"+254700000002","next_of_kin_relationship":"Brother"}'

export PATIENT_ID=1
```

Create an admission (save its `id` as `ADMISSION_ID`):

```bash
curl -sS -X POST "$API/admissions/" \
  -H "Authorization: Bearer $CLINICIAN_ACCESS" -H "X-Tenant: $TENANT" \
  -H 'Content-Type: application/json' \
  -d "{\"patient\":$PATIENT_ID,\"intake_date\":\"2026-08-07T08:00:00Z\",\"room\":\"Ward A\",\"bed\":\"A-03\",\"primary_diagnosis\":\"Alcohol-use disorder\"}"

export ADMISSION_ID=1
```

Write a clinical note and retain `id` as `NOTE_ID`:

```bash
curl -sS -X POST "$API/clinical-notes/" \
  -H "Authorization: Bearer $CLINICIAN_ACCESS" -H "X-Tenant: $TENANT" \
  -H 'Content-Type: application/json' \
  -d "{\"patient\":$PATIENT_ID,\"admission\":$ADMISSION_ID,\"subjective\":\"Reports improved sleep.\",\"objective\":\"Calm and cooperative.\",\"assessment\":\"Improving.\",\"plan\":\"Continue group therapy.\"}"

export NOTE_ID=1
```

The nurse can read it, but PATCH is not routed (clinical notes are append-only)
and returns `405 Method Not Allowed`:

```bash
curl -i -sS "$API/clinical-notes/$NOTE_ID/" \
  -H "Authorization: Bearer $NURSE_ACCESS" -H "X-Tenant: $TENANT"

curl -i -sS -X PATCH "$API/clinical-notes/$NOTE_ID/" \
  -H "Authorization: Bearer $NURSE_ACCESS" -H "X-Tenant: $TENANT" \
  -H 'Content-Type: application/json' -d '{"plan":"Changed"}'
```

Finally, confirm the GET emitted a `READ` event for the note. The audit table
is immutable at the database layer:

```bash
curl -sS "$API/audit-logs/" \
  -H "Authorization: Bearer $ADMIN_ACCESS" -H "X-Tenant: $TENANT" \
  | jq --argjson note_id "$NOTE_ID" '.[] | select(.action == "READ" and .object_id == $note_id)'
```

Corrections are explicit new versions rather than edits:

```bash
curl -sS -X POST "$API/clinical-notes/$NOTE_ID/corrections/" \
  -H "Authorization: Bearer $CLINICIAN_ACCESS" -H "X-Tenant: $TENANT" \
  -H 'Content-Type: application/json' \
  -d '{"subjective":"Clarification: sleep improved over two nights.","objective":"Calm and cooperative.","assessment":"Improving.","plan":"Continue group therapy.","correction_reason":"Clarified timing stated in original note."}'
```
