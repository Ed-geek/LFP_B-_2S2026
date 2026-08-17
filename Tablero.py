class Tablero:
    """
    Representa un tablero de Sudoku.
    Atributos:
        id: identificador único (int)
        dificultad: str ('Facil', 'Media', 'Dificil', 'Experto')
        matriz: lista de listas 9x9 con números (0 = vacío)
    """
    def __init__(self, id_sudoku, dificultad, cadena):
        self.id = id_sudoku
        self.dificultad = dificultad
        self.matriz = self._cadena_a_matriz(cadena)

    def _cadena_a_matriz(self, cadena):
        """Convierte una cadena de 81 caracteres en matriz 9x9."""
        if len(cadena) != 81:
            raise ValueError("La cadena debe tener 81 caracteres")
        matriz = []
        for i in range(9):
            fila = []
            for j in range(9):
                fila.append(int(cadena[i*9 + j]))
            matriz.append(fila)
        return matriz

    def obtener_valor(self, fila, col):
        """Devuelve el valor en la posición (fila, col) (0-indexado)."""
        return self.matriz[fila][col]

    def es_pista(self, fila, col):
        """Devuelve True si la celda es una pista fija (valor != 0)."""
        return self.matriz[fila][col] != 0