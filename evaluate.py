#!/usr/bin/env python3
"""
Government Site Evaluator — North Macedonia & Netherlands
Checks: load time, SSL cert validity, CMS detection + version, robots.txt,
sitemap.xml, and llms.txt
"""

import json
import time
import ssl
import socket
import datetime
import re
import sys
import urllib.request
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── Sites ─────────────────────────────────────────────────────────────────────
WEBSITES_MK = [
    # ── Core government ───────────────────────────────────────────────────────
    {"name": "Government of North Macedonia",           "url": "https://vlada.mk"},
    {"name": "Assembly of North Macedonia",             "url": "https://sobranie.mk"},
    {"name": "President of North Macedonia",            "url": "https://president.gov.mk"},

    # ── Ministries ────────────────────────────────────────────────────────────
    {"name": "Ministry of Foreign Affairs",             "url": "https://mfa.gov.mk"},
    {"name": "Ministry of Finance",                     "url": "https://finance.gov.mk"},
    {"name": "Ministry of Interior",                    "url": "https://mvr.gov.mk"},
    {"name": "Ministry of Defence",                     "url": "https://mod.gov.mk"},
    {"name": "Ministry of Justice",                     "url": "https://pravda.gov.mk"},
    {"name": "Ministry of Education & Science",         "url": "https://mon.gov.mk"},
    {"name": "Ministry of Health",                      "url": "https://zdravstvo.gov.mk"},
    {"name": "Ministry of Economy & Labor",             "url": "https://economy.gov.mk"},
    {"name": "Ministry of Transport & Communication",   "url": "https://mtc.gov.mk"},
    {"name": "Ministry of Agriculture",                 "url": "https://mzsv.gov.mk"},
    {"name": "Ministry of Environment",                 "url": "https://moepp.gov.mk"},
    {"name": "Ministry of Local Self-Government",       "url": "https://mls.gov.mk"},
    {"name": "Ministry of Digital Transformation",      "url": "https://mdt.gov.mk"},
    {"name": "Ministry of Social Policy",               "url": "https://mtsp.gov.mk"},
    {"name": "Ministry of Culture",                     "url": "https://kultura.gov.mk"},
    {"name": "Secretariat for European Affairs",        "url": "https://sep.gov.mk"},

    # ── Courts & constitutional bodies ────────────────────────────────────────
    {"name": "Constitutional Court",                    "url": "https://ustavensud.mk"},
    {"name": "Supreme Court",                           "url": "https://vsrm.mk"},
    {"name": "Judicial Council",                        "url": "https://ssrm.mk"},
    {"name": "Administrative Court",                    "url": "https://us.mk"},
    {"name": "Public Prosecutor's Office",              "url": "https://jorm.org.mk"},
    {"name": "State Procuratorate",                     "url": "https://drzavnopravobranitelstvo.gov.mk"},

    # ── Independent oversight bodies ──────────────────────────────────────────
    {"name": "Ombudsman",                               "url": "https://ombudsman.mk"},
    {"name": "State Election Commission",               "url": "https://dik.mk"},
    {"name": "Anti-Corruption Commission (DKSK)",       "url": "https://dksk.mk"},
    {"name": "State Audit Office",                      "url": "https://dzr.gov.mk"},
    {"name": "Personal Data Protection Directorate",    "url": "https://dzlp.mk"},
    {"name": "Committee for Free Access to Info",       "url": "https://komspi.mk"},
    {"name": "Inspectorate Council",                    "url": "https://is.gov.mk"},
    {"name": "Intelligence Agency",                     "url": "https://ia.gov.mk"},
    {"name": "Directorate for Security (DBKI)",         "url": "https://dbki.gov.mk"},

    # ── Regulatory & government agencies ──────────────────────────────────────
    {"name": "Public Revenue Office",                   "url": "https://ujp.gov.mk"},
    {"name": "Customs Administration",                  "url": "https://customs.gov.mk"},
    {"name": "State Statistical Office",                "url": "https://stat.gov.mk"},
    {"name": "National Bank (NBRM)",                    "url": "https://nbrm.mk"},
    {"name": "Central Register",                        "url": "https://crm.com.mk"},
    {"name": "Securities and Exchange Commission",      "url": "https://sec.gov.mk"},
    {"name": "Employment Service Agency",               "url": "https://av.gov.mk"},
    {"name": "Geodetic Authority (Cadastre)",           "url": "https://katastar.gov.mk"},
    {"name": "Administration Agency",                   "url": "https://ads.gov.mk"},
    {"name": "State Archives",                          "url": "https://arhiv.gov.mk"},
    {"name": "Crisis Management Centre",                "url": "https://cuk.gov.mk"},
    {"name": "Agency of Youth and Sport",               "url": "https://ams.gov.mk"},
    {"name": "Agency for Audio & Audiovisual (AVMU)",   "url": "https://avmu.mk"},
    {"name": "Regulatory Commission Energy (RKE)",      "url": "https://rke.mk"},
    {"name": "Electronic Communications Agency (AEK)",  "url": "https://aek.mk"},
    {"name": "Drug Agency (MALMED)",                    "url": "https://malmed.gov.mk"},
    {"name": "Food Safety Agency",                      "url": "https://afs.gov.mk"},
    {"name": "Health Insurance Fund (FZO)",             "url": "https://fzo.org.mk"},
    {"name": "Pension & Disability Fund (PIOM)",        "url": "https://piom.mk"},
    {"name": "Development Bank (MBDP)",                 "url": "https://mbdp.com.mk"},
    {"name": "Invest North Macedonia",                  "url": "https://investnorthmacedonia.gov.mk"},
    {"name": "Macedonian Information Agency (MIA)",     "url": "https://mia.mk"},
    {"name": "Macedonian Academy of Sciences (MANU)",   "url": "https://manu.edu.mk"},
    {"name": "Post of North Macedonia",                 "url": "https://posta.com.mk"},
    {"name": "Macedonian Railways (MZ)",                "url": "https://mz.com.mk"},
    {"name": "Macedonian Power Plants (ESM)",           "url": "https://esm.com.mk"},
    {"name": "Macedonian Telecom",                      "url": "https://telekom.mk"},

    # ── City of Skopje & its 10 municipalities ────────────────────────────────
    {"name": "City of Skopje",                          "url": "https://skopje.gov.mk"},
    {"name": "Municipality of Aerodrom",                "url": "https://aerodrom.gov.mk"},
    {"name": "Municipality of Butel",                   "url": "https://butel.gov.mk"},
    {"name": "Municipality of Čair",                    "url": "https://chair.gov.mk"},
    {"name": "Municipality of Centar",                  "url": "https://centar.gov.mk"},
    {"name": "Municipality of Gazi Baba",               "url": "https://gazibaba.gov.mk"},
    {"name": "Municipality of Gjorče Petrov",           "url": "https://gjorcepetrov.gov.mk"},
    {"name": "Municipality of Karpoš",                  "url": "https://karpos.gov.mk"},
    {"name": "Municipality of Kisela Voda",             "url": "https://kiselavoda.gov.mk"},
    {"name": "Municipality of Saraj",                   "url": "https://saraj.gov.mk"},
    {"name": "Municipality of Šuto Orizari",            "url": "https://sutoorizari.gov.mk"},

    # ── Municipalities — Eastern region ───────────────────────────────────────
    {"name": "Municipality of Berovo",                  "url": "https://berovo.gov.mk"},
    {"name": "Municipality of Češinovo-Obleševo",       "url": "https://cesinovo-oblesevo.gov.mk"},
    {"name": "Municipality of Delčevo",                 "url": "https://delcevo.gov.mk"},
    {"name": "Municipality of Karbinci",                "url": "https://karbinci.gov.mk"},
    {"name": "Municipality of Kočani",                  "url": "https://kocani.gov.mk"},
    {"name": "Municipality of Makedonska Kamenica",     "url": "https://makedonskakamenica.gov.mk"},
    {"name": "Municipality of Pehčevo",                 "url": "https://pehcevo.gov.mk"},
    {"name": "Municipality of Probištip",               "url": "https://probistip.gov.mk"},
    {"name": "Municipality of Štip",                    "url": "https://stip.gov.mk"},
    {"name": "Municipality of Vinica",                  "url": "https://vinica.gov.mk"},
    {"name": "Municipality of Zrnovci",                 "url": "https://zrnovci.gov.mk"},

    # ── Municipalities — Northeastern region ──────────────────────────────────
    {"name": "Municipality of Kratovo",                 "url": "https://kratovo.gov.mk"},
    {"name": "Municipality of Kriva Palanka",           "url": "https://krivapalanka.gov.mk"},
    {"name": "Municipality of Kumanovo",                "url": "https://kumanovo.gov.mk"},
    {"name": "Municipality of Lipkovo",                 "url": "https://lipkovo.gov.mk"},
    {"name": "Municipality of Rankovce",                "url": "https://rankovce.gov.mk"},
    {"name": "Municipality of Staro Nagoričane",        "url": "https://staronagoricane.gov.mk"},

    # ── Municipalities — Pelagonia region ─────────────────────────────────────
    {"name": "Municipality of Bitola",                  "url": "https://bitola.gov.mk"},
    {"name": "Municipality of Demir Hisar",             "url": "https://demirhistar.gov.mk"},
    {"name": "Municipality of Dolneni",                 "url": "https://dolneni.gov.mk"},
    {"name": "Municipality of Krivogaštani",            "url": "https://krivogastani.gov.mk"},
    {"name": "Municipality of Kruševo",                 "url": "https://krusevo.gov.mk"},
    {"name": "Municipality of Mogila",                  "url": "https://mogila.gov.mk"},
    {"name": "Municipality of Novaci",                  "url": "https://novaci.gov.mk"},
    {"name": "Municipality of Prilep",                  "url": "https://prilep.gov.mk"},
    {"name": "Municipality of Resen",                   "url": "https://resen.gov.mk"},

    # ── Municipalities — Polog region ─────────────────────────────────────────
    {"name": "Municipality of Bogovinje",               "url": "https://bogovinje.gov.mk"},
    {"name": "Municipality of Brvenica",                "url": "https://brvenica.gov.mk"},
    {"name": "Municipality of Gostivar",                "url": "https://gostivari.gov.mk"},
    {"name": "Municipality of Jegunovce",               "url": "https://jegunovce.gov.mk"},
    {"name": "Municipality of Mavrovo i Rostuša",       "url": "https://mavrovirostu-sa.gov.mk"},
    {"name": "Municipality of Tearce",                  "url": "https://tearce.gov.mk"},
    {"name": "Municipality of Tetovo",                  "url": "https://tetovo.gov.mk"},
    {"name": "Municipality of Vrapčište",               "url": "https://vrapciste.gov.mk"},
    {"name": "Municipality of Želino",                  "url": "https://zhelina.gov.mk"},

    # ── Municipalities — Skopje region (non-city) ─────────────────────────────
    {"name": "Municipality of Aračinovo",               "url": "https://aracinovo.gov.mk"},
    {"name": "Municipality of Čučer-Sandevo",           "url": "https://cucer-sandevo.gov.mk"},
    {"name": "Municipality of Ilinden",                 "url": "https://ilinden.gov.mk"},
    {"name": "Municipality of Petrovec",                "url": "https://petrovec.gov.mk"},
    {"name": "Municipality of Sopište",                 "url": "https://sopiste.gov.mk"},
    {"name": "Municipality of Studeničani",             "url": "https://studenicani.gov.mk"},
    {"name": "Municipality of Zelenikovo",              "url": "https://zelenikovo.gov.mk"},

    # ── Municipalities — Southeastern region ──────────────────────────────────
    {"name": "Municipality of Bogdanci",                "url": "https://bogdanci.gov.mk"},
    {"name": "Municipality of Bosilovo",                "url": "https://bosilovo.gov.mk"},
    {"name": "Municipality of Gevgelija",               "url": "https://gevgelija.gov.mk"},
    {"name": "Municipality of Dojran",                  "url": "https://dojran.gov.mk"},
    {"name": "Municipality of Konče",                   "url": "https://konce.gov.mk"},
    {"name": "Municipality of Novo Selo",               "url": "https://novoselo.gov.mk"},
    {"name": "Municipality of Radoviš",                 "url": "https://radovis.gov.mk"},
    {"name": "Municipality of Strumica",                "url": "https://strumica.gov.mk"},
    {"name": "Municipality of Valandovo",               "url": "https://valandovo.gov.mk"},
    {"name": "Municipality of Vasilevo",                "url": "https://vasilevo.gov.mk"},

    # ── Municipalities — Southwestern region ──────────────────────────────────
    {"name": "Municipality of Centar Župa",             "url": "https://centarzupa.gov.mk"},
    {"name": "Municipality of Debar",                   "url": "https://debar.gov.mk"},
    {"name": "Municipality of Debarca",                 "url": "https://debarca.gov.mk"},
    {"name": "Municipality of Kičevo",                  "url": "https://kicevo.gov.mk"},
    {"name": "Municipality of Makedonski Brod",         "url": "https://makedonskibrod.gov.mk"},
    {"name": "Municipality of Ohrid",                   "url": "https://ohrid.gov.mk"},
    {"name": "Municipality of Plasnica",                "url": "https://plasnica.gov.mk"},
    {"name": "Municipality of Struga",                  "url": "https://struga.gov.mk"},
    {"name": "Municipality of Vevčani",                 "url": "https://vevcani.gov.mk"},

    # ── Municipalities — Vardar region ────────────────────────────────────────
    {"name": "Municipality of Čaška",                   "url": "https://caska.gov.mk"},
    {"name": "Municipality of Demir Kapija",            "url": "https://demirkapija.gov.mk"},
    {"name": "Municipality of Gradsko",                 "url": "https://gradsko.gov.mk"},
    {"name": "Municipality of Kavadarci",               "url": "https://kavadarci.gov.mk"},
    {"name": "Municipality of Lozovo",                  "url": "https://lozovo.gov.mk"},
    {"name": "Municipality of Negotino",                "url": "https://negotino.gov.mk"},
    {"name": "Municipality of Rosoman",                 "url": "https://rosoman.gov.mk"},
    {"name": "Municipality of Sveti Nikole",            "url": "https://svetinikole.gov.mk"},
    {"name": "Municipality of Veles",                   "url": "https://veles.gov.mk"},

    # ── Additional municipalities (alt/confirmed domains) ─────────────────────
    {"name": "Municipality of Čair",                    "url": "https://cair.gov.mk"},
    {"name": "Municipality of Čučer-Sandevo",           "url": "https://cucersandevo.gov.mk"},
    {"name": "Municipality of Debarca",                 "url": "https://debrca.gov.mk"},
    {"name": "Municipality of Demir Hisar",             "url": "https://demirhisar.gov.mk"},
    {"name": "Municipality of Debar (Albanian domain)", "url": "https://dibra.gov.mk"},
    {"name": "Municipality of Bosilovo",                "url": "https://opstinabosilovo.gov.mk"},
    {"name": "Municipality of Butel (alt domain)",      "url": "https://opstinabutel.gov.mk"},
    {"name": "Municipality of Dolneni",                 "url": "https://opstinadolneni.gov.mk"},
    {"name": "Municipality of Gjorče Petrov",           "url": "https://opstinagpetrov.gov.mk"},
    {"name": "Municipality of Jegunovce",               "url": "https://opstinajegunovce.gov.mk"},
    {"name": "Municipality of Kratovo (alt domain)",    "url": "https://opstinakratovo.gov.mk"},
    {"name": "Municipality of Novaci",                  "url": "https://opstinanovic.gov.mk"},
    {"name": "Municipality of Rosoman",                 "url": "https://opstinarosoman.gov.mk"},
    {"name": "Municipality of Sopište (alt domain)",    "url": "https://opstinasopiste.gov.mk"},
    {"name": "Municipality of Vasilevo (alt domain)",   "url": "https://opstinavasilevo.gov.mk"},
    {"name": "Municipality of Aračinovo (Albanian)",    "url": "https://www.haracina.gov.mk"},
    {"name": "Municipality of Tetovo (alt domain)",     "url": "https://www.tetova.gov.mk"},
    {"name": "Municipality of Makedonski Brod (alt)",   "url": "https://www.mbrod.gov.mk"},
    {"name": "Gazi Baba Business Portal",               "url": "https://business.gazibaba.gov.mk"},
    {"name": "Communal Services Gostivar",              "url": "https://komunalecgostivar.gov.mk"},
    {"name": "Kisela Voda (alt domain)",                "url": "https://opstinakiselavoda.gov.mk"},

    # ── Additional government portals & services ──────────────────────────────
    {"name": "President (alt domain)",                  "url": "https://pretsedatel.mk"},
    {"name": "Government Contact Portal",               "url": "https://contact.vlada.mk"},
    {"name": "Government e-Services Portal",            "url": "https://uslugi.gov.mk"},
    {"name": "e-Procurement Portal",                    "url": "https://e-nabavki.gov.mk"},
    {"name": "Voter Register Portal",                   "url": "https://izbirackispisok.gov.mk"},
    {"name": "Official Gazette",                        "url": "https://www.slvesnik.com.mk"},
    {"name": "Legal Database (Justice Ministry)",       "url": "https://ldbis.pravda.gov.mk"},
    {"name": "TrustedID Portal",                        "url": "https://trusteid.mdt.gov.mk"},
    {"name": "1000 Books Programme (Education)",        "url": "https://www.1000knigi.mon.gov.mk"},

    # ── Additional agencies & directorates ────────────────────────────────────
    {"name": "Special Prosecution Office (SPO)",        "url": "https://sjorm.gov.mk"},
    {"name": "Public Prosecutor's Office (gov domain)", "url": "https://jorm.gov.mk"},
    {"name": "Financial Police",                        "url": "https://finpol.gov.mk"},
    {"name": "Directorate for e-Government",            "url": "https://digu.gov.mk"},
    {"name": "Directorate for ICT",                     "url": "https://dils.gov.mk"},
    {"name": "Directorate for Internal Supervision",    "url": "https://disl.gov.mk"},
    {"name": "Directorate for Infra & Technologies",    "url": "https://dit.gov.mk"},
    {"name": "Directorate for Protection & Rescue",     "url": "https://dip.gov.mk"},
    {"name": "Directorate for Protection & Rescue (2)", "url": "https://dzs.gov.mk"},
    {"name": "State Social Protection Institute",       "url": "https://dszi.gov.mk"},
    {"name": "Council for Civil Servant Oversight",     "url": "https://cov.gov.mk"},
    {"name": "Energy Regulatory Commission",            "url": "https://ener.gov.mk"},
    {"name": "Energy Agency",                           "url": "https://www.ea.gov.mk"},
    {"name": "Free Economic Zones Directorate",         "url": "https://fez.gov.mk"},
    {"name": "Veterinary Agency",                       "url": "https://fva.gov.mk"},
    {"name": "Veterinary e-Portal",                     "url": "https://e-portal.uvmk.gov.mk"},
    {"name": "Food Safety Agency (alt)",                "url": "https://iarm.gov.mk"},
    {"name": "IPARD (EU Rural Development)",            "url": "https://ipard.gov.mk"},
    {"name": "IPARD Paying Agency",                     "url": "https://www.bjn.gov.mk"},
    {"name": "Bureau for Regional Development",         "url": "https://biroescp.gov.mk"},
    {"name": "Development & Investment Agency",         "url": "https://www.adi.gov.mk"},
    {"name": "Public Administration Academy",           "url": "https://jpacademy.gov.mk"},
    {"name": "Institute for Standardization",           "url": "https://isrsm.gov.mk"},
    {"name": "Hydrometeorological Service",             "url": "https://uhmr.gov.mk"},
    {"name": "Intellectual Property Office",            "url": "https://www.ippo.gov.mk"},
    {"name": "Office for Cultural Heritage",            "url": "https://uzkn.gov.mk"},
    {"name": "Office for Victims of Persecution",       "url": "https://ovp.gov.mk"},
    {"name": "Agency for Seized Assets",                "url": "https://akazum.gov.mk"},
    {"name": "Agency for Seized Property (alt)",        "url": "https://odzemenimot.gov.mk"},
    {"name": "Agency for Supervision of Pension Funds", "url": "https://www.mapas.gov.mk"},
    {"name": "Commission for Religious Communities",    "url": "https://www.kovz.gov.mk"},
    {"name": "Social Work Centre Skopje",               "url": "https://www.jumcsrskopje.gov.mk"},
    {"name": "Penitentiary Idrizovo",                   "url": "https://www.kpuidrizovo.gov.mk"},
    {"name": "Integrated Pollution Register",           "url": "https://ripz.moepp.gov.mk"},
    {"name": "Finance Ministry EU Funds (CFCD)",        "url": "https://cfcd.finance.gov.mk"},
    {"name": "Public Expenditure Operations",           "url": "https://peo.finance.gov.mk"},
    {"name": "Unit for Financial Reporting",            "url": "https://ufr.gov.mk"},
    {"name": "Health Insurance Registry (ZPIS)",        "url": "https://zpis.gov.mk"},
    {"name": "Macedonian Language Institute",           "url": "https://makedonski.gov.mk"},
    {"name": "NGO Cooperation Portal",                  "url": "https://www.nvosorabotka.gov.mk"},
    {"name": "State Roads Inspectorate Admin",          "url": "https://duinspektorat.mioa.gov.mk"},
    {"name": "Ministry of Sport",                       "url": "https://ms.gov.mk"},
    {"name": "Film Agency",                             "url": "https://filmagency.gov.mk"},
    {"name": "National Film Fund",                      "url": "https://filmfund.gov.mk"},
    {"name": "Cultural Information Centre",             "url": "https://www.kic.com.mk"},
    {"name": "National Gallery of North Macedonia",     "url": "https://nationalgallery.mk"},
    {"name": "National Library Ohrid",                  "url": "https://bibliotekaohrid.mk"},

    # ── State-backed enterprises & public bodies ──────────────────────────────
    {"name": "Army of North Macedonia",                 "url": "https://mil.mk"},
    {"name": "Macedonian Radio-Television (MRT)",       "url": "https://mrt.com.mk"},
    {"name": "Public Enterprise for State Roads",       "url": "https://roads.org.mk"},
    {"name": "Electronic Toll Collection",              "url": "https://etc.roads.org.mk"},
    {"name": "Road Safety Agency",                      "url": "https://rsbsp.org.mk"},
    {"name": "National Tourism Board",                  "url": "https://macedonia-timeless.com"},
    {"name": "Tourism North Macedonia (gov domain)",    "url": "https://tourismmacedonia.gov.mk"},
    {"name": "Accreditation Body (AA)",                 "url": "https://aa.mk"},
    {"name": "Accreditation Applications Portal",       "url": "https://prijava.aa.mk"},
    {"name": "e-Jobs Portal",                           "url": "https://e-rabota.av.gov.mk"},
    {"name": "Cadastre e-Services",                     "url": "https://e-uslugi.katastar.gov.mk"},

    # ── Professional chambers (state-mandated) ────────────────────────────────
    {"name": "Bar Association",                         "url": "https://www.mba.org.mk"},
    {"name": "Notary Chamber",                          "url": "https://www.nkrm.org.mk"},
    {"name": "Chamber of Enforcement Agents",           "url": "https://kirm.mk"},
]

WEBSITES_NL = [
    # Core government portal
    {"name": "Government of the Netherlands",          "url": "https://www.government.nl"},
    {"name": "Rijksoverheid (Dutch portal)",           "url": "https://www.rijksoverheid.nl"},
    {"name": "House of Representatives",               "url": "https://www.tweedekamer.nl"},
    {"name": "Senate",                                 "url": "https://www.eerstekamer.nl"},
    {"name": "Royal House",                            "url": "https://www.royal-house.nl"},
    # Ministries
    {"name": "Ministry of General Affairs",            "url": "https://www.government.nl/ministries/ministry-of-general-affairs"},
    {"name": "Ministry of Foreign Affairs",            "url": "https://www.government.nl/ministries/ministry-of-foreign-affairs"},
    {"name": "Ministry of Finance",                    "url": "https://www.government.nl/ministries/ministry-of-finance"},
    {"name": "Ministry of Interior & Kingdom Relations","url": "https://www.government.nl/ministries/ministry-of-the-interior-and-kingdom-relations"},
    {"name": "Ministry of Justice & Security",         "url": "https://www.government.nl/ministries/ministry-of-justice-and-security"},
    {"name": "Ministry of Defence",                    "url": "https://english.defensie.nl"},
    {"name": "Ministry of Education, Culture & Science","url": "https://www.government.nl/ministries/ministry-of-education-culture-and-science"},
    {"name": "Ministry of Health, Welfare & Sport",    "url": "https://www.government.nl/ministries/ministry-of-health-welfare-and-sport"},
    {"name": "Ministry of Infrastructure & Water",     "url": "https://www.government.nl/ministries/ministry-of-infrastructure-and-water-management"},
    {"name": "Ministry of Economic Affairs",           "url": "https://www.government.nl/ministries/ministry-of-economic-affairs"},
    {"name": "Ministry of Agriculture & Nature",       "url": "https://www.government.nl/ministries/ministry-of-agriculture-nature-and-food-quality"},
    {"name": "Ministry of Social Affairs",             "url": "https://www.government.nl/ministries/ministry-of-social-affairs-and-employment"},
    {"name": "Ministry of Asylum & Migration",         "url": "https://www.government.nl/ministries/ministry-of-asylum-and-migration"},
    {"name": "Ministry of Climate & Green Growth",     "url": "https://www.government.nl/ministries/ministry-of-climate-policy-and-green-growth"},
    {"name": "Ministry of Housing",                    "url": "https://www.government.nl/ministries/ministry-of-housing-and-spatial-planning"},
    # Key agencies
    {"name": "Tax and Customs Administration",         "url": "https://www.belastingdienst.nl"},
    {"name": "Statistics Netherlands (CBS)",           "url": "https://www.cbs.nl"},
    {"name": "Dutch National Bank (DNB)",              "url": "https://www.dnb.nl"},
    {"name": "Netherlands Enterprise Agency (RVO)",    "url": "https://www.rvo.nl"},
    {"name": "Invest in Holland",                      "url": "https://investinholland.com"},
    {"name": "Netherlands Authority Fin. Markets",     "url": "https://www.afm.nl"},
]

# Combined list with country tag
WEBSITES = (
    [dict(country="MK", **s) for s in WEBSITES_MK] +
    [dict(country="NL", **s) for s in WEBSITES_NL]
)

TIMEOUT = 12
REPEAT  = 2

# ── CMS fingerprints ──────────────────────────────────────────────────────────
# Each entry: (cms_name, list_of_header_or_body_patterns)
CMS_SIGNATURES = {
    "WordPress": {
        "body":    [r'/wp-content/', r'/wp-includes/', r'wordpress'],
        "headers": {"x-powered-by": r"wordpress", "link": r'rel="https://api\.w\.org/"'},
        "version": [
            r'<meta name="generator" content="WordPress ([0-9.]+)"',
            r'ver=([0-9]+\.[0-9]+(?:\.[0-9]+)?)',   # fallback from scripts
        ],
    },
    "Drupal": {
        "body":    [r'Drupal\.settings', r'/sites/default/files/', r'drupal'],
        "headers": {"x-generator": r"Drupal", "x-drupal-cache": r""},
        "version": [r'<meta name="generator" content="Drupal ([0-9.]+)"'],
    },
    "Joomla": {
        "body":    [r'/media/jui/', r'joomla'],
        "headers": {"x-content-encoded-by": r"Joomla"},
        "version": [r'<meta name="generator" content="Joomla! - Open Source Content Management" />'],
    },
    "TYPO3": {
        "body":    [r'typo3', r'/typo3/'],
        "headers": {"x-powered-by": r"TYPO3"},
        "version": [r'TYPO3 ([0-9.]+)'],
    },
}

# Latest stable versions (update these as CMS releases happen)
CMS_LATEST = {
    "WordPress": "6.9",
    "Drupal":    "11",
    "Joomla":    "5.3",
    "TYPO3":     "13",
}

# ─────────────────────────────────────────────────────────────────────────────

def make_request(url, timeout=TIMEOUT):
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; GovSiteEvaluator/1.0)",
        "Accept": "text/html,application/xhtml+xml,*/*",
    })
    t0 = time.perf_counter()
    with urlopen(req, timeout=timeout) as resp:
        t1 = time.perf_counter()
        body = resp.read(500_000)   # cap at 500 KB
    return resp, body, (t1 - t0) * 1000


def check_ssl(hostname: str, port: int = 443) -> dict:
    result = {"valid": False, "expires": None, "days_left": None, "issuer": None, "error": None}
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.create_connection((hostname, port), timeout=10),
                             server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            not_after = cert.get("notAfter", "")
            exp = datetime.datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
            now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            days_left = (exp - now).days
            issuer = dict(x[0] for x in cert.get("issuer", []))
            result.update({
                "valid":     days_left > 0,
                "expires":   exp.strftime("%Y-%m-%d"),
                "days_left": days_left,
                "issuer":    issuer.get("organizationName", issuer.get("commonName", "Unknown")),
            })
    except ssl.SSLCertVerificationError as e:
        result["error"] = f"Invalid cert: {e}"
    except Exception as e:
        result["error"] = str(e)
    return result


def detect_cms(body_str: str, headers: dict) -> dict:
    body_lower = body_str.lower()
    for cms, sigs in CMS_SIGNATURES.items():
        matched = False
        # body patterns
        for pat in sigs.get("body", []):
            if re.search(pat, body_lower):
                matched = True
                break
        # header patterns
        if not matched:
            for hdr, pat in sigs.get("headers", {}).items():
                val = headers.get(hdr, "")
                if pat == "" and val:
                    matched = True
                    break
                if pat and re.search(pat, val, re.I):
                    matched = True
                    break
        if matched:
            # try to extract version
            version = None
            for vpat in sigs.get("version", []):
                m = re.search(vpat, body_str, re.I)
                if m:
                    version = m.group(1)
                    break
            latest   = CMS_LATEST.get(cms)
            outdated = None
            if version and latest:
                # compare major versions only for robustness
                try:
                    v_major = int(version.split(".")[0])
                    l_major = int(latest.split(".")[0])
                    outdated = v_major < l_major
                except Exception:
                    outdated = None
            return {"cms": cms, "version": version, "latest": latest, "outdated": outdated}
    return {"cms": None, "version": None, "latest": None, "outdated": None}


def check_url_exists(base_url: str, path: str) -> bool:
    url = base_url.rstrip("/") + path
    try:
        req = Request(url, headers={"User-Agent": "GovSiteEvaluator/1.0"})
        with urlopen(req, timeout=8) as resp:
            return resp.status < 400
    except Exception:
        return False


def check_site(entry: dict) -> dict:
    url     = entry["url"]
    name    = entry["name"]
    country = entry.get("country", "??")
    parsed   = urlparse(url)
    hostname = parsed.netloc

    result = {
        "name":         name,
        "country":      country,
        "url":          url,
        "hostname":     hostname,
        "timestamp":    datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "up":           False,
        "status_code":  None,
        "avg_load_ms":  None,
        "ssl":          {},
        "cms":          None,
        "cms_version":  None,
        "cms_latest":   None,
        "cms_outdated": None,
        "robots_txt":   False,
        "sitemap_xml":  False,
        "llms_txt":     False,
        "rss_feed":     False,
        "error":        None,
    }

    # ── SSL ──
    result["ssl"] = check_ssl(hostname)

    # ── Load time + body ──
    load_times = []
    body_str   = ""
    resp_headers = {}
    for i in range(REPEAT):
        try:
            resp, body, elapsed = make_request(url)
            load_times.append(elapsed)
            if i == 0:
                result["status_code"] = resp.status
                result["up"]          = 200 <= resp.status < 400
                resp_headers          = dict(resp.headers)
                body_str              = body.decode("utf-8", errors="replace")
        except HTTPError as e:
            result["status_code"] = e.code
            result["up"]          = False
            result["error"]       = f"HTTP {e.code}"
            break
        except Exception as e:
            result["up"]    = False
            result["error"] = str(e)
            break

    if load_times:
        result["avg_load_ms"] = round(sum(load_times) / len(load_times), 1)

    # ── CMS detection ──
    if body_str:
        lower_headers = {k.lower(): v for k, v in resp_headers.items()}
        cms_info = detect_cms(body_str, lower_headers)
        result["cms"]          = cms_info["cms"]
        result["cms_version"]  = cms_info["version"]
        result["cms_latest"]   = cms_info["latest"]
        result["cms_outdated"] = cms_info["outdated"]

    # ── robots.txt / sitemap.xml / llms.txt ──
    result["robots_txt"]  = check_url_exists(url, "/robots.txt")
    result["sitemap_xml"] = check_url_exists(url, "/sitemap.xml")
    result["llms_txt"]    = check_url_exists(url, "/llms.txt")

    # ── RSS feed detection ──
    # 1. Look for <link rel="alternate" type="application/rss+xml"> or atom in body
    rss_found = False
    if body_str:
        if re.search(r'type=["\']application/(rss|atom)\+xml["\']', body_str, re.I):
            rss_found = True
    # 2. Fallback: probe common feed paths
    if not rss_found:
        for feed_path in ("/feed", "/rss", "/feed.xml", "/rss.xml", "/atom.xml",
                          "/feed/rss", "/index.xml", "/en/rss", "/news/feed"):
            if check_url_exists(url, feed_path):
                rss_found = True
                break
    result["rss_feed"] = rss_found

    return result


WORKERS = 10  # concurrent site checks

def main():
    total = len(WEBSITES)
    print(f"[{datetime.datetime.now(datetime.timezone.utc).isoformat()}] "
          f"Evaluating {total} sites (MK + NL) with {WORKERS} workers…\n")

    # Run checks concurrently, preserve original order in output
    results_map = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(check_site, entry): i for i, entry in enumerate(WEBSITES)}
        completed = 0
        for future in as_completed(futures):
            idx = futures[future]
            try:
                r = future.result()
            except Exception as e:
                entry = WEBSITES[idx]
                r = {
                    "name": entry["name"], "country": entry.get("country", "??"),
                    "url": entry["url"], "hostname": urlparse(entry["url"]).netloc,
                    "up": False, "error": str(e),
                    "ssl": {}, "avg_load_ms": None,
                    "cms": None, "cms_version": None, "cms_latest": None, "cms_outdated": None,
                    "robots_txt": False, "sitemap_xml": False,
                    "llms_txt": False, "rss_feed": False,
                    "status_code": None,
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                }
            results_map[idx] = r
            completed += 1
            status  = "✓ UP" if r["up"] else "✗ DOWN"
            ssl_ok  = "🔒" if r["ssl"].get("valid") else "⚠ SSL"
            cms_str = r["cms"] or "?"
            if r.get("cms_version"):
                cms_str += f" {r['cms_version']}"
            if r.get("cms_outdated"):
                cms_str += " [OUTDATED]"
            print(f"  [{completed:>3}/{total}] {r['name'][:45]:<45}  "
                  f"{status}  {ssl_ok}  CMS:{cms_str:<18}  "
                  f"load:{str(r['avg_load_ms'])+'ms':<9}  "
                  f"robots:{'✓' if r['robots_txt'] else '✗'}  "
                  f"sitemap:{'✓' if r['sitemap_xml'] else '✗'}  "
                  f"llms:{'✓' if r['llms_txt'] else '✗'}  "
                  f"rss:{'✓' if r['rss_feed'] else '✗'}",
                  flush=True)

    # Restore original order
    all_results = [results_map[i] for i in range(total)]

    output = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "site_count":   len(all_results),
        "results":      all_results,
    }
    with open("results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults written to results.json")
    if any(not r["up"] for r in all_results):
        sys.exit(1)


if __name__ == "__main__":
    main()
