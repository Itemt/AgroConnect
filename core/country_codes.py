"""
Códigos de país y sus prefijos telefónicos para el selector de país
"""

COUNTRY_CODES = [
    ('', 'Selecciona un país'),
    ('+1', '🇺🇸 Estados Unidos (+1)'),
    ('+1', '🇨🇦 Canadá (+1)'),
    ('+52', '🇲🇽 México (+52)'),
    ('+54', '🇦🇷 Argentina (+54)'),
    ('+55', '🇧🇷 Brasil (+55)'),
    ('+56', '🇨🇱 Chile (+56)'),
    ('+57', '🇨🇴 Colombia (+57)'),
    ('+58', '🇻🇪 Venezuela (+58)'),
    ('+51', '🇵🇪 Perú (+51)'),
    ('+591', '🇧🇴 Bolivia (+591)'),
    ('+593', '🇪🇨 Ecuador (+593)'),
    ('+595', '🇵🇾 Paraguay (+595)'),
    ('+598', '🇺🇾 Uruguay (+598)'),
    ('+34', '🇪🇸 España (+34)'),
    ('+33', '🇫🇷 Francia (+33)'),
    ('+49', '🇩🇪 Alemania (+49)'),
    ('+39', '🇮🇹 Italia (+39)'),
    ('+44', '🇬🇧 Reino Unido (+44)'),
    ('+7', '🇷🇺 Rusia (+7)'),
    ('+86', '🇨🇳 China (+86)'),
    ('+81', '🇯🇵 Japón (+81)'),
    ('+82', '🇰🇷 Corea del Sur (+82)'),
    ('+91', '🇮🇳 India (+91)'),
    ('+61', '🇦🇺 Australia (+61)'),
    ('+27', '🇿🇦 Sudáfrica (+27)'),
    ('+20', '🇪🇬 Egipto (+20)'),
    ('+90', '🇹🇷 Turquía (+90)'),
    ('+966', '🇸🇦 Arabia Saudí (+966)'),
    ('+971', '🇦🇪 Emiratos Árabes Unidos (+971)'),
    ('+55', '🇧🇷 Brasil (+55)'),
    ('+56', '🇨🇱 Chile (+56)'),
    ('+57', '🇨🇴 Colombia (+57)'),
    ('+58', '🇻🇪 Venezuela (+58)'),
    ('+51', '🇵🇪 Perú (+51)'),
    ('+591', '🇧🇴 Bolivia (+591)'),
    ('+593', '🇪🇨 Ecuador (+593)'),
    ('+595', '🇵🇾 Paraguay (+595)'),
    ('+598', '🇺🇾 Uruguay (+598)'),
]

def get_country_codes():
    """Retorna la lista de códigos de país"""
    return COUNTRY_CODES

def get_country_code_by_code(code):
    """Retorna el país por su código"""
    for country_code, country_name in COUNTRY_CODES:
        if country_code == code:
            return country_name
    return None

def get_phone_validation_pattern(country_code):
    """Retorna el patrón de validación para un código de país específico"""
    patterns = {
        '+1': r'^\+1[0-9]{10}$',  # Estados Unidos/Canadá: +1XXXXXXXXXX
        '+52': r'^\+52[0-9]{10}$',  # México: +52XXXXXXXXXX
        '+54': r'^\+54[0-9]{10,11}$',  # Argentina: +54XXXXXXXXXX
        '+55': r'^\+55[0-9]{10,11}$',  # Brasil: +55XXXXXXXXXX
        '+56': r'^\+56[0-9]{8,9}$',  # Chile: +56XXXXXXXX
        '+57': r'^\+57[0-9]{10}$',  # Colombia: +57XXXXXXXXXX
        '+58': r'^\+58[0-9]{10}$',  # Venezuela: +58XXXXXXXXXX
        '+51': r'^\+51[0-9]{9}$',  # Perú: +51XXXXXXXXX
        '+591': r'^\+591[0-9]{8}$',  # Bolivia: +591XXXXXXXX
        '+593': r'^\+593[0-9]{9}$',  # Ecuador: +593XXXXXXXXX
        '+595': r'^\+595[0-9]{9}$',  # Paraguay: +595XXXXXXXXX
        '+598': r'^\+598[0-9]{8}$',  # Uruguay: +598XXXXXXXX
        '+34': r'^\+34[0-9]{9}$',  # España: +34XXXXXXXXX
        '+33': r'^\+33[0-9]{9}$',  # Francia: +33XXXXXXXXX
        '+49': r'^\+49[0-9]{10,11}$',  # Alemania: +49XXXXXXXXXX
        '+39': r'^\+39[0-9]{9,10}$',  # Italia: +39XXXXXXXXX
        '+44': r'^\+44[0-9]{10,11}$',  # Reino Unido: +44XXXXXXXXXX
        '+7': r'^\+7[0-9]{10}$',  # Rusia: +7XXXXXXXXXX
        '+86': r'^\+86[0-9]{11}$',  # China: +86XXXXXXXXXXX
        '+81': r'^\+81[0-9]{10,11}$',  # Japón: +81XXXXXXXXXX
        '+82': r'^\+82[0-9]{9,10}$',  # Corea del Sur: +82XXXXXXXXX
        '+91': r'^\+91[0-9]{10}$',  # India: +91XXXXXXXXXX
        '+61': r'^\+61[0-9]{9}$',  # Australia: +61XXXXXXXXX
        '+27': r'^\+27[0-9]{9}$',  # Sudáfrica: +27XXXXXXXXX
        '+20': r'^\+20[0-9]{10}$',  # Egipto: +20XXXXXXXXXX
        '+90': r'^\+90[0-9]{10}$',  # Turquía: +90XXXXXXXXXX
        '+966': r'^\+966[0-9]{9}$',  # Arabia Saudí: +966XXXXXXXXX
        '+971': r'^\+971[0-9]{9}$',  # Emiratos Árabes Unidos: +971XXXXXXXXX
    }
    return patterns.get(country_code, r'^\+[0-9]{1,4}[0-9]{6,15}$')  # Patrón genérico
