"""
Sample data loader for GovScheme AI Monitor
Run: python backend/test_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import random
from pymongo import MongoClient

# Import config
from backend.app.config import settings

client = MongoClient(settings.MONGO_URI)
db = client[settings.DB_NAME]

CATEGORIES = [
    "Agriculture & Farming", "Education & Scholarship",
    "Health & Medical", "Women & Child Development",
    "Employment & Skill Development", "Housing & Infrastructure",
    "Financial Inclusion & Banking", "Senior Citizens & Pension",
    "Environment & Energy"
]

SAMPLE_SCHEMES = [
    {
        "title": "PM Kisan Samman Nidhi - Annual Income Support for Farmers",
        "url": "https://pmkisan.gov.in/scheme-update-2024",
        "summary": "Under PM-KISAN, farmers receive Rs. 6000 per year in three equal installments of Rs. 2000 each, provided directly to bank accounts.",
        "category": "Agriculture & Farming",
        "is_relevant": True,
        "ai_summary": "PM-KISAN provides Rs. 6000 annual income support to small and marginal farmers directly through DBT. All landholding farmer families are eligible.",
        "target_beneficiaries": "Small and marginal farmers across India",
        "key_benefits": ["Rs. 6000 annual support", "Direct bank transfer", "No middlemen"],
        "source": "Government of India"
    },
    {
        "title": "Pradhan Mantri Awas Yojana - Housing for All Urban 2024",
        "url": "https://pmaymis.gov.in/update-2024",
        "summary": "PMAY Urban provides central assistance to Urban Local Bodies for housing to all eligible families in urban areas.",
        "category": "Housing & Infrastructure",
        "is_relevant": True,
        "ai_summary": "PMAY Urban offers subsidized home loans and direct subsidies to economically weaker sections for constructing or buying homes.",
        "target_beneficiaries": "EWS/LIG/MIG families in urban areas",
        "key_benefits": ["Interest subsidy up to 6.5%", "Rs. 2.5 lakh direct subsidy", "Women ownership mandatory"],
        "source": "Ministry of Housing"
    },
    {
        "title": "National Scholarship Portal - Merit Scholarships 2024-25",
        "url": "https://scholarships.gov.in/new-2024",
        "summary": "NSP provides scholarships to students from pre-matric to post-matric levels. Applications open for 2024-25 academic year.",
        "category": "Education & Scholarship",
        "is_relevant": True,
        "ai_summary": "NSP consolidates multiple central and state scholarships. Students from SC/ST/OBC/Minority communities can apply for pre/post-matric scholarships.",
        "target_beneficiaries": "SC/ST/OBC/Minority students",
        "key_benefits": ["Pre-matric scholarships", "Post-matric scholarships", "Merit-cum-means scholarships"],
        "source": "Ministry of Education"
    },
    {
        "title": "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana Update",
        "url": "https://pmjay.gov.in/coverage-update-2024",
        "summary": "PMJAY now covers 70+ crore beneficiaries with Rs. 5 lakh health cover per family per year at empanelled hospitals.",
        "category": "Health & Medical",
        "is_relevant": True,
        "ai_summary": "PMJAY (Ayushman Bharat) provides Rs. 5 lakh health insurance to poor families for secondary and tertiary care hospitalization.",
        "target_beneficiaries": "Poor and vulnerable families (SECC database)",
        "key_benefits": ["Rs. 5 lakh annual cover", "Cashless treatment", "Pre-existing conditions covered"],
        "source": "Ministry of Health"
    },
    {
        "title": "Skill India Mission - Free Vocational Training Programs 2024",
        "url": "https://skillindia.gov.in/programs-2024",
        "summary": "PMKVY 4.0 offers free short-term skill training with certificate and placement assistance across 200+ trade sectors.",
        "category": "Employment & Skill Development",
        "is_relevant": True,
        "ai_summary": "PMKVY provides free industry-relevant skill training to youth aged 15-45 with post-training placement support and Rs. 8000 reward on completion.",
        "target_beneficiaries": "Youth aged 15-45, school dropouts",
        "key_benefits": ["Free training", "Rs. 8000 completion reward", "Placement assistance"],
        "source": "Ministry of Skill Development"
    },
    {
        "title": "Beti Bachao Beti Padhao - New Districts Coverage 2024",
        "url": "https://wcd.nic.in/bbbp-update",
        "summary": "BBBP scheme expanded to all 640 districts to improve child sex ratio and promote education for girls.",
        "category": "Women & Child Development",
        "is_relevant": True,
        "ai_summary": "BBBP addresses declining CSR and empowers girl children through education support, awareness campaigns, and multi-sector interventions.",
        "target_beneficiaries": "Girl children and women across India",
        "key_benefits": ["Education scholarships for girls", "Health benefits", "Awareness programs"],
        "source": "Ministry of Women & Child Development"
    },
    {
        "title": "PM SVANidhi - Street Vendors Working Capital Loan Scheme",
        "url": "https://pmsvanidhi.mohua.gov.in/update",
        "summary": "SVANidhi provides affordable loans to street vendors to resume livelihoods post-COVID with Rs. 10,000 initial working capital.",
        "category": "Financial Inclusion & Banking",
        "is_relevant": True,
        "ai_summary": "PM SVANidhi offers collateral-free loans starting from Rs. 10,000 to street vendors with credit guarantee and digital transactions incentive.",
        "target_beneficiaries": "Street vendors in urban areas",
        "key_benefits": ["Rs. 10,000 initial loan", "Interest subsidy 7%", "Digital payment cashback"],
        "source": "Ministry of Housing & Urban Affairs"
    },
    {
        "title": "PM Ujjwala Yojana 3.0 - Free LPG Connections for BPL Families",
        "url": "https://pmuy.gov.in/ujjwala3",
        "summary": "PMUY 3.0 targets 75 lakh new BPL connections with free LPG cylinder for cooking fuel to reduce indoor air pollution.",
        "category": "Women & Child Development",
        "is_relevant": True,
        "ai_summary": "PMUY provides free LPG connections to BPL families, especially women, replacing traditional biomass cooking that causes indoor pollution.",
        "target_beneficiaries": "BPL families, especially women",
        "key_benefits": ["Free LPG connection", "First refill free", "Stove subsidy"],
        "source": "Ministry of Petroleum"
    }
]

SAMPLE_BLOGS = [
    {
        "scheme_title": "PM Kisan Samman Nidhi",
        "title": "PM-KISAN 2024: Complete Guide to Rs. 6000 Annual Farmer Support Scheme",
        "slug": "pm-kisan-samman-nidhi-2024-complete-guide",
        "meta_description": "PM-KISAN provides Rs. 6000 annual income support to small farmers. Check eligibility, how to apply, required documents, and status check.",
        "tags": ["PM Kisan", "Farmer Scheme", "Agriculture", "Government Scheme", "DBT"],
        "category": "Agriculture & Farming",
        "status": "published",
        "content_html": """<h1>PM-KISAN 2024: Complete Guide to Rs. 6000 Annual Farmer Support Scheme</h1>
<p>The Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) scheme is one of India's most impactful agricultural welfare programs, directly benefiting crores of farmers across the country with financial support of Rs. 6000 per year.</p>

<h2>What is PM-KISAN?</h2>
<p>PM-KISAN is a Central Sector Scheme launched on February 24, 2019 by the Government of India. The scheme provides income support of <strong>Rs. 6,000 per year</strong> to all landholding farmer families across the country, subject to certain exclusion criteria.</p>

<h2>Key Benefits</h2>
<ul>
<li>Rs. 6,000 annual financial support</li>
<li>Paid in 3 equal installments of Rs. 2,000 each</li>
<li>Direct Bank Transfer (DBT) — no middlemen</li>
<li>Money credited directly to farmer's Aadhaar-linked bank account</li>
</ul>

<h2>Eligibility Criteria</h2>
<p>All landholding farmer families whose names appear in the land records are eligible. However, the following categories are excluded:</p>
<ul>
<li>Institutional land holders</li>
<li>Farmer families holding constitutional posts</li>
<li>Current or former holders of ministerial posts</li>
<li>Income Tax payers</li>
<li>Professionals (doctors, engineers, lawyers, etc.)</li>
</ul>

<h2>How to Apply</h2>
<ol>
<li>Visit the official PM-KISAN portal: <a href="https://pmkisan.gov.in">pmkisan.gov.in</a></li>
<li>Click on "New Farmer Registration"</li>
<li>Enter your Aadhaar Number and mobile number</li>
<li>Fill in the required personal and bank details</li>
<li>Submit the form and note your reference number</li>
<li>Your application will be verified by local officials</li>
</ol>

<h2>Required Documents</h2>
<ul>
<li>Aadhaar Card (mandatory)</li>
<li>Land ownership documents / Khasra-Khatauni</li>
<li>Bank account passbook (must be Aadhaar-linked)</li>
<li>Mobile number linked to Aadhaar</li>
</ul>

<h2>Check Payment Status</h2>
<p>Visit <a href="https://pmkisan.gov.in">pmkisan.gov.in</a> → Beneficiary Status → Enter Aadhaar/Account/Mobile number to check your installment status.</p>

<p><strong>Source:</strong> <a href="https://pmkisan.gov.in">PM-KISAN Official Portal</a></p>"""
    }
]

def load_sample_data():
    print("🔄 Loading sample data...")

    # Clear existing
    db.schemes.delete_many({})
    db.blogs.delete_many({})
    db.pipeline_logs.delete_many({})
    print("🗑️  Cleared existing data")

    # Insert schemes
    for i, scheme in enumerate(SAMPLE_SCHEMES):
        scheme["url"] = scheme.get("url", f"https://example.gov.in/scheme-{i}")
        scheme["fetched_at"] = datetime.utcnow() - timedelta(hours=random.randint(1, 48))
        scheme["published_date"] = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        scheme["blog_generated"] = False
        scheme["blog_id"] = None
        scheme["wp_post_id"] = None
        scheme["status"] = "filtered"

    result = db.schemes.insert_many(SAMPLE_SCHEMES)
    print(f"✅ Inserted {len(result.inserted_ids)} sample schemes")

    # Insert blogs
    for i, blog in enumerate(SAMPLE_BLOGS):
        scheme = db.schemes.find_one({"title": {"$regex": blog["scheme_title"]}})
        blog["scheme_id"] = str(scheme["_id"]) if scheme else None
        blog["created_at"] = datetime.utcnow() - timedelta(hours=random.randint(1, 24))
        blog["published_at"] = datetime.utcnow() - timedelta(hours=random.randint(1, 12))
        blog["wp_post_id"] = random.randint(100, 999)
        blog["wp_url"] = f"https://your-site.com/?p={blog['wp_post_id']}"
        blog["featured_image_prompt"] = "Indian farmers working in green fields"

    result = db.blogs.insert_many(SAMPLE_BLOGS)
    print(f"✅ Inserted {len(result.inserted_ids)} sample blogs")

    # Update scheme blog_generated flag
    for blog in db.blogs.find():
        if blog.get("scheme_id"):
            from bson import ObjectId
            db.schemes.update_one(
                {"_id": ObjectId(blog["scheme_id"])},
                {"$set": {"blog_generated": True, "blog_id": str(blog["_id"]), "status": "published"}}
            )

    # Insert sample pipeline logs
    logs = [
        {"type": "full_pipeline", "timestamp": datetime.utcnow() - timedelta(minutes=30),
         "results": {"fetch": {"total_new": 5}, "filter": {"relevant": 3}, "blog": {"generated": 2}}},
        {"type": "fetch", "timestamp": datetime.utcnow() - timedelta(hours=1),
         "results": {"total_fetched": 12, "total_new": 8}},
    ]
    db.pipeline_logs.insert_many(logs)
    print("✅ Inserted sample pipeline logs")

    print("\n🎉 Sample data loaded successfully!")
    print(f"📊 Schemes: {db.schemes.count_documents({})}")
    print(f"📝 Blogs: {db.blogs.count_documents({})}")
    print(f"📋 Logs: {db.pipeline_logs.count_documents({})}")

if __name__ == "__main__":
    load_sample_data()
