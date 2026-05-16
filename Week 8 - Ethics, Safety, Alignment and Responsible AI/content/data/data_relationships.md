# E-Commerce Data Relationships

## Entity Relationship Diagram

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│  CUSTOMERS   │────1:N──│    ORDERS    │────1:1──│   PAYMENTS   │
└──────────────┘         └──────────────┘         └──────────────┘
                                │
                               N:M
                                │
                         ┌──────────────┐
                         │   PRODUCTS   │
                         └──────────────┘
```

## Relationship Details

### 1. Customer → Orders (One-to-Many)
- **Primary Key**: `customer_id` in Customers table
- **Foreign Key**: `customer_id` in Orders table
- **Description**: One customer can have multiple orders
- **Example**: Customer CUST-2001 has orders ORD-10001 and ORD-10005

### 2. Order → Payment (One-to-One)
- **Primary Key**: `order_id` in Orders table
- **Foreign Key**: `order_id` in Payments table
- **Description**: Each order has exactly one payment record
- **Validation**: `total_amount` in Orders must match `amount` in Payments
- **Example**: Order ORD-10001 has payment PAY-487291

### 3. Order → Products (Many-to-Many)
- **Relationship Table**: Order items array within Orders
- **Keys**: `product_id` references Products table
- **Description**: Each order can contain multiple products, and each product can be in multiple orders
- **Example**: Order ORD-10001 contains products PROD-1001 and PROD-1002

### 4. Customer → Payments (One-to-Many via Orders)
- **Indirect Relationship**: Through Orders table
- **Validation**: `customer_id` exists in both Orders and Payments for cross-validation
- **Purpose**: Audit trail and fraud prevention

## Data Integrity Rules

### Payment-Order Consistency
```json
{
  "rule": "payment.amount == order.total_amount",
  "validation": "Payment amount must match order total",
  "example": "Order ORD-10001 total: $1302.26 = Payment PAY-487291 amount: $1302.26"
}
```

### Customer-Order Validation
```json
{
  "rule": "order.customer_id must exist in customers",
  "validation": "Every order must belong to a valid customer",
  "example": "Order ORD-10001 belongs to Customer CUST-2001"
}
```

### Product Availability
```json
{
  "rule": "order.items[].product_id must exist in products",
  "validation": "Ordered products must exist in catalog",
  "example": "Order item references PROD-1001 which exists in products"
}
```

## Sensitive Data Mapping

### High Sensitivity (PII & Financial)
- **Customers**: SSN, date_of_birth, full_name, email, phone
- **Payments**: card_number_full, cvv, cardholder_name

### Medium Sensitivity
- **Orders**: shipping_address, customer purchase patterns
- **Payments**: card_last_four, billing_address

### Low Sensitivity
- **Products**: All fields (public catalog data)

## Access Control Recommendations

### Customer Service Agent Access
- ✅ View: Order status, shipping info, product details
- ✅ View (Masked): Last 4 digits of card, partial address
- ❌ No Access: Full card numbers, CVV, SSN

### Data Analytics Access
- ✅ View: Aggregated purchase data, product performance
- ✅ View (Anonymized): Customer demographics
- ❌ No Access: Individual PII, payment details

### System Admin Access
- ✅ Full Access: All data with audit logging
- ⚠️ Monitoring: All sensitive data access logged

## Query Examples

### Get Order with Payment Details (Masked)
```sql
SELECT 
    o.order_id,
    o.customer_id,
    o.total_amount,
    p.payment_id,
    p.card_details->>'card_last_four' as card_last_four,
    p.status as payment_status
FROM orders o
JOIN payments p ON o.order_id = p.order_id
WHERE o.order_id = 'ORD-10001';
```

### Get Customer Order History (Without Sensitive Data)
```sql
SELECT 
    o.order_id,
    o.order_date,
    o.total_amount,
    o.status,
    o.tracking_number
FROM orders o
WHERE o.customer_id = 'CUST-2001'
ORDER BY o.order_date DESC;
```

## Responsible AI Implementation Notes

1. **Data Masking**: Always mask sensitive fields in AI responses
2. **Access Logging**: Log all access to sensitive data fields
3. **Purpose Limitation**: Only access data necessary for the specific query
4. **Data Minimization**: Return minimum required information
5. **Consent Verification**: Check marketing_consent before using customer data for promotions