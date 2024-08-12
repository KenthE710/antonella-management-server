# beauty_provider.py
from faker.providers import BaseProvider

BEAUTY_PRODUCTS = {
    "Cuidado del Cabello": [
        "Champú",
        "Acondicionador",
        "Mascarilla Capilar",
        "Aceite para el Cabello",
        "Sérum para el Cabello",
        "Cepillo para el Cabello",
        "Champú en Seco",
        "Espuma para el Cabello",
        "Gel para el Cabello",
        "Cera para el Cabello",
        "Tinte para el Cabello",
    ],
    "Cuidado de la Piel": [
        "Crema Facial",
        "Loción Corporal",
        "Limpiador Facial",
        "Tónico",
        "Sérum",
        "Protector Solar",
        "Exfoliante Facial",
        "Exfoliante Corporal",
        "Mascarilla Facial",
        "Mascarilla de Tela",
        "Crema para los Ojos",
        "Crema de Manos",
        "Crema para los Pies",
        "Aceite para Cutículas",
        "Fortalecedor de Uñas",
        "Quitaesmalte",
    ],
    "Maquillaje": [
        "Lápiz Labial",
        "Máscara de Pestañas",
        "Base de Maquillaje",
        "Rubor",
        "Delineador de Ojos",
        "Bálsamo Labial",
        "Brillo Labial",
        "Delineador de Labios",
        "Tinte Labial",
        "Corrector",
        "Iluminador",
        "Bronceador",
        "Kit de Contorno",
        "Spray Fijador",
        "Polvo Fijador",
    ],
    "Fragancias": ["Perfume", "Bruma Corporal"],
    "Cuidado Corporal": ["Desmaquillante", "Algodones", "Cepillo Facial", "Pinzas"],
}

BEAUTY_BRANDS = [
    "L'Oréal",
    "Estée Lauder",
    "Nivea",
    "Maybelline",
    "Dove",
    "Clinique",
    "Pantene",
    "Neutrogena",
    "Revlon",
    "Olay",
]

BEAUTY_SERVICES = {
    "Cuidado del Cabello": [
        "Corte de Cabello",
        "Tinte de Cabello",
        "Tratamiento Capilar",
        "Peinado",
        "Alisado",
    ],
    "Cuidado de la Piel": [
        "Facial",
        "Exfoliación",
        "Masaje Facial",
        "Tratamiento Antiacné",
        "Tratamiento Antiedad",
    ],
    "Maquillaje": [
        "Maquillaje de Día",
        "Maquillaje de Noche",
        "Maquillaje para Eventos",
        "Maquillaje de Novia",
    ],
    "Cuidado Corporal": [
        "Masaje Corporal",
        "Exfoliación Corporal",
        "Depilación",
        "Manicura",
        "Pedicura",
    ],
}


class Provider(BaseProvider):
    def beauty_product(self):
        tipo = self.random_element(list(BEAUTY_PRODUCTS.keys()))
        producto = self.random_element(BEAUTY_PRODUCTS[tipo])
        return producto, tipo

    def beauty_brand(self):
        return self.random_element(BEAUTY_BRANDS)

    def beauty_service(self):
        tipo = self.random_element(list(BEAUTY_SERVICES.keys()))
        servicio = self.random_element(BEAUTY_SERVICES[tipo])
        return servicio, tipo
