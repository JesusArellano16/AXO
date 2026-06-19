class Central:
    def __init__(self, nombre, fullName, queries, file_name):
        self.nombre = nombre
        self.fullName = fullName
        self.queries = queries
        self.file_name = file_name

centrales = [
    Central(
        "IXTLA",
        "IXTLAHUACA",
        ['ASSETS IN IXTLAHUACA', 'SERVERS IN IXTLAHUACA', 'ALL NETWORK DEVICES IN IXTLAHUACA', 'PCs IN IXTLAHUACA'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "CARSO",
        "CARSO",
        ['ASSETS IN CARSO LEGACY', 'SERVERS IN CARSO', 'ALL NETWORK DEVICES IN CARSO', 'PCs IN CARSO LEGACY'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "L_ALB",
        "LAGO ALBERTO",
        ['ASSETS IN LAGO ALBERTO', 'SERVERS IN LAGO ALBERTO', 'ALL NETWORK DEVICES IN LAGO ALBERTO', 'PCs IN LAGO ALBERTO'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "SOTELO",
        "SOTELO",
        ['ASSETS IN SOTELO', 'SERVERS IN SOTELO', 'ALL NETWORK DEVICES IN SOTELO', 'PCs IN SOTELO'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "VALLEJO",
        "VALLEJO",
        ['ASSETS IN VALLEJO', 'SERVERS IN VALLEJO', 'ALL NETWORK DEVICES IN VALLEJO', 'PCs IN VALLEJO'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "TECA",
        "TECAMACHALCO",
        ['ASSETS IN TECAMACHALCO', 'SERVERS IN TECAMACHALCO', 'ALL NETWORK DEVICES IN TECAMACHALCO', 'PCs IN TECAMACHALCO'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "CIVAC",
        "CIVAC",
        ['ASSETS IN CIVAC', 'SERVERS IN CIVAC', 'ALL NETWORK DEVICES IN CIVAC', 'PCs IN CIVAC'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "CUAUTI",
        "CUAUTITLAN",
        ['ASSETS IN CUAUTITLAN', 'SERVERS IN CUAUTITLAN', 'ALL NETWORK DEVICES IN CUAUTITLAN', 'PCs IN CUAUTITLAN'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "ECA",
        "ECATEPEC",
        ['ASSETS IN ECATEPEC', 'SERVERS IN ECATEPEC', 'ALL NETWORK DEVICES IN ECATEPEC', 'PCs IN ECATEPEC'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "POLANCO",
        "POLANCO",
        ['ASSETS IN POLANCO', 'SERVERS IN POLANCO', 'ALL NETWORK DEVICES IN POLANCO', 'PCs IN POLANCO'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "POPOTLA",
        "POPOTLA",
        ['ASSETS IN POPOTLA', 'SERVERS IN POPOTLA', 'ALL NETWORK DEVICES IN POPOTLA', 'PCs IN POPOTLA'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "SAN_JER",
        "SAN JERONIMO",
        ['ASSETS IN SAN JERONIMO', 'SERVERS IN SAN JERONIMO', 'ALL NETWORK DEVICES IN SAN JERONIMO', 'PCs IN SAN JERONIMO'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "REVO9",
        "REVOLUCION PACHUCA",
        ['ASSETS IN REVOLUCION PACHUCA', 'SERVERS IN REVOLUCION PACHUCA', 'ALL NETWORK DEVICES IN REVOLUCION PACHUCA', 'PCs IN REVOLUCION PACHUCA'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "TACUBA",
        "TACUBAYA",
        ['ASSETS IN TACUBAYA', 'SERVERS IN TACUBAYA', 'ALL NETWORK DEVICES IN TACUBAYA', 'PCs IN TACUBAYA'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "TOLLO",
        "TOLLOCAN",
        ['ASSETS IN TOLLOCAN', 'SERVERS IN TOLLOCAN', 'ALL NETWORK DEVICES IN TOLLOCAN', 'PCs IN TOLLOCAN'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "URRAZA",
        "URRAZA",
        ['ASSETS IN URRAZA', 'SERVERS IN URRAZA', 'ALL NETWORK DEVICES IN URRAZA', 'PCs IN URRAZA'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "XOCHI",
        "XOCHIMILCO",
        ['ASSETS IN XOCHIMILCO', 'SERVERS IN XOCHIMILCO', 'ALL NETWORK DEVICES IN XOCHIMILCO', 'PCs IN XOCHIMILCO'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "CARRAS",
        "CARRASCO",
        ['ASSETS IN CARRASCO', 'SERVERS IN CARRASCO', 'ALL NETWORK DEVICES IN CARRASCO', 'PCs IN CARRASCO'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "MORALES",
        "MORALES",
        ['ASSETS IN MORALES', 'SERVERS IN MORALES', 'ALL NETWORK DEVICES IN MORALES', 'PCs IN MORALES'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "NEXTENG",
        "NEXTENGO",
        ['ASSETS IN NEXTENGO', 'SERVERS IN NEXTENGO', 'ALL NETWORK DEVICES IN NEXTENGO', 'PCs IN NEXTENGO'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "NEZA",
        "NEZA",
        ['ASSETS IN NEZA', 'SERVERS IN NEZA', 'ALL NETWORK DEVICES IN NEZA', 'PCs IN NEZA'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "PORTALE",
        "PORTALES",
        ['ASSETS IN PORTALES', 'SERVERS IN PORTALES', 'ALL NETWORK DEVICES IN PORTALES', 'PCs IN PORTALES'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "L_ARA",
        "LAGO ARAGON",
        ['ASSETS IN LAGO ARAGON', 'SERVERS IN LAGO ARAGON', 'ALL NETWORK DEVICES IN LAGO ARAGON', 'PCs IN LAGO ARAGON'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "MALINCH",
        "MALINCHE",
        ['ASSETS IN MALINCHE', 'SERVERS IN MALINCHE', 'ALL NETWORK DEVICES IN MALINCHE', 'PCs IN MALINCHE'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "VALLAR",
        "PTO VALLARTA",
        ['ASSETS IN PTO VALLARTA', 'SERVERS IN PTO VALLARTA', 'ALL NETWORK DEVICES IN PTO VALLARTA', 'PCs IN PTO VALLARTA'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "URUAPAN",
        "URUAPAN",
        ['ASSETS IN URUAPAN', 'SERVERS IN URUAPAN', 'ALL NETWORK DEVICES IN URUAPAN', 'PCs IN URUAPAN'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "TLAQUE",
        "TLAQUEPAQUE",
        ['ASSETS IN TLAQUEPAQUE', 'SERVERS IN TLAQUEPAQUE', 'ALL NETWORK DEVICES IN TLAQUEPAQUE', 'PCs IN TLAQUEPAQUE'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "FRESNO",
        "FRESNO",
        ['ASSETS IN FRESNO', 'SERVERS IN FRESNO', 'ALL NETWORK DEVICES IN FRESNO', 'PCs IN FRESNO'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "FUENTES",
        "FUENTES",
        ['ASSETS IN FUENTES', 'SERVERS IN FUENTES', 'ALL NETWORK DEVICES IN FUENTES', 'PCs IN FUENTES'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "MORELIA",
        "MORELIA",
        ['ASSETS IN MORELIA', 'SERVERS IN MORELIA', 'ALL NETWORK DEVICES IN MORELIA', 'PCs IN MORELIA'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "R9",
        "R9",
        ['ASSETS IN R9', 'SERVERS IN R9', 'ALL NETWORK DEVICES IN R9', 'PCs IN R9'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "R5",
        "R5",
        ['ASSETS IN R5', 'SERVERS IN R5', 'ALL NETWORK DEVICES IN R5', 'PCs IN R5'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "R4",
        "R4",
        ['ASSETS IN R4', 'SERVERS IN R4', 'ALL NETWORK DEVICES IN R4', 'PCs IN R4'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "GENERAL",
        "GENERAL",
        ['ASSETS IN GENERAL', 'SERVERS IN GENERAL', 'ALL NETWORK DEVICES IN GENERAL', 'PCs IN GENERAL'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "R1",
        "R1",
        ['ASSETS IN R1', 'SERVERS IN R1', 'ALL NETWORK DEVICES IN R1', 'PCs IN R1'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
    Central(
        "R2",
        "R2",
        ['ASSETS IN R2', 'SERVERS IN R2', 'ALL NETWORK DEVICES IN R2', 'PCs IN R2'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
]
