"""Turn raw model labels (e.g. ``Tomato__late_blight``) into human-friendly
crop / condition names plus practical care guidance for the UI."""

import re

# Dataset typos / odd spellings -> clean display names.
CROP_FIXES = {
    "Gauva": "Guava",
    "Pepper_bell": "Bell Pepper",
}

# Keyword -> care guidance. Matched against the condition text (longest match
# wins) so we can give useful advice for all 89 classes without enumerating
# each one. Each entry: short description + a few actionable tips.
CONDITION_GUIDE = [
    ("healthy", {
        "kind": "healthy",
        "summary": "No disease detected. The leaf looks healthy.",
        "tips": [
            "Keep up your current watering and light routine.",
            "Inspect new growth weekly to catch problems early.",
            "Ensure good airflow between plants to prevent fungal issues.",
        ],
    }),
    ("late_blight", {
        "kind": "disease",
        "summary": "A fast-spreading fungal-like disease that thrives in cool, wet weather.",
        "tips": [
            "Remove and destroy infected leaves immediately — do not compost.",
            "Avoid overhead watering; keep foliage dry.",
            "Apply a copper-based or appropriate fungicide preventively.",
        ],
    }),
    ("early_blight", {
        "kind": "disease",
        "summary": "A fungal disease causing concentric brown spots, usually on older leaves first.",
        "tips": [
            "Prune lower infected leaves and improve air circulation.",
            "Mulch the soil to stop spores splashing up onto leaves.",
            "Rotate crops yearly and water at the base of the plant.",
        ],
    }),
    ("blight", {
        "kind": "disease",
        "summary": "A blight infection causing browning, lesions, and dieback of leaf tissue.",
        "tips": [
            "Remove affected foliage and sanitize tools afterwards.",
            "Keep leaves dry and avoid working with plants when wet.",
            "Use resistant varieties and apply fungicide if it spreads.",
        ],
    }),
    ("rust", {
        "kind": "disease",
        "summary": "A fungal disease showing orange, brown, or yellow pustules on leaves.",
        "tips": [
            "Remove infected leaves and clear fallen debris.",
            "Avoid wetting foliage; water early so leaves dry fast.",
            "Apply a suitable fungicide at the first sign of pustules.",
        ],
    }),
    ("powdery_mildew", {
        "kind": "disease",
        "summary": "A fungal disease that leaves a white, powdery coating on leaves.",
        "tips": [
            "Increase spacing and airflow; reduce shade and humidity.",
            "Remove the worst-affected leaves.",
            "Treat with sulfur, potassium bicarbonate, or neem oil.",
        ],
    }),
    ("downy_mildew", {
        "kind": "disease",
        "summary": "A moisture-loving disease with yellow patches above and fuzzy growth below leaves.",
        "tips": [
            "Improve drainage and air movement; avoid overhead watering.",
            "Remove infected leaves promptly.",
            "Apply an appropriate fungicide during humid spells.",
        ],
    }),
    ("mildew", {
        "kind": "disease",
        "summary": "A mildew infection encouraged by humidity and poor airflow.",
        "tips": [
            "Improve ventilation and reduce leaf wetness.",
            "Prune dense growth to let light and air in.",
            "Treat with an appropriate fungicide.",
        ],
    }),
    ("leaf_mold", {
        "kind": "disease",
        "summary": "A fungal disease common in humid, enclosed spaces, with yellow spots and moldy undersides.",
        "tips": [
            "Lower humidity and increase ventilation, especially in greenhouses.",
            "Space plants and prune for airflow.",
            "Remove affected leaves and apply fungicide if needed.",
        ],
    }),
    ("mosaic", {
        "kind": "disease",
        "summary": "A viral disease causing mottled green/yellow patterns and distorted growth.",
        "tips": [
            "There is no cure — remove and destroy infected plants.",
            "Control aphids and other sap-sucking insects that spread it.",
            "Wash hands and tools to avoid mechanical spread.",
        ],
    }),
    ("yellow_leaf_curl_virus", {
        "kind": "disease",
        "summary": "A whitefly-transmitted virus causing yellowing, curling, and stunted growth.",
        "tips": [
            "Remove and destroy infected plants to limit spread.",
            "Control whiteflies with traps, neem oil, or netting.",
            "Plant resistant varieties where available.",
        ],
    }),
    ("leaf_curl", {
        "kind": "disease",
        "summary": "Curling and distortion of leaves, often from a virus or sap-sucking pests.",
        "tips": [
            "Inspect for whiteflies, aphids, and mites and control them.",
            "Remove severely affected leaves.",
            "Keep plants well-watered and fed to support recovery.",
        ],
    }),
    ("virus", {
        "kind": "disease",
        "summary": "A viral infection — usually incurable and spread by insects or tools.",
        "tips": [
            "Remove and destroy infected plants promptly.",
            "Control insect vectors such as aphids and whiteflies.",
            "Disinfect tools and hands between plants.",
        ],
    }),
    ("bacterial", {
        "kind": "disease",
        "summary": "A bacterial infection causing water-soaked spots that turn brown or black.",
        "tips": [
            "Remove infected leaves and avoid handling plants when wet.",
            "Use copper-based sprays as a preventive measure.",
            "Rotate crops and use disease-free seed.",
        ],
    }),
    ("scab", {
        "kind": "disease",
        "summary": "A fungal disease causing rough, dark, scabby lesions on leaves and fruit.",
        "tips": [
            "Rake up and destroy fallen leaves to break the cycle.",
            "Prune for airflow and apply fungicide in early season.",
            "Choose scab-resistant varieties when planting.",
        ],
    }),
    ("rot", {
        "kind": "disease",
        "summary": "A rot disease causing dark, decaying lesions on leaves, stems, or fruit.",
        "tips": [
            "Remove and destroy affected parts immediately.",
            "Improve drainage and avoid overwatering.",
            "Sanitize tools and apply fungicide if it persists.",
        ],
    }),
    ("anthracnose", {
        "kind": "disease",
        "summary": "A fungal disease producing dark, sunken lesions on leaves and fruit.",
        "tips": [
            "Prune and destroy infected tissue.",
            "Avoid overhead watering and improve airflow.",
            "Apply fungicide during warm, wet periods.",
        ],
    }),
    ("scorch", {
        "kind": "disease",
        "summary": "Browning, drying leaf margins from disease or environmental stress.",
        "tips": [
            "Remove scorched leaves and keep soil evenly moist.",
            "Protect plants from harsh sun and drying wind.",
            "Check roots and drainage for underlying stress.",
        ],
    }),
    ("spot", {
        "kind": "disease",
        "summary": "Leaf-spot disease showing distinct spots that can merge and cause leaf drop.",
        "tips": [
            "Pick off spotted leaves and clear debris below the plant.",
            "Water at the base and keep foliage dry.",
            "Apply an appropriate fungicide if spots keep spreading.",
        ],
    }),
    ("mite", {
        "kind": "pest",
        "summary": "Spider-mite damage — tiny pests causing stippling, bronzing, and fine webbing.",
        "tips": [
            "Spray foliage (including undersides) with water to dislodge mites.",
            "Apply insecticidal soap, neem oil, or miticide.",
            "Raise humidity — mites thrive in hot, dry air.",
        ],
    }),
    ("whitefly", {
        "kind": "pest",
        "summary": "Whitefly infestation — sap-sucking insects that weaken plants and spread viruses.",
        "tips": [
            "Use yellow sticky traps to monitor and reduce numbers.",
            "Spray with insecticidal soap or neem oil, hitting leaf undersides.",
            "Remove heavily infested leaves.",
        ],
    }),
    ("caterpillar", {
        "kind": "pest",
        "summary": "Caterpillar feeding damage — chewed leaves and visible larvae.",
        "tips": [
            "Hand-pick caterpillars and remove egg clusters.",
            "Apply Bacillus thuringiensis (Bt) for safe control.",
            "Encourage natural predators like birds and wasps.",
        ],
    }),
    ("diabrotica_speciosa", {
        "kind": "pest",
        "summary": "Cucurbit beetle damage — leaf holes from a sap- and foliage-feeding beetle.",
        "tips": [
            "Hand-pick beetles and use row covers on young plants.",
            "Apply neem oil or an approved insecticide if numbers are high.",
            "Rotate crops to disrupt the beetle's life cycle.",
        ],
    }),
    ("green_mottle", {
        "kind": "disease",
        "summary": "A viral mottling disease causing pale-green blotches and distorted leaves.",
        "tips": [
            "Remove and destroy infected plants.",
            "Control insect vectors and weeds nearby.",
            "Use clean, certified planting material.",
        ],
    }),
    ("hispa", {
        "kind": "pest",
        "summary": "Rice hispa — a beetle that scrapes leaf surfaces, leaving white streaks.",
        "tips": [
            "Clip and destroy badly damaged leaf tips.",
            "Avoid excess nitrogen fertilizer, which attracts the pest.",
            "Use approved insecticides during heavy infestations.",
        ],
    }),
    ("blast", {
        "kind": "disease",
        "summary": "Rice blast — a serious fungal disease with spindle-shaped lesions.",
        "tips": [
            "Plant resistant varieties and use balanced fertilizer.",
            "Drain fields periodically and manage water carefully.",
            "Apply fungicide at early infection stages.",
        ],
    }),
    ("red_stripe", {
        "kind": "disease",
        "summary": "Sugarcane red stripe — reddish streaks along the leaf from a bacterial infection.",
        "tips": [
            "Remove and destroy infected leaves and stalks.",
            "Avoid excessive nitrogen and improve field drainage.",
            "Use disease-free planting setts.",
        ],
    }),
    ("algal_leaf", {
        "kind": "disease",
        "summary": "Algal leaf spot — orange/green raised spots caused by parasitic algae.",
        "tips": [
            "Prune for better airflow and sunlight penetration.",
            "Remove affected leaves and reduce humidity around plants.",
            "Apply copper-based spray if it spreads.",
        ],
    }),
    ("diseased", {
        "kind": "disease",
        "summary": "Signs of disease detected on this leaf.",
        "tips": [
            "Isolate the plant to prevent spreading to neighbors.",
            "Remove the most affected leaves and monitor closely.",
            "Consult a local extension service for a precise diagnosis.",
        ],
    }),
]

GENERIC_DISEASE = {
    "kind": "disease",
    "summary": "A plant-health issue was detected on this leaf.",
    "tips": [
        "Isolate the affected plant and remove damaged leaves.",
        "Keep foliage dry and improve air circulation.",
        "Monitor closely and treat with an appropriate remedy.",
    ],
}


def _clean_crop(raw: str) -> str:
    if raw in CROP_FIXES:
        return CROP_FIXES[raw]
    return raw.replace("_", " ").strip().title()


def _clean_condition(raw: str) -> str:
    text = raw.replace("_", " ").strip()
    # Preserve content inside parentheses, just tidy spacing.
    text = re.sub(r"\s+", " ", text)
    return text[:1].upper() + text[1:] if text else text


def parse_label(label: str) -> dict:
    """Split ``Crop__condition`` into structured, display-ready fields."""
    parts = re.split(r"_{2,}", label, maxsplit=1)
    crop_raw = parts[0]
    cond_raw = parts[1] if len(parts) > 1 else ""

    crop = _clean_crop(crop_raw)
    condition = _clean_condition(cond_raw) if cond_raw else "Unknown"

    guide = _guidance_for(cond_raw)
    is_healthy = guide["kind"] == "healthy"

    return {
        "label": label,
        "crop": crop,
        "condition": "Healthy" if is_healthy else condition,
        "kind": guide["kind"],
        "summary": guide["summary"],
        "tips": guide["tips"],
        "display": f"{crop} — {'Healthy' if is_healthy else condition}",
    }


def _guidance_for(cond_raw: str) -> dict:
    key = cond_raw.lower().replace(" ", "_")
    if not key:
        return GENERIC_DISEASE
    # Longest keyword first so "late_blight" beats "blight", etc.
    for keyword, guide in sorted(CONDITION_GUIDE, key=lambda kv: -len(kv[0])):
        if keyword in key:
            return guide
    return GENERIC_DISEASE
