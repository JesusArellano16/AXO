class Central:
    def __init__(self, nombre, queries, file_name):
        self.nombre = nombre
        self.queries = queries
        self.file_name = file_name

centrales = [
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
    )
]