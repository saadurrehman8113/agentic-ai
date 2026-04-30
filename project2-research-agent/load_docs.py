from knowledge_base import load_documents, count

# Simulate a company knowledge base —
# In a real project: load from PDFs, markdown files, a database, etc.
documents = [

    # ── Account & Auth ──
    {
        "id": "auth-001",
        "text": "To reset your password, go to the login page and click "
                "'Forgot Password'. Enter your registered email address. "
                "You will receive a reset link within 5 minutes. "
                "The link expires after 30 minutes.",
        "metadata": {"source": "faq", "category": "account"}
    },
    {
        "id": "auth-002",
        "text": "Two-factor authentication (2FA) can be enabled from "
                "Account Settings > Security. We support authenticator "
                "apps like Google Authenticator and Authy. SMS-based "
                "2FA is also available for premium users.",
        "metadata": {"source": "faq", "category": "account"}
    },

    # ── Billing ──
    {
        "id": "bill-001",
        "text": "We accept Visa, Mastercard, and bank transfers. "
                "PayPal is supported in selected countries. "
                "All transactions are processed in USD. "
                "Pakistani users can pay via Easypaisa or JazzCash.",
        "metadata": {"source": "billing", "category": "payments"}
    },
    {
        "id": "bill-002",
        "text": "Refunds are available within 30 days of purchase for "
                "annual plans. Monthly plans can be cancelled anytime "
                "but are non-refundable. To request a refund, contact "
                "support@company.com with your order ID.",
        "metadata": {"source": "billing", "category": "refunds"}
    },
    {
        "id": "bill-003",
        "text": "Invoices are automatically generated on your billing date "
                "and sent to your registered email. You can also download "
                "past invoices from Account > Billing > Invoice History.",
        "metadata": {"source": "billing", "category": "invoices"}
    },

    # ── Plans & Pricing ──
    {
        "id": "plan-001",
        "text": "We offer three plans: Starter ($9/month), Pro ($29/month), "
                "and Enterprise (custom pricing). Annual billing gives a "
                "20% discount on all plans. Students get 50% off with a "
                "valid university email.",
        "metadata": {"source": "pricing", "category": "plans"}
    },
    {
        "id": "plan-002",
        "text": "The Pro plan includes unlimited projects, priority support, "
                "API access, and team collaboration for up to 10 members. "
                "The Starter plan is limited to 3 projects and 1 user.",
        "metadata": {"source": "pricing", "category": "plans"}
    },

    # ── Technical / API ──
    {
        "id": "api-001",
        "text": "API keys can be generated from Developer Settings > API Keys. "
                "Each key has a rate limit of 1000 requests per hour. "
                "Keys should be kept secret and never committed to public "
                "repositories. Rotate keys immediately if compromised.",
        "metadata": {"source": "docs", "category": "api"}
    },
    {
        "id": "api-002",
        "text": "Our REST API uses JSON. Authentication requires passing your "
                "API key in the Authorization header as: "
                "Authorization: Bearer YOUR_API_KEY. "
                "All endpoints return standard HTTP status codes.",
        "metadata": {"source": "docs", "category": "api"}
    },

    # ── Support ──
    {
        "id": "support-001",
        "text": "Support is available Monday to Friday, 9am to 6pm PKT. "
                "Pro and Enterprise users get 24/7 priority support. "
                "Average response time is under 2 hours for Pro users "
                "and under 8 hours for Starter users.",
        "metadata": {"source": "support", "category": "help"}
    },
    {
        "id": "support-002",
        "text": "You can reach support via email at support@company.com, "
                "via live chat on our website, or by opening a ticket "
                "in your dashboard. Enterprise users have a dedicated "
                "Slack channel with their account manager.",
        "metadata": {"source": "support", "category": "help"}
    },
]

load_documents(documents)
print(f"\nTotal documents in knowledge base: {count()}")