import nltk
import re
import os

nltk_data = os.path.join(os.path.dirname(__file__), '..', 'nltk_data')
os.makedirs(nltk_data, exist_ok=True)
nltk.data.path.append(nltk_data)

try:
    nltk.download('punkt', download_dir=nltk_data, quiet=True)
    nltk.download('punkt_tab', download_dir=nltk_data, quiet=True)
    nltk.download('stopwords', download_dir=nltk_data, quiet=True)
except:
    pass

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

STOPWORDS_ES = set([
    'el','la','los','las','un','una','de','del','en','que','y','a',
    'es','por','con','se','su','al','lo','como','para','mas','mi',
    'me','te','le','nos','si','o','pero','porque','cuando','donde'
])

try:
    STOPWORDS_ES = STOPWORDS_ES.union(set(stopwords.words('spanish')))
except:
    pass

CATEGORIAS = {
    'QUEJA':      ['queja','molestia','problema','malo','deficiente','inconformidad','insatisfecho'],
    'PETICION':   ['peticion','solicitud','informacion','certificado','documento','constancia','tramite'],
    'RECLAMO':    ['reclamo','derecho','exigir','incumplio','cobro','pago','devolucion','reembolso'],
    'SUGERENCIA': ['sugerencia','mejorar','proponer','idea','recomendacion','propuesta','mejora']
}

def tokenizar(texto):
    texto = texto.lower()
    texto = texto.encode('ascii', 'ignore').decode('ascii')
    texto = re.sub(r'[^a-z0-9\s]', ' ', texto)
    try:
        tokens = word_tokenize(texto, language='spanish')
    except:
        tokens = texto.split()
    tokens = [t for t in tokens if t.isalpha() and t not in STOPWORDS_ES and len(t) > 2]
    return tokens

def clasificar_intencion(texto):
    tokens = tokenizar(texto)
    puntajes = {cat: 0 for cat in CATEGORIAS}
    for token in tokens:
        for cat, palabras in CATEGORIAS.items():
            if any(token in p or p in token for p in palabras):
                puntajes[cat] += 1
    max_p = max(puntajes.values())
    if max_p == 0:
        return None
    return max(puntajes, key=puntajes.get)

def preprocesar(texto):
    tokens = tokenizar(texto)
    intencion = clasificar_intencion(texto)
    texto_limpio = ' '.join(tokens) if tokens else texto
    return {
        'texto_original': texto,
        'texto_limpio': texto_limpio,
        'tokens': tokens,
        'intencion': intencion
    }
