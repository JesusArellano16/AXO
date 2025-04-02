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
            "NETWORK DEVICES IXTLAHUACA",
            "PCs IN IXTLAHUACA"
        ],
        [
            "TOTAL_ASSETS",
            "SERVERS",
            "NET_DEV",
            "PCs"
        ]
    ),
    Central(
        "CARSO",
        [
            "ASSETS IN CARSO LEGACY",
            "SERVERS IN CARSO",
            "NETWORK DEVICES IN CARSO LEGACY",
            "PCs IN CARSO LEGACY"
        ],
        [
            "TOTAL_ASSETS",
            "SERVERS",
            "NET_DEV",
            "PCs"
        ]
    )
]