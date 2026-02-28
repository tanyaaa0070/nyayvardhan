"""
NyayVandan - Sample Indian Legal Dataset Generator
====================================================
Generates a realistic sample dataset for offline development.
In production, replace with a full Kaggle Indian Court Judgments dataset.

Dataset columns:
  - case_id: Unique identifier
  - case_title: Short title
  - case_text: Detailed facts of the case
  - court: Court that heard the case
  - year: Year of judgment
  - ipc_sections: Applicable IPC sections (comma-separated)
  - crpc_sections: Applicable CrPC sections (comma-separated)
  - constitutional_articles: Applicable constitutional articles
  - judgment_outcome: Outcome label (Convicted, Acquitted, etc.)
"""

import pandas as pd
import os

# --- Sample Indian Legal Cases ---
cases = [
    {
        "case_id": "NV-2024-001",
        "case_title": "State v. Ramesh Kumar",
        "case_text": "The accused Ramesh Kumar was charged under IPC 302 for the murder of his business partner. "
                     "The prosecution presented forensic evidence including DNA and fingerprint analysis. "
                     "Three eyewitnesses testified to seeing the accused at the scene. "
                     "The defense argued alibi and lack of motive. The Sessions Court examined ballistic evidence "
                     "and CCTV footage from nearby establishments. The victim had sustained multiple stab wounds "
                     "as per the post-mortem report. Article 21 right to life was invoked by prosecution.",
        "court": "Delhi High Court",
        "year": 2023,
        "ipc_sections": "302,201",
        "crpc_sections": "154,161,313",
        "constitutional_articles": "21",
        "judgment_outcome": "Convicted"
    },
    {
        "case_id": "NV-2024-002",
        "case_title": "Priya Sharma v. State of Maharashtra",
        "case_text": "The petitioner Priya Sharma filed a bail application under CrPC 437 after being arrested "
                     "for charges under IPC 420 for allegedly defrauding investors in a Ponzi scheme. "
                     "The accused collected over Rs 50 crore from 2000 investors promising 30% returns. "
                     "The Economic Offences Wing investigated the case. The defense argued that the petitioner "
                     "was a minor employee and not the mastermind. Article 14 and Article 21 were cited "
                     "regarding prolonged pre-trial detention.",
        "court": "Bombay High Court",
        "year": 2023,
        "ipc_sections": "420,406,120B",
        "crpc_sections": "437,439",
        "constitutional_articles": "14,21",
        "judgment_outcome": "Bail Granted"
    },
    {
        "case_id": "NV-2024-003",
        "case_title": "State of UP v. Mohammad Irfan",
        "case_text": "The accused Mohammad Irfan was charged under IPC 376 for the alleged sexual assault "
                     "of a minor. The POCSO Act provisions were also invoked. Medical examination confirmed "
                     "the assault. The victim's statement under CrPC 164 was recorded before a Magistrate. "
                     "The defense challenged the delay in filing FIR under CrPC 154. DNA evidence matched "
                     "the accused. The court considered Article 21 right to dignity of the victim.",
        "court": "Allahabad High Court",
        "year": 2022,
        "ipc_sections": "376,506",
        "crpc_sections": "154,164,309",
        "constitutional_articles": "21,15",
        "judgment_outcome": "Convicted"
    },
    {
        "case_id": "NV-2024-004",
        "case_title": "Sunil Enterprises v. State of Karnataka",
        "case_text": "A writ petition challenging the cancellation of a mining license. The petitioner "
                     "Sunil Enterprises argued violation of Article 19(1)(g) right to practice any profession. "
                     "The state argued environmental violations under the Mines and Minerals Act. "
                     "The court examined whether due process under Article 14 was followed before cancellation. "
                     "Environmental impact assessment reports were submitted as evidence.",
        "court": "Karnataka High Court",
        "year": 2022,
        "ipc_sections": "",
        "crpc_sections": "",
        "constitutional_articles": "14,19,21,48A",
        "judgment_outcome": "Petition Dismissed"
    },
    {
        "case_id": "NV-2024-005",
        "case_title": "Arun Patel v. State of Gujarat",
        "case_text": "The accused Arun Patel was charged under IPC 304A for causing death by negligence "
                     "in a road accident. The accused was driving under the influence of alcohol. "
                     "The victim was a pedestrian crossing at a designated crossing. Traffic camera footage "
                     "showed the accused running a red light. Blood alcohol test confirmed intoxication above "
                     "legal limits. CrPC 174 inquest proceedings were conducted. The Motor Vehicles Act "
                     "provisions were also invoked.",
        "court": "Gujarat High Court",
        "year": 2023,
        "ipc_sections": "304A,279,338",
        "crpc_sections": "154,174",
        "constitutional_articles": "21",
        "judgment_outcome": "Convicted"
    },
    {
        "case_id": "NV-2024-006",
        "case_title": "Kavitha Reddy v. Union of India",
        "case_text": "A public interest litigation challenging the constitutionality of certain provisions "
                     "in the IT Act relating to digital surveillance. The petitioner argued violation of "
                     "Article 21 right to privacy as established in Puttaswamy judgment. Article 19(1)(a) "
                     "freedom of speech and expression was also invoked. The government argued national "
                     "security under Article 19(2) reasonable restrictions. The court examined proportionality "
                     "and necessity tests for surveillance measures.",
        "court": "Supreme Court of India",
        "year": 2023,
        "ipc_sections": "",
        "crpc_sections": "",
        "constitutional_articles": "14,19,21",
        "judgment_outcome": "Partially Allowed"
    },
    {
        "case_id": "NV-2024-007",
        "case_title": "State v. Deepak Singh & Others",
        "case_text": "The accused Deepak Singh along with three co-accused were charged under IPC 395 "
                     "for dacoity and IPC 397 for robbery with attempt to cause death. The gang robbed "
                     "a jewelry store in broad daylight, assaulting the owner causing grievous injuries. "
                     "IPC 34 common intention was invoked against all accused. Recovery of stolen gold "
                     "ornaments was made under CrPC 27. Identification parade was conducted under "
                     "CrPC 9. CCTV evidence was presented.",
        "court": "Rajasthan High Court",
        "year": 2022,
        "ipc_sections": "395,397,34,452",
        "crpc_sections": "27,9,154",
        "constitutional_articles": "",
        "judgment_outcome": "Convicted"
    },
    {
        "case_id": "NV-2024-008",
        "case_title": "Meena Kumari v. State of Bihar",
        "case_text": "A habeas corpus petition filed by Meena Kumari under Article 32 challenging "
                     "the illegal detention of her husband without producing before a Magistrate within "
                     "24 hours as required under Article 22 and CrPC 57. The police had arrested her "
                     "husband on suspicion of IPC 379 theft but failed to follow due process. "
                     "The court examined custodial rights under Article 21 and 22.",
        "court": "Patna High Court",
        "year": 2023,
        "ipc_sections": "379",
        "crpc_sections": "57,167,41",
        "constitutional_articles": "21,22,32",
        "judgment_outcome": "Petition Allowed"
    },
    {
        "case_id": "NV-2024-009",
        "case_title": "State of Tamil Nadu v. Rajkumar",
        "case_text": "The accused Rajkumar was charged under IPC 498A for cruelty towards his wife "
                     "and IPC 304B for dowry death. The victim died under suspicious circumstances "
                     "within two years of marriage. The prosecution relied on dying declaration recorded "
                     "under CrPC 32. Evidence of dowry demands was presented through witnesses "
                     "and WhatsApp messages. The Dowry Prohibition Act was also invoked. "
                     "Article 15 gender equality was referenced by the prosecution.",
        "court": "Madras High Court",
        "year": 2022,
        "ipc_sections": "498A,304B,306",
        "crpc_sections": "154,161,32",
        "constitutional_articles": "15,21",
        "judgment_outcome": "Convicted"
    },
    {
        "case_id": "NV-2024-010",
        "case_title": "Vikram Industries v. State of Maharashtra",
        "case_text": "The petitioner challenged the attachment of property under the Prevention of "
                     "Money Laundering Act. The Enforcement Directorate had provisionally attached "
                     "assets worth Rs 200 crore. The company argued violation of Article 300A right "
                     "to property and Article 19(1)(g) right to trade. The court examined whether "
                     "there was sufficient evidence linking the property to proceeds of crime. "
                     "The predicate offence was under IPC 420 and IPC 467 forgery.",
        "court": "Bombay High Court",
        "year": 2023,
        "ipc_sections": "420,467,471",
        "crpc_sections": "",
        "constitutional_articles": "14,19,300A",
        "judgment_outcome": "Partially Allowed"
    },
    {
        "case_id": "NV-2024-011",
        "case_title": "State v. Lakshmi Narayan",
        "case_text": "The accused Lakshmi Narayan, a public servant, was charged under IPC 13 of "
                     "Prevention of Corruption Act and IPC 409 for criminal breach of trust by public servant. "
                     "CBI investigation revealed disproportionate assets worth Rs 15 crore. "
                     "The accused held position of Joint Secretary. Bank records and property documents "
                     "were seized under CrPC 91. The defense argued legitimate income sources "
                     "and ancestral property. Article 311 procedure for dismissal was also examined.",
        "court": "Delhi High Court",
        "year": 2023,
        "ipc_sections": "409,420,13",
        "crpc_sections": "91,154,161",
        "constitutional_articles": "311,14",
        "judgment_outcome": "Convicted"
    },
    {
        "case_id": "NV-2024-012",
        "case_title": "Anjali Devi v. State of Madhya Pradesh",
        "case_text": "The petitioner Anjali Devi filed for anticipatory bail under CrPC 438 in a case "
                     "registered under IPC 306 for abetment to suicide. The deceased was the petitioner's "
                     "daughter-in-law who left a suicide note alleging harassment. The prosecution opposed bail "
                     "citing severity of allegations and risk of evidence tampering. The court considered "
                     "Article 21 personal liberty while balancing investigation needs.",
        "court": "Madhya Pradesh High Court",
        "year": 2022,
        "ipc_sections": "306,498A,34",
        "crpc_sections": "438,154",
        "constitutional_articles": "21",
        "judgment_outcome": "Bail Granted"
    },
    {
        "case_id": "NV-2024-013",
        "case_title": "Workers Union v. ABC Manufacturing Ltd",
        "case_text": "An industrial dispute regarding wrongful termination of 150 factory workers. "
                     "The workers were terminated without following the provisions of the Industrial "
                     "Disputes Act 1947. The management argued poor financial performance and restructuring. "
                     "Article 14 equality and Article 21 right to livelihood were invoked. "
                     "The court examined whether Section 25F of ID Act was complied with. "
                     "Collective bargaining rights under Article 19(1)(c) were also discussed.",
        "court": "Supreme Court of India",
        "year": 2023,
        "ipc_sections": "",
        "crpc_sections": "",
        "constitutional_articles": "14,19,21,43",
        "judgment_outcome": "Workers Reinstated"
    },
    {
        "case_id": "NV-2024-014",
        "case_title": "State v. Harish Chandra",
        "case_text": "The accused Harish Chandra was charged under IPC 307 for attempt to murder "
                     "and IPC 326 for voluntarily causing grievous hurt by dangerous weapons. "
                     "The accused attacked his neighbor with an axe over a land dispute. The victim "
                     "sustained life-threatening injuries. FIR was filed under CrPC 154. "
                     "Weapon was recovered under CrPC 27. Medical evidence confirmed the nature "
                     "of injuries consistent with the weapon recovered.",
        "court": "Punjab and Haryana High Court",
        "year": 2023,
        "ipc_sections": "307,326,504,506",
        "crpc_sections": "154,27,161",
        "constitutional_articles": "21",
        "judgment_outcome": "Convicted"
    },
    {
        "case_id": "NV-2024-015",
        "case_title": "Green Earth Foundation v. State of Kerala",
        "case_text": "A PIL challenging illegal quarrying in Western Ghats ecologically sensitive zone. "
                     "The petitioner presented satellite imagery showing extensive environmental damage. "
                     "Article 48A duty of state to protect environment and Article 51A(g) fundamental "
                     "duty to protect forests were invoked. The court examined the Environment Protection "
                     "Act 1986 and Kerala Minor Mineral Concession Rules. Scientific expert testimony "
                     "on biodiversity loss was presented.",
        "court": "Kerala High Court",
        "year": 2022,
        "ipc_sections": "",
        "crpc_sections": "",
        "constitutional_articles": "14,21,48A,51A",
        "judgment_outcome": "Quarrying Banned"
    },
    {
        "case_id": "NV-2024-016",
        "case_title": "State v. Sanjay Mishra",
        "case_text": "The accused Sanjay Mishra was charged under IPC 420 cheating, IPC 468 forgery "
                     "for purpose of cheating, and IPC 471 using forged documents. The accused created "
                     "fake educational certificates to secure a government job. The investigation revealed "
                     "that the accused had submitted forged marksheets of a university. Document examination "
                     "expert confirmed the forgery. CrPC 91 was used to obtain documents from the university.",
        "court": "Chhattisgarh High Court",
        "year": 2023,
        "ipc_sections": "420,468,471",
        "crpc_sections": "91,154,161",
        "constitutional_articles": "",
        "judgment_outcome": "Convicted"
    },
    {
        "case_id": "NV-2024-017",
        "case_title": "Fatima Begum v. State of Telangana",
        "case_text": "A petition challenging triple talaq pronounced through WhatsApp. The petitioner "
                     "argued violation of Article 14 equality before law and Article 15 prohibition of "
                     "discrimination on grounds of religion and gender. The Supreme Court's Shayara Bano "
                     "judgment declaring triple talaq unconstitutional was cited. The respondent husband "
                     "argued personal law exception. Article 25 freedom of religion was examined against "
                     "Article 14 and 21.",
        "court": "Telangana High Court",
        "year": 2023,
        "ipc_sections": "",
        "crpc_sections": "",
        "constitutional_articles": "14,15,21,25",
        "judgment_outcome": "Petition Allowed"
    },
    {
        "case_id": "NV-2024-018",
        "case_title": "State v. Ravi Shankar & Others",
        "case_text": "The accused Ravi Shankar along with co-accused were charged under IPC 147 rioting, "
                     "IPC 148 rioting armed with deadly weapon, IPC 302 murder read with IPC 149 unlawful "
                     "assembly. A mob attacked members of another community during a festival dispute. "
                     "Two persons were killed and ten injured. CrPC 144 prohibitory orders were in force. "
                     "FIR under CrPC 154 was registered. Article 21 and Article 25 were examined.",
        "court": "Allahabad High Court",
        "year": 2022,
        "ipc_sections": "147,148,149,302,324",
        "crpc_sections": "144,154,161",
        "constitutional_articles": "21,25",
        "judgment_outcome": "Partially Convicted"
    },
    {
        "case_id": "NV-2024-019",
        "case_title": "Digital Rights Foundation v. Union of India",
        "case_text": "A challenge to the Information Technology (Intermediary Guidelines) Rules 2021. "
                     "The petitioner argued that mandatory traceability requirements violate Article 19(1)(a) "
                     "freedom of speech, Article 21 right to privacy, and create a chilling effect on free "
                     "expression. The government defended the rules citing Article 19(2) reasonable "
                     "restrictions for sovereignty, security, and public order. Proportionality analysis "
                     "was conducted by the court.",
        "court": "Supreme Court of India",
        "year": 2023,
        "ipc_sections": "",
        "crpc_sections": "",
        "constitutional_articles": "14,19,21",
        "judgment_outcome": "Partially Struck Down"
    },
    {
        "case_id": "NV-2024-020",
        "case_title": "State v. Bhupendra Yadav",
        "case_text": "The accused Bhupendra Yadav, a police officer, was charged under IPC 330 "
                     "voluntarily causing hurt to extort confession and IPC 348 wrongful confinement "
                     "to extort confession. The accused tortured a suspect in custody leading to injuries. "
                     "Medical evidence of custodial torture was presented. Article 20(3) protection against "
                     "self-incrimination and Article 21 were invoked. The DK Basu guidelines on custodial "
                     "rights were cited. CrPC 176 magistrate inquiry into custodial death was relevant.",
        "court": "Rajasthan High Court",
        "year": 2023,
        "ipc_sections": "330,348,342,323",
        "crpc_sections": "154,176",
        "constitutional_articles": "20,21,22",
        "judgment_outcome": "Convicted"
    },
    {
        "case_id": "NV-2024-021",
        "case_title": "Sarita Bai v. Rajendra Prasad",
        "case_text": "A family dispute regarding maintenance under CrPC 125. The wife Sarita Bai claimed "
                     "maintenance after desertion by husband Rajendra Prasad. Evidence showed the husband "
                     "had substantial income from agriculture and business. The wife had no independent "
                     "means of livelihood. Article 15 and Article 21 right to live with dignity were cited. "
                     "The court examined the Hindu Marriage Act provisions and quantum of maintenance.",
        "court": "Madhya Pradesh High Court",
        "year": 2022,
        "ipc_sections": "",
        "crpc_sections": "125",
        "constitutional_articles": "15,21",
        "judgment_outcome": "Maintenance Granted"
    },
    {
        "case_id": "NV-2024-022",
        "case_title": "State v. Amit Kapoor",
        "case_text": "The accused Amit Kapoor was charged under IPC 354 assault or criminal force "
                     "on woman with intent to outrage her modesty and IPC 509 word, gesture or act "
                     "intended to insult modesty. The accused, a senior manager, sexually harassed "
                     "a female employee at the workplace. Complaints were lodged under the POSH Act. "
                     "Internal complaints committee found the accused guilty. CCTV and email evidence "
                     "was presented. CrPC 154 FIR was registered.",
        "court": "Delhi High Court",
        "year": 2023,
        "ipc_sections": "354,354A,509",
        "crpc_sections": "154,161",
        "constitutional_articles": "14,15,21",
        "judgment_outcome": "Convicted"
    },
    {
        "case_id": "NV-2024-023",
        "case_title": "Tribals Welfare Society v. State of Jharkhand",
        "case_text": "A PIL challenging displacement of tribal communities for a mining project "
                     "without obtaining consent under the Forest Rights Act 2006. The petitioners "
                     "argued violation of Article 14, Article 19(1)(e) right to reside, Article 21, "
                     "and Fifth Schedule protections for scheduled areas. The state argued economic "
                     "development and national interest. GRAM SABHA consent was not obtained. "
                     "Environmental clearance was challenged.",
        "court": "Jharkhand High Court",
        "year": 2022,
        "ipc_sections": "",
        "crpc_sections": "",
        "constitutional_articles": "14,19,21,244",
        "judgment_outcome": "Displacement Stayed"
    },
    {
        "case_id": "NV-2024-024",
        "case_title": "State v. Naveen Joshi",
        "case_text": "The accused Naveen Joshi was charged under IPC 304 culpable homicide not "
                     "amounting to murder. The accused, a doctor, was charged with medical negligence "
                     "causing the death of a patient during surgery. Expert medical testimony presented "
                     "conflicting opinions on standard of care. The Indian Medical Council guidelines "
                     "were examined. CrPC 174 inquest was conducted. The Bolam test for medical "
                     "negligence was applied. Article 21 right to health was discussed.",
        "court": "Uttarakhand High Court",
        "year": 2023,
        "ipc_sections": "304,304A,338",
        "crpc_sections": "174,154",
        "constitutional_articles": "21",
        "judgment_outcome": "Acquitted"
    },
    {
        "case_id": "NV-2024-025",
        "case_title": "Ram Lakhan v. State of Uttar Pradesh",
        "case_text": "The accused Ram Lakhan was charged under IPC 302 for murder arising out of "
                     "a long-standing family property dispute. The victim was the accused's cousin. "
                     "The prosecution presented circumstantial evidence including last seen theory, "
                     "recovery of weapon under CrPC 27, and motive through property documents. "
                     "The defense argued right of private defense under IPC 96 to IPC 106. "
                     "Multiple witnesses turned hostile during trial.",
        "court": "Allahabad High Court",
        "year": 2023,
        "ipc_sections": "302,34,201",
        "crpc_sections": "27,154,161",
        "constitutional_articles": "21",
        "judgment_outcome": "Convicted"
    },
    {
        "case_id": "NV-2024-026",
        "case_title": "Digital Privacy Alliance v. State of Maharashtra",
        "case_text": "The petitioner challenged mass surveillance through facial recognition technology "
                     "deployed by Mumbai police without legislative framework. Article 21 right to privacy "
                     "as per Puttaswamy judgment was cited. The petitioner argued absence of data protection "
                     "law makes such surveillance unconstitutional. Article 14 arbitrariness argument was "
                     "also raised. The state argued prevention of crime and Section 144 CrPC public order.",
        "court": "Bombay High Court",
        "year": 2023,
        "ipc_sections": "",
        "crpc_sections": "144",
        "constitutional_articles": "14,19,21",
        "judgment_outcome": "Notice Issued"
    },
    {
        "case_id": "NV-2024-027",
        "case_title": "State v. Prakash Mehta",
        "case_text": "The accused Prakash Mehta was charged under IPC 420 cheating and IPC 406 "
                     "criminal breach of trust for a real estate fraud. The accused collected advance "
                     "payments from 500 home buyers but failed to deliver possession for 8 years. "
                     "RERA provisions were also invoked. The total amount involved was Rs 300 crore. "
                     "CrPC 91 was used to seize financial records. The accused's properties were "
                     "attached under CrPC 83. Article 21 right to shelter was cited by victims.",
        "court": "Gujarat High Court",
        "year": 2022,
        "ipc_sections": "420,406,467,471",
        "crpc_sections": "91,83,154",
        "constitutional_articles": "21",
        "judgment_outcome": "Convicted"
    },
    {
        "case_id": "NV-2024-028",
        "case_title": "Student Federation v. UGC",
        "case_text": "A petition challenging the UGC regulation mandating minimum attendance for "
                     "university examinations. The petitioners argued violation of Article 14 equality "
                     "and Article 21 right to education. Students with disabilities were disproportionately "
                     "affected. Article 15(4) special provisions for socially and educationally backward "
                     "classes were invoked. The Rights of Persons with Disabilities Act 2016 was cited. "
                     "The court examined reasonableness of the attendance criteria.",
        "court": "Supreme Court of India",
        "year": 2023,
        "ipc_sections": "",
        "crpc_sections": "",
        "constitutional_articles": "14,15,21,21A",
        "judgment_outcome": "Regulation Modified"
    },
    {
        "case_id": "NV-2024-029",
        "case_title": "State v. Dinesh Gupta",
        "case_text": "The accused Dinesh Gupta was charged under IPC 363 kidnapping and IPC 364A "
                     "kidnapping for ransom. A 12-year-old child was abducted from school and ransom "
                     "of Rs 1 crore was demanded. The accused was traced through mobile tower location "
                     "data and call records. The child was rescued by police within 48 hours. "
                     "CrPC 154 FIR was lodged. Statement of child under CrPC 164 was recorded. "
                     "Article 21 and Article 39(f) protection of children were cited.",
        "court": "Delhi High Court",
        "year": 2022,
        "ipc_sections": "363,364A,387",
        "crpc_sections": "154,164,161",
        "constitutional_articles": "21,39",
        "judgment_outcome": "Convicted"
    },
    {
        "case_id": "NV-2024-030",
        "case_title": "Farmers Cooperative v. State of Punjab",
        "case_text": "A PIL challenging the acquisition of fertile agricultural land for an industrial "
                     "corridor without adequate compensation under the Right to Fair Compensation Act 2013. "
                     "The petitioners argued violation of Article 300A right to property, Article 14 "
                     "equality, and Article 21 right to livelihood. Social impact assessment was not "
                     "conducted as per the Act. The court examined whether the acquisition served "
                     "public purpose and whether consent of landowners was obtained.",
        "court": "Punjab and Haryana High Court",
        "year": 2023,
        "ipc_sections": "",
        "crpc_sections": "",
        "constitutional_articles": "14,21,300A",
        "judgment_outcome": "Acquisition Stayed"
    },
]

def generate_dataset():
    """Generate and save the sample dataset as CSV."""
    df = pd.DataFrame(cases)
    
    # Ensure data directory exists
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, "judgments.csv")
    
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"✅ Generated {len(df)} sample cases → {output_path}")
    print(f"   Columns: {list(df.columns)}")
    print(f"   Courts: {df['court'].nunique()} unique courts")
    print(f"   Years: {df['year'].min()} - {df['year'].max()}")
    return df

if __name__ == "__main__":
    generate_dataset()
