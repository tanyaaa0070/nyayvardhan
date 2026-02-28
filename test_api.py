"""Test: Corruption / Bribery Case"""
import requests
import json

r = requests.post("http://localhost:8000/api/analyze", json={
    "case_text": (
        "The accused Rajiv Sharma, a government officer in the Public Works Department, "
        "was arrested for demanding and accepting a bribe of Rs 5 lakh from a contractor "
        "for approving construction bills. The Anti-Corruption Bureau conducted a trap "
        "operation and caught the accused red-handed while accepting the bribe amount. "
        "The marked currency notes were recovered from the accused possession. The accused "
        "was charged under Section 7 of the Prevention of Corruption Act and IPC 420 for "
        "cheating. The accused applied for bail under CrPC 437 arguing that he is a "
        "first-time offender with no criminal record and has deep roots in society. "
        "The prosecution opposed bail stating the gravity of the offence and the possibility "
        "of evidence tampering. Article 14 equality before law and Article 21 right to "
        "personal liberty were cited by the defense counsel. The investigation revealed "
        "disproportionate assets worth Rs 2 crore in the name of the accused and his family "
        "members. Bank statements and property documents were seized under CrPC 91."
    ),
    "top_k": 5
})

d = r.json()

print("=" * 60)
print("  NYAYVANDAN TEST RESULT")  
print("=" * 60)

print("\nEXTRACTED ENTITIES:")
for k, v in d["extracted_entities"].items():
    if v:
        print(f"  {k}: {', '.join(v)}")

print("\nSIMILAR CASES FOUND:")
for i, c in enumerate(d["similar_cases"], 1):
    title = c["case_title"][:65]
    print(f"\n  {i}. {c['case_id']} - {title}")
    print(f"     Court: {c['court']} | Year: {c['year']}")
    print(f"     Similarity: {c['similarity_label']} (score: {c['scores']['hybrid']})")
    print(f"     Outcome: {c['judgment_outcome']}")

print("\n" + "-" * 60)
print("ETHICAL FLAGS:")
print(f"  Has concerns: {d['ethical_flags']['has_ethical_concerns']}")
score = d["ethical_flags"]["diversity_score"]["overall_score"]
print(f"  Diversity score: {score}")
for w in d["ethical_flags"]["bias_warnings"]:
    msg = w["message"][:100]
    print(f"  [{w['severity']}] {msg}...")

print("\nEXPLANATIONS (first case):")
if d["explanations"]:
    exp = d["explanations"][0]
    print(f"  {exp['explanation_text'][:200]}...")
