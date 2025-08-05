class Central:
    def __init__(self, nombre, queries, file_name):
        self.nombre = nombre
        self.queries = queries
        self.file_name = file_name

centrales = [
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
    )
]