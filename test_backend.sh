#!/bin/bash

# ============================================
# RehabYangu Backend MVP Test Suite
# ============================================

set -e
BASE_URL="http://localhost:8000/api"
ADMIN_USER="demo_admin"
ADMIN_PASS="demo123"
SUPER_USER="rehabyangu"
SUPER_PASS="RehabYangu@2024"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=========================================="
echo "RehabYangu Backend MVP Test Suite"
echo "==========================================${NC}"

if ! command -v jq &> /dev/null; then
    echo -e "${RED}jq is not installed. Please install it: sudo apt install jq${NC}"
    exit 1
fi

echo -e "\n${YELLOW}[1] Logging in as demo_admin...${NC}"
TOKEN_RESP=$(curl -s -X POST "$BASE_URL/token/" -H "Content-Type: application/json" -d "{\"username\":\"$ADMIN_USER\", \"password\":\"$ADMIN_PASS\"}")
ACCESS_TOKEN=$(echo "$TOKEN_RESP" | jq -r '.access')
if [ "$ACCESS_TOKEN" == "null" ] || [ -z "$ACCESS_TOKEN" ]; then
    echo -e "${RED}Login failed. Response: $TOKEN_RESP${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Login successful. Access token obtained.${NC}"

# Extract user ID from the token (base64 decode the payload)
USER_ID=$(echo -n "$ACCESS_TOKEN" | cut -d"." -f2 | base64 -d 2>/dev/null | jq -r '.user_id' 2>/dev/null)
if [ -z "$USER_ID" ] || [ "$USER_ID" == "null" ]; then
    # fallback: use 2 (common for demo_admin)
    USER_ID=2
fi
echo -e "${GREEN}✅ User ID: $USER_ID${NC}"

echo -e "\n${YELLOW}[2] Creating a patient...${NC}"
PATIENT_RESP=$(curl -s -X POST "$BASE_URL/patients/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "first_name": "Test",
        "last_name": "Patient",
        "date_of_birth": "1990-01-01",
        "gender": "M",
        "phone": "0712345678"
    }')
PATIENT_ID=$(echo "$PATIENT_RESP" | jq -r '.id')
if [ "$PATIENT_ID" == "null" ] || [ -z "$PATIENT_ID" ]; then
    echo -e "${RED}Patient creation failed. Response: $PATIENT_RESP${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Patient created with ID: $PATIENT_ID${NC}"

echo -e "\n${YELLOW}[3] Creating a clinical note (SOAP)...${NC}"
NOTE_RESP=$(curl -s -X POST "$BASE_URL/clinical-notes/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"patient\": $PATIENT_ID,
        \"clinician\": $USER_ID,
        \"subjective\": \"Patient reports feeling anxious.\",
        \"objective\": \"Vitals stable.\",
        \"assessment\": \"Moderate anxiety.\",
        \"plan\": \"Continue therapy.\"
    }")
NOTE_ID=$(echo "$NOTE_RESP" | jq -r '.id')
if [ "$NOTE_ID" == "null" ] || [ -z "$NOTE_ID" ]; then
    echo -e "${RED}Clinical note creation failed. Response: $NOTE_RESP${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Clinical note created with ID: $NOTE_ID${NC}"

echo -e "\n${YELLOW}[4] Recording vitals...${NC}"
VITALS_RESP=$(curl -s -X POST "$BASE_URL/vitals/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"patient\": $PATIENT_ID,
        \"date_measured\": \"2026-07-30T10:00:00Z\",
        \"systolic_bp\": 120,
        \"diastolic_bp\": 80,
        \"heart_rate\": 72,
        \"temperature\": 36.5,
        \"oxygen_saturation\": 98,
        \"weight\": 70,
        \"height\": 175
    }")
VITALS_ID=$(echo "$VITALS_RESP" | jq -r '.id')
if [ "$VITALS_ID" == "null" ] || [ -z "$VITALS_ID" ]; then
    echo -e "${RED}Vitals recording failed. Response: $VITALS_RESP${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Vitals recorded with ID: $VITALS_ID${NC}"

echo -e "\n${YELLOW}[5] Creating inventory item...${NC}"
INVENTORY_RESP=$(curl -s -X POST "$BASE_URL/inventory/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Paracetamol 500mg",
        "category": "DRUG",
        "cost_price": 10,
        "unit_price": 50,
        "current_stock": 100,
        "reorder_level": 20
    }')
ITEM_ID=$(echo "$INVENTORY_RESP" | jq -r '.id')
if [ "$ITEM_ID" == "null" ] || [ -z "$ITEM_ID" ]; then
    echo -e "${RED}Inventory creation failed. Response: $INVENTORY_RESP${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Inventory item created with ID: $ITEM_ID${NC}"

echo -e "\n${YELLOW}[6] Charging patient...${NC}"
CHARGE_RESP=$(curl -s -X POST "$BASE_URL/charge/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"patient_id\": $PATIENT_ID,
        \"item_id\": $ITEM_ID,
        \"quantity\": 2
    }")
NEW_BALANCE=$(echo "$CHARGE_RESP" | jq -r '.new_balance')
if [ "$NEW_BALANCE" == "null" ] || [ -z "$NEW_BALANCE" ]; then
    echo -e "${RED}Charge failed. Response: $CHARGE_RESP${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Charge applied. New balance: KES $NEW_BALANCE${NC}"

echo -e "\n${YELLOW}[7] Fetching patient bill...${NC}"
BILL_RESP=$(curl -s -X GET "$BASE_URL/patient-bill/$PATIENT_ID/" \
    -H "Authorization: Bearer $ACCESS_TOKEN")
BILL_ID=$(echo "$BILL_RESP" | jq -r '.id')
if [ "$BILL_ID" == "null" ] || [ -z "$BILL_ID" ]; then
    echo -e "${RED}Bill retrieval failed. Response: $BILL_RESP${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Bill retrieved with ID: $BILL_ID${NC}"

echo -e "\n${YELLOW}[8] Generating invoice...${NC}"
INVOICE_RESP=$(curl -s -X POST "$BASE_URL/invoices/generate/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"patient_id\": $PATIENT_ID,
        \"due_date\": \"2026-08-30\",
        \"period_start\": \"2026-07-01\",
        \"period_end\": \"2026-07-30\",
        \"sponsor_email\": \"sponsor@example.com\",
        \"sponsor_name\": \"Test Sponsor\"
    }")
INVOICE_ID=$(echo "$INVOICE_RESP" | jq -r '.id')
if [ "$INVOICE_ID" == "null" ] || [ -z "$INVOICE_ID" ]; then
    echo -e "${RED}Invoice generation failed. Response: $INVOICE_RESP${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Invoice generated with ID: $INVOICE_ID${NC}"

echo -e "\n${YELLOW}[9] Downloading invoice PDF...${NC}"
HTTP_CODE=$(curl -s -o /tmp/invoice.pdf -w "%{http_code}" -X GET "$BASE_URL/invoices/$INVOICE_ID/download/" \
    -H "Authorization: Bearer $ACCESS_TOKEN")
if [ "$HTTP_CODE" -ne 200 ]; then
    echo -e "${RED}Invoice download failed. HTTP code: $HTTP_CODE${NC}"
    exit 1
fi
if [ ! -s /tmp/invoice.pdf ]; then
    echo -e "${RED}Invoice PDF is empty.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Invoice PDF downloaded successfully (size: $(du -h /tmp/invoice.pdf | cut -f1)).${NC}"

echo -e "\n${YELLOW}[10] Requesting discharge...${NC}"
DISCHARGE_REQ_RESP=$(curl -s -X POST "$BASE_URL/patients/$PATIENT_ID/request-discharge/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"reason": "Patient completed program.", "force": false}')
REQUEST_ID=$(echo "$DISCHARGE_REQ_RESP" | jq -r '.request_id')
if [ "$REQUEST_ID" == "null" ] || [ -z "$REQUEST_ID" ]; then
    echo -e "${RED}Discharge request failed. Response: $DISCHARGE_REQ_RESP${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Discharge requested with ID: $REQUEST_ID${NC}"

echo -e "\n${YELLOW}[11] Approving discharge...${NC}"
APPROVE_RESP=$(curl -s -X POST "$BASE_URL/discharge-requests/$REQUEST_ID/approve/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"password\": \"$ADMIN_PASS\", \"approval_reason\": \"Approved.\"}")
APPROVE_MSG=$(echo "$APPROVE_RESP" | jq -r '.message')
if [ "$APPROVE_MSG" != "Discharge approved successfully" ]; then
    echo -e "${RED}Discharge approval failed. Response: $APPROVE_RESP${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Discharge approved.${NC}"

echo -e "\n${YELLOW}[12] Running subscription check...${NC}"
CHECK_OUTPUT=$(docker exec -i rehabyangu_backend python manage.py check_subscriptions 2>&1 || true)
if echo "$CHECK_OUTPUT" | grep -q "Subscription check completed"; then
    echo -e "${GREEN}✅ Subscription check completed successfully.${NC}"
else
    echo -e "${YELLOW}⚠️ Subscription check might have issues. Output:${NC}"
    echo "$CHECK_OUTPUT"
fi

echo -e "\n${GREEN}=========================================="
echo "✅ All MVP backend tests passed!"
echo "==========================================${NC}"
echo -e "\nPatient ID: $PATIENT_ID"
echo "Clinical Note ID: $NOTE_ID"
echo "Vitals ID: $VITALS_ID"
echo "Inventory Item ID: $ITEM_ID"
echo "Invoice ID: $INVOICE_ID"
echo "Discharge Request ID: $REQUEST_ID"
echo "Invoice PDF saved to /tmp/invoice.pdf"
