class Central:
    def __init__(self, nombre, queries, file_name):
        self.nombre = nombre
        self.queries = queries
        self.file_name = file_name

centrales = [
    Central(
        "IXTLA",
        [
            "ASSETS IN IXTLAHUACA",
            "SERVERS IN IXTLAHUACA 2",
            "ALL NETWORK DEVICES IN IXTLAHUACA",
            "PCs IN IXTLAHUACA",
        ],
        [
            "TOTAL_ASSETS",
            "SERVERS",
            "NET_DEV",
            "PCs"
        ],
    ),
    Central(
        "CARSO",
        [
            "ASSETS IN CARSO LEGACY",
            "SERVERS IN CARSO",
            "ALL NETWORK DEVICES IN CARSO",
            "PCs IN CARSO LEGACY"
        ],
        [
            "TOTAL_ASSETS",
            "SERVERS",
            "NET_DEV",
            "PCs"
        ],
    ),
    Central(
        "L_ALB",
        [
            "ASSETS IN LAGO ALBERTO",
            "SERVERS IN LAGO ALBERTO",
            "ALL NETWORK DEVICES IN LAGO ALBERTO",
            "PCs IN LAGO ALBERTO"
        ],
        [
            "TOTAL_ASSETS",
            "SERVERS",
            "NET_DEV",
            "PCs"
        ],
    ),
    Central(
        "MALINCHE",
        [
            "ASSETS IN MALINCHE",
            "SERVERS IN MALINCHE",
            "ALL NETWORK DEVICES IN MALINCHE",
            "PCs IN MALINCHE"
        ],
        [
            "TOTAL_ASSETS",
            "SERVERS",
            "NET_DEV",
            "PCs"
        ],
    ),
    Central(
        "SOTELO",
        [
            "ASSETS IN SOTELO",
            "SERVERS IN SOTELO",
            "ALL NETWORK DEVICES IN SOTELO",
            "PCs IN SOTELO"
        ],
        [
            "TOTAL_ASSETS",
            "SERVERS",
            "NET_DEV",
            "PCs"
        ],
    ),
    Central(
        "L_ARA",
        [
            "ASSETS IN LAGO ARAGON",
            "SERVERS IN LAGO ARAGON",
            "ALL NETWORK DEVICES IN LAGO ARAGON",
            "PCs IN LAGO ARAGON"
        ],
        [
            "TOTAL_ASSETS",
            "SERVERS",
            "NET_DEV",
            "PCs"
        ],
    )
]