class Central:
    def __init__(self, nombre, fullName, queries, file_name):
        self.nombre = nombre
        self.fullName = fullName
        self.queries = queries
        self.file_name = file_name

centrales = [
    Central(
        "CARSO",
        "CARSO",
        ['ASSETS IN CARSO LEGACY', 'SERVERS IN CARSO', 'ALL NETWORK DEVICES IN CARSO', 'PCs IN CARSO LEGACY'],
        ['TOTAL_ASSETS', 'SERVERS', 'NET_DEV', 'PCs'],
    ),
]
