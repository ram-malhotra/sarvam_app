"""Demo menu seed dataset for South Spice Kitchen in VoiceMenu AI."""

import logging
from typing import Any, Dict, List
from sqlalchemy.orm import Session
from app.models import MenuItem, Restaurant

logger = logging.getLogger(__name__)

DEMO_RESTAURANT_ID = "demo-restaurant"

DEMO_RESTAURANT_DATA: Dict[str, Any] = {
    "id": DEMO_RESTAURANT_ID,
    "name": "South Spice Kitchen",
    "description": (
        "Authentic South Indian culinary experience with traditional recipes, "
        "crispy dosas, aromatic filter coffee, and fragrant spices. [DEMO DATA]"
    ),
    "address": "124 Indiranagar 100ft Road, Bengaluru, Karnataka 560038",
    "is_demo": True,
}

DEMO_MENU_ITEMS: List[Dict[str, Any]] = [
    # --- DOSA (4 items) ---
    {
        "id": "masala-dosa",
        "restaurant_id": DEMO_RESTAURANT_ID,
        "category": "dosa",
        "canonical_name": "Masala Dosa",
        "localized_names": {
            "hi-IN": "मसाला डोसा",
            "ta-IN": "மசாலா தோசை",
            "te-IN": "మసాలా దోశ",
        },
        "description": (
            "Crispy golden fermented crepe stuffed with spiced potato masala and "
            "served with fresh coconut chutney and piping hot sambar. [DEMO DATA]"
        ),
        "localized_descriptions": {
            "hi-IN": "मसालेदार आलू के मिश्रण से भरा कुरकुरा डोसा, नारियल की चटनी और सांभर के साथ। [DEMO DATA]",
            "ta-IN": "மசாலா உருளைக்கிழங்கு நிரப்பப்பட்ட மொறுமொறு தோசை, தேங்காய் சட்னி மற்றும் சாம்பாருடன். [DEMO DATA]",
            "te-IN": "మసాలా బంగాళాదుంప మిశ్రమంతో కూడిన కరకరలాడే దోశ, కొబ్బరి చట్నీ మరియు సాంబారుతో. [DEMO DATA]",
        },
        "price": 120.0,
        "is_veg": True,
        "ingredients": ["rice", "urad dal", "potato", "onion", "mustard seeds", "curry leaves", "ghee"],
        "spice_level": "medium",
        "available": True,
        "customizations": [
            {"name": "extra_spicy", "options": ["yes", "no"]},
            {"name": "cheese", "options": ["yes", "no"]},
        ],
        "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc",
    },
    {
        "id": "plain-dosa",
        "restaurant_id": DEMO_RESTAURANT_ID,
        "category": "dosa",
        "canonical_name": "Plain Dosa",
        "localized_names": {
            "hi-IN": "सादा डोसा",
            "ta-IN": "சாதாரண தோசை",
            "te-IN": "ప్లేన్ దోశ",
        },
        "description": (
            "Thin, crispy golden crepe made from traditional slow-fermented rice and "
            "lentil batter, accompanied by house-special chutneys. [DEMO DATA]"
        ),
        "localized_descriptions": {
            "hi-IN": "पारंपरिक किण्वित घोल से बना पतला, कुरकुरा सादा डोसा और चटनी। [DEMO DATA]",
            "ta-IN": "பாரம்பரிய புளித்த மாவில் செய்யப்பட்ட மெல்லிய, மொறுமொறு தோசை. [DEMO DATA]",
            "te-IN": "సాంప్రదాయ పిండితో చేసిన పలుచని, కరకరలాడే ప్లేన్ దోశ. [DEMO DATA]",
        },
        "price": 80.0,
        "is_veg": True,
        "ingredients": ["rice", "urad dal", "fenugreek", "ghee"],
        "spice_level": "mild",
        "available": True,
        "customizations": [],
        "image_url": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976",
    },
    {
        "id": "rava-dosa",
        "restaurant_id": DEMO_RESTAURANT_ID,
        "category": "dosa",
        "canonical_name": "Rava Dosa",
        "localized_names": {
            "hi-IN": "रवा डोसा",
            "ta-IN": "ரவா தோசை",
            "te-IN": "రవ్వ దోశ",
        },
        "description": (
            "Extremely crispy and lacy semolina crepe speckled with crushed black "
            "peppercorns, ginger, and cumin seeds. [DEMO DATA]"
        ),
        "localized_descriptions": {
            "hi-IN": "सूजी, जीरा, अदरक और हरी मिर्च से बना जालीदार कुरकुरा डोसा। [DEMO DATA]",
            "ta-IN": "ரவை, சீரகம், இஞ்சி மற்றும் பச்சை மிளகாயால் செய்யப்பட்ட மொறுமொறு தோசை. [DEMO DATA]",
            "te-IN": "రవ్వ, జీలకర్ర, అల్లం మరియు పచ్చిమిర్చితో చేసిన కరకరలాడే రవ్వ దోశ. [DEMO DATA]",
        },
        "price": 110.0,
        "is_veg": True,
        "ingredients": ["semolina (rava)", "rice flour", "cumin", "peppercorns", "ginger", "curry leaves"],
        "spice_level": "mild",
        "available": True,
        "customizations": [
            {"name": "onion", "options": ["yes", "no"]},
        ],
        "image_url": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46",
    },
    {
        "id": "mysore-dosa",
        "restaurant_id": DEMO_RESTAURANT_ID,
        "category": "dosa",
        "canonical_name": "Mysore Masala Dosa",
        "localized_names": {
            "hi-IN": "मैसूर मसाला डोसा",
            "ta-IN": "மைசூர் மசாலா தோசை",
            "te-IN": "మైసూర్ మసాలా దోశ",
        },
        "description": (
            "Crispy crepe generously smeared with signature fiery red garlic-chili "
            "chutney and stuffed with spiced potato filling. [DEMO DATA]"
        ),
        "localized_descriptions": {
            "hi-IN": "तीखी लाल लहसुन की चटनी और आलू भरावन से बना प्रसिद्ध मैसूर डोसा। [DEMO DATA]",
            "ta-IN": "காரசாரமான பூண்டு சட்னி தடவப்பட்டு உருளைக்கிழங்கு மசாலாவுடன் கூடிய மைசூர் தோசை. [DEMO DATA]",
            "te-IN": "ఎర్రటి వెల్లుల్లి చట్నీ రాసి బంగాళాదుంప మసాలాతో నింపిన మైసూర్ దోశ. [DEMO DATA]",
        },
        "price": 140.0,
        "is_veg": True,
        "ingredients": ["rice", "urad dal", "red garlic chutney", "potato", "onion", "butter"],
        "spice_level": "spicy",
        "available": True,
        "customizations": [],
        "image_url": "https://images.unsplash.com/photo-1516714435131-44d6b64dc6a2",
    },

    # --- IDLI (2 items) ---
    {
        "id": "idli-sambar",
        "restaurant_id": DEMO_RESTAURANT_ID,
        "category": "idli",
        "canonical_name": "Idli Sambar (2 pcs)",
        "localized_names": {
            "hi-IN": "इडली सांभर (2 पीस)",
            "ta-IN": "இட்லி சாம்பார் (2 துண்டுகள்)",
            "te-IN": "ఇడ్లీ సాంబారు (2 ముక్కలు)",
        },
        "description": (
            "Two pillow-soft steamed fermented rice cakes submerged in rich aromatic "
            "vegetable sambar with freshly ground coconut chutney. [DEMO DATA]"
        ),
        "localized_descriptions": {
            "hi-IN": "गरमागरम सांभर और नारियल की चटनी के साथ दो मुलायम भाप में पकी इडली। [DEMO DATA]",
            "ta-IN": "சூடான நறுமண சாம்பாரில் ஊறவைத்த மிருதுவான இட்லிகள் தேங்காய் சட்னியுடன். [DEMO DATA]",
            "te-IN": "వేడి వేడి సాంబారులో ముంచిన మెత్తటి ఇడ్లీలు కొబ్బరి చట్నీతో. [DEMO DATA]",
        },
        "price": 70.0,
        "is_veg": True,
        "ingredients": ["rice", "urad dal", "toor dal", "tamarind", "drumstick", "sambar spices"],
        "spice_level": "mild",
        "available": True,
        "customizations": [],
        "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc",
    },
    {
        "id": "ghee-podi-idli",
        "restaurant_id": DEMO_RESTAURANT_ID,
        "category": "idli",
        "canonical_name": "Ghee Podi Idli",
        "localized_names": {
            "hi-IN": "घी पोड़ी इडली",
            "ta-IN": "நெய் பொடி இட்லி",
            "te-IN": "నెయ్యి పొడి ఇడ్లీ",
        },
        "description": (
            "Bite-sized melt-in-mouth idlis tossed generously in golden desi ghee and "
            "aromatic spiced gunpowder (milagai podi). [DEMO DATA]"
        ),
        "localized_descriptions": {
            "hi-IN": "शुद्ध देसी घी और तीखे गनपाउडर मसाले में लिपटी स्वादिष्ट इडली। [DEMO DATA]",
            "ta-IN": "சுத்தமான நெய் மற்றும் இட்லி பொடியில் வதக்கிய பஞ்சு போன்ற இட்லிகள். [DEMO DATA]",
            "te-IN": "స్వచ్ఛమైన నెయ్యి మరియు కారప్పొడితో కలిపిన మెత్తటి ఇడ్లీలు. [DEMO DATA]",
        },
        "price": 90.0,
        "is_veg": True,
        "ingredients": ["rice", "urad dal", "desi ghee", "milagai podi (gunpowder)", "roasted lentils"],
        "spice_level": "medium",
        "available": True,
        "customizations": [],
        "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc",
    },

    # --- RICE (3 items) ---
    {
        "id": "curd-rice",
        "restaurant_id": DEMO_RESTAURANT_ID,
        "category": "rice",
        "canonical_name": "Curd Rice",
        "localized_names": {
            "hi-IN": "दही चावल",
            "ta-IN": "தயிர் சாதம்",
            "te-IN": "పెరుగు అన్నం",
        },
        "description": (
            "Classic soothing yogurt rice tempered with crackling mustard seeds, curry "
            "leaves, grated ginger, and garnished with sweet pomegranate. [DEMO DATA]"
        ),
        "localized_descriptions": {
            "hi-IN": "सरसों, करी पत्ता, अदरक और अनार के दानों से तड़का लगा मलाईदार दही चावल। [DEMO DATA]",
            "ta-IN": "கடுகு, கறிவேப்பிலை, இஞ்சி தாளித்த சுவையான கிரீமி தயிர் சாதம். [DEMO DATA]",
            "te-IN": "ఆవాలు, కరివేపాకు, అల్లం తాలింపుతో చేసిన రుచికరమైన పెరుగు అన్నం. [DEMO DATA]",
        },
        "price": 100.0,
        "is_veg": True,
        "ingredients": ["boiled rice", "fresh yogurt", "mustard seeds", "green chilies", "ginger", "curry leaves", "pomegranate"],
        "spice_level": "mild",
        "available": True,
        "customizations": [],
        "image_url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d",
    },
    {
        "id": "lemon-rice",
        "restaurant_id": DEMO_RESTAURANT_ID,
        "category": "rice",
        "canonical_name": "Lemon Rice",
        "localized_names": {
            "hi-IN": "नींबू चावल",
            "ta-IN": "எலுமிச்சை சாதம்",
            "te-IN": "నిమ్మకాయ పులిహోర",
        },
        "description": (
            "Zesty basmati rice infused with freshly squeezed lemon juice, turmeric, crunchy "
            "roasted peanuts, and fragrant tempered spices. [DEMO DATA]"
        ),
        "localized_descriptions": {
            "hi-IN": "नींबू के रस, हल्दी और कुरकुरी मूंगफली के तड़के से बना खुशबूदार चावल। [DEMO DATA]",
            "ta-IN": "எலுமிச்சை சாறு, மஞ்சள் மற்றும் வறுத்த வேர்க்கடலை கலந்த மணம் மிக்க சாதம். [DEMO DATA]",
            "te-IN": "నిమ్మరసం, పసుపు మరియు వేరుశెనగ పప్పుల తాలింపుతో చేసిన పులిహోర. [DEMO DATA]",
        },
        "price": 110.0,
        "is_veg": True,
        "ingredients": ["rice", "lemon juice", "peanuts", "turmeric", "mustard seeds", "green chilies", "curry leaves"],
        "spice_level": "mild",
        "available": True,
        "customizations": [],
        "image_url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d",
    },
    {
        "id": "chicken-biryani",
        "restaurant_id": DEMO_RESTAURANT_ID,
        "category": "rice",
        "canonical_name": "Chicken Biryani",
        "localized_names": {
            "hi-IN": "चिकन बिरयानी",
            "ta-IN": "சிக்கன் பிரியாணி",
            "te-IN": "చికెన్ బిర్యానీ",
        },
        "description": (
            "Rich and flavorful South Indian style chicken dum biryani cooked with succulent "
            "marinated chicken, fragrant seeraga samba rice, and whole spices. [DEMO DATA]"
        ),
        "localized_descriptions": {
            "hi-IN": "सुगंधित चावल और खड़े मसालों के साथ पकाई गई दक्षिण भारतीय चिकन बिरयानी। [DEMO DATA]",
            "ta-IN": "மணமணக்கும் சீரக சம்பா அரிசி மற்றும் மசாலாக்களுடன் சமைக்கப்பட்ட சுவையான சிக்கன் பிரியாணி. [DEMO DATA]",
            "te-IN": "సుగంధ ద్రవ్యాలు మరియు చికెన్ ముక్కలతో దమ్ చేసిన దక్షిణ భారత చికెన్ బిర్యానీ. [DEMO DATA]",
        },
        "price": 220.0,
        "is_veg": False,
        "ingredients": ["chicken", "seeraga samba rice", "onion", "yogurt", "mint", "coriander", "biryani masala", "ghee"],
        "spice_level": "spicy",
        "available": True,
        "customizations": [
            {"name": "portion", "options": ["half", "full"]},
            {"name": "raita", "options": ["yes", "no"]},
        ],
        "image_url": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8",
    },

    # --- SNACKS (3 items) ---
    {
        "id": "medu-vada",
        "restaurant_id": DEMO_RESTAURANT_ID,
        "category": "snacks",
        "canonical_name": "Medu Vada (2 pcs)",
        "localized_names": {
            "hi-IN": "मेदु वड़ा (2 पीस)",
            "ta-IN": "மெது வடை (2 துண்டுகள்)",
            "te-IN": "మెదు వడ (2 ముక్కలు)",
        },
        "description": (
            "Crispy golden exterior with fluffy cloud-like center, doughnut-shaped savory "
            "fritters flavored with whole pepper and curry leaves. [DEMO DATA]"
        ),
        "localized_descriptions": {
            "hi-IN": "बाहर से कुरकुरे और अंदर से बेहद नरम उड़द दाल के बड़े। [DEMO DATA]",
            "ta-IN": "வெளியே மொறுமொறுப்பாகவும் உள்ளே மிருதுவாகவும் இருக்கும் உளுந்து வடை. [DEMO DATA]",
            "te-IN": "బయట కరకరలాడుతూ లోపల మెత్తగా ఉండే మినప గారెలు. [DEMO DATA]",
        },
        "price": 70.0,
        "is_veg": True,
        "ingredients": ["urad dal", "cracked black pepper", "cumin", "ginger", "curry leaves", "oil"],
        "spice_level": "mild",
        "available": True,
        "customizations": [],
        "image_url": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46",
    },
    {
        "id": "samosa",
        "restaurant_id": DEMO_RESTAURANT_ID,
        "category": "snacks",
        "canonical_name": "Samosa (2 pcs)",
        "localized_names": {
            "hi-IN": "समोसा (2 पीस)",
            "ta-IN": "சமோசா (2 துண்டுகள்)",
            "te-IN": "సమోసా (2 ముక్కలు)",
        },
        "description": (
            "Crisp flaky pastry triangles generously loaded with spiced potatoes, tender "
            "green peas, and crushed coriander seeds. [DEMO DATA]"
        ),
        "localized_descriptions": {
            "hi-IN": "आलू, हरी मटर और मसालों से भरी कुरकुरी सुनहरी समोसा पेस्ट्री। [DEMO DATA]",
            "ta-IN": "மசாலா உருளைக்கிழங்கு மற்றும் பட்டாணி நிரப்பப்பட்ட மொறுமொறு சமோசா. [DEMO DATA]",
            "te-IN": "మసాలా బంగాళాదుంప, బఠానీలు నింపిన కరకరలాడే వేడి వేడి సమోసాలు. [DEMO DATA]",
        },
        "price": 60.0,
        "is_veg": True,
        "ingredients": ["flour", "potatoes", "green peas", "cumin", "coriander seeds", "garam masala", "oil"],
        "spice_level": "medium",
        "available": True,
        "customizations": [],
        "image_url": "https://images.unsplash.com/photo-1601050690597-df0568f70950",
    },
    {
        "id": "chicken-65",
        "restaurant_id": DEMO_RESTAURANT_ID,
        "category": "snacks",
        "canonical_name": "Chicken 65",
        "localized_names": {
            "hi-IN": "चिकन 65",
            "ta-IN": "சிக்கன் 65",
            "te-IN": "చికెన్ 65",
        },
        "description": (
            "Fiery, deeply spiced, crispy fried boneless chicken bites tossed with fresh green "
            "chilies, ginger-garlic paste, and crackling curry leaves. [DEMO DATA]"
        ),
        "localized_descriptions": {
            "hi-IN": "अदरक, लहसुन, लाल मिर्च और करी पत्ता में मैरीनेट किया हुआ कुरकुरा चिकन 65। [DEMO DATA]",
            "ta-IN": "இஞ்சி, பூண்டு, கறிவேப்பிலை மசாலா கலவையில் பொரித்த காரசாரமான சிக்கன் 65. [DEMO DATA]",
            "te-IN": "అల్లం వెల్లుల్లి, ఎర్ర కారం మరియు కరివేపాకుతో వేయించిన కారమైన చికెన్ 65. [DEMO DATA]",
        },
        "price": 180.0,
        "is_veg": False,
        "ingredients": ["boneless chicken", "kashmiri chili powder", "ginger garlic paste", "curry leaves", "yogurt", "cornflour"],
        "spice_level": "very_spicy",
        "available": False,  # Marked unavailable to test unavailable flow
        "customizations": [],
        "image_url": "https://images.unsplash.com/photo-1610057099443-fde8c4d50f91",
    },

    # --- BEVERAGES (3 items) ---
    {
        "id": "filter-coffee",
        "restaurant_id": DEMO_RESTAURANT_ID,
        "category": "beverages",
        "canonical_name": "South Indian Filter Coffee",
        "localized_names": {
            "hi-IN": "दक्षिण भारतीय फ़िल्टर कॉफ़ी",
            "ta-IN": "தென்னிந்திய பில்டர் காபி",
            "te-IN": "దక్షిణ భారత ఫిల్టర్ కాఫీ",
        },
        "description": (
            "Authentic slow-drip brass filter coffee prepared with aromatic chicory blend, "
            "frothed high with steaming full-cream dairy milk. [DEMO DATA]"
        ),
        "localized_descriptions": {
            "hi-IN": "कांस्य के गिलास में परोसी जाने वाली कड़क और खुशबूदार पारंपरिक फ़िल्टर कॉफ़ी। [DEMO DATA]",
            "ta-IN": "பித்தளை டம்ளரில் நுரை பொங்க பரிமாறப்படும் பாரம்பரிய பில்டர் காபி. [DEMO DATA]",
            "te-IN": "ఇత్తడి గ్లాసులో అందించే తియ్యని, చిక్కని సాంప్రదాయ ఫిల్టర్ కాఫీ. [DEMO DATA]",
        },
        "price": 50.0,
        "is_veg": True,
        "ingredients": ["roasted coffee beans", "chicory", "fresh whole milk", "cane sugar"],
        "spice_level": "mild",
        "available": True,
        "customizations": [],
        "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd",
    },
    {
        "id": "mango-lassi",
        "restaurant_id": DEMO_RESTAURANT_ID,
        "category": "beverages",
        "canonical_name": "Mango Lassi",
        "localized_names": {
            "hi-IN": "मैंगो लस्सी",
            "ta-IN": "மாம்பழ லஸ்ஸி",
            "te-IN": "మామిడి లస్సీ",
        },
        "description": (
            "Velvety smooth, chilled yogurt drink blended with sweet Alphonso mango pulp "
            "and a delicate fragrant touch of green cardamom. [DEMO DATA]"
        ),
        "localized_descriptions": {
            "hi-IN": "मीठे अल्फोंसो आम के गूदे, ताजे दही और इलायची से बनी ठंडी मैंगो लस्सी। [DEMO DATA]",
            "ta-IN": "இனிப்பான மாம்பழக் கூழ், தயிர் மற்றும் ஏலக்காய் கலந்த குளிர்ச்சியான மாம்பழ லஸ்ஸி. [DEMO DATA]",
            "te-IN": "తీపి మామిడి గుజ్జు, తాజా పెరుగు మరియు యాలకులతో చేసిన చల్లని మామిడి లస్సీ. [DEMO DATA]",
        },
        "price": 80.0,
        "is_veg": True,
        "ingredients": ["alphonso mango pulp", "fresh yogurt", "milk", "cardamom", "sugar"],
        "spice_level": "mild",
        "available": True,
        "customizations": [],
        "image_url": "https://images.unsplash.com/photo-1546173159-315724a31696",
    },
    {
        "id": "masala-chai",
        "restaurant_id": DEMO_RESTAURANT_ID,
        "category": "beverages",
        "canonical_name": "Masala Chai",
        "localized_names": {
            "hi-IN": "मसाला चाय",
            "ta-IN": "மசாலா டீ",
            "te-IN": "మసాలా టీ",
        },
        "description": (
            "Strong aromatic CTC Assam black tea simmered with fresh crushed ginger, green "
            "cardamom pods, cinnamon bark, and rich milk. [DEMO DATA]"
        ),
        "localized_descriptions": {
            "hi-IN": "अदरक, इलायची, दालचीनी और दूध के साथ उबाली गई कड़क मसाला चाय। [DEMO DATA]",
            "ta-IN": "இஞ்சி, ஏலக்காய், இலவங்கப்பட்டை சேர்த்து காய்ச்சிய மணமணக்கும் மசாலா டீ. [DEMO DATA]",
            "te-IN": "అల్లం, యాలకులు, దాల్చిన చెక్క వేసి మరిగించిన వేడి మసాలా టీ. [DEMO DATA]",
        },
        "price": 40.0,
        "is_veg": True,
        "ingredients": ["assam tea leaves", "crushed ginger", "green cardamom", "cinnamon", "milk"],
        "spice_level": "mild",
        "available": True,
        "customizations": [
            {"name": "sugar", "options": ["less", "normal", "more"]},
        ],
        "image_url": "https://images.unsplash.com/photo-1561336313-0bd5e0b27ec8",
    },
]


def seed_database(db: Session) -> None:
    """Populate database with demo restaurant and 15 authentic South Spice Kitchen items.

    Args:
        db (Session): SQLAlchemy database session.
    """
    try:
        # Check if restaurant exists or create
        restaurant = db.query(Restaurant).filter(Restaurant.id == DEMO_RESTAURANT_ID).first()
        if not restaurant:
            logger.info("Creating demo restaurant: %s", DEMO_RESTAURANT_DATA["name"])
            restaurant = Restaurant(**DEMO_RESTAURANT_DATA)
            db.add(restaurant)
            db.flush()

        # Seed menu items
        for item_data in DEMO_MENU_ITEMS:
            existing = db.query(MenuItem).filter(MenuItem.id == item_data["id"]).first()
            if not existing:
                item = MenuItem(**item_data)
                db.add(item)

        db.commit()
        logger.info("Successfully seeded %d menu items for %s.", len(DEMO_MENU_ITEMS), restaurant.name)
    except Exception as exc:
        db.rollback()
        logger.error("Failed to seed database: %s", exc, exc_info=True)
        raise exc
