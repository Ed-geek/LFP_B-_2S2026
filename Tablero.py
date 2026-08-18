import os

# ------------------------------------------------------------
# CLASES
# ------------------------------------------------------------


class Tablero:
    """
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

class Jugador:
    """
    Representa un jugador.
    """
    def __init__(self, carnet, nombre, apellido, nivel):
        self.carnet = carnet
        self.nombre = nombre
        self.apellido = apellido
        self.nivel = nivel

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


class Intento:
    """
    Representa el intento de un jugador en un sudoku.
    """
    def __init__(self, carnet, id_sudoku, solucion_cadena, tiempo, fecha):
        self.carnet = carnet
        self.id_sudoku = id_sudoku
        self.tiempo = int(tiempo)
        self.fecha = fecha
        self.matriz = self._cadena_a_matriz(solucion_cadena)
        # Atributos que se llenarán después de validar
        self.porcentaje_validez = None
        self.resuelto_correctamente = False
        self.detalle_validacion = {}  # Para depuración

    def _cadena_a_matriz(self, cadena):
        if len(cadena) != 81:
            raise ValueError("La cadena de solución debe tener 81 caracteres")
        matriz = []
        for i in range(9):
            fila = []
            for j in range(9):
                fila.append(int(cadena[i*9 + j]))
            matriz.append(fila)
        return matriz

    def obtener_valor(self, fila, col):
        return self.matriz[fila][col]
    

# ------------------------------------------------------------
# FUNCIONES DE VALIDACION
# ------------------------------------------------------------

def es_conjunto_valido(lista_numeros):
    """
    Verifica que una lista de 9 números (puede contener 0) cumpla con la regla:
    los números del 1 al 9 no se repiten. Los ceros se ignoran.
    """
    vistos = set()
    for num in lista_numeros:
        if num != 0:
            if num < 1 or num > 9:
                return False
            if num in vistos:
                return False
            vistos.add(num)
    return True


def validar_intento(tablero, intento):

    """
    Valida un intento contra el tablero original.
    Llena los atributos porcentaje_validez y resuelto_correctamente del intento.
    Retorna el porcentaje de validez (float).
    """

    # 1. Verificar que las pistas no hayan sido modificadas
    pistas_modificadas = False
    for i in range(9):
        for j in range(9):
            if tablero.es_pista(i, j):
                if intento.obtener_valor(i, j) != tablero.obtener_valor(i, j):
                    pistas_modificadas = True
                    break

        if pistas_modificadas:
            break

    # 2. Validar filas, columnas y cajas
    filas_validas = 0
    columnas_validas = 0
    cajas_validas = 0

    # Validar filas
    for i in range(9):
        if es_conjunto_valido(intento.matriz[i]):
            filas_validas += 1

    # Validar columnas
    for j in range(9):
        columna = [intento.matriz[i][j] for i in range(9)]
        if es_conjunto_valido(columna):
            columnas_validas += 1

    # Validar cajas 3x3
    for inicio_fila in range(0, 9, 3):
        for inicio_col in range(0, 9, 3):
            caja = []
            for i in range(inicio_fila, inicio_fila+3):
                for j in range(inicio_col, inicio_col+3):
                    caja.append(intento.matriz[i][j])
            if es_conjunto_valido(caja):
                cajas_validas += 1


    total_validas = filas_validas + columnas_validas + cajas_validas
    porcentaje = (total_validas / 27) * 100

    # Determinar si está resuelto correctamente
    correcto = (porcentaje == 100.0 and not pistas_modificadas)

    # Guardar resultados en el objeto intento
    intento.porcentaje_validez = porcentaje
    intento.resuelto_correctamente = correcto
    intento.detalle_validacion = {
        'filas_validas': filas_validas,
        'columnas_validas': columnas_validas,
        'cajas_validas': cajas_validas,
        'pistas_modificadas': pistas_modificadas
    }

    return porcentaje

# ------------------------------------------------------------
# CARGA DE ARCHIVOS
# ------------------------------------------------------------

def cargar_sudokus(ruta):
    """Lee el archivo sudokus.lfp y devuelve una lista de objetos Tablero."""
    tableros = []
    with open(ruta, 'r', encoding='utf-8') as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            partes = linea.split(',')
            if len(partes) >= 3:
                id_sudoku = int(partes[0].strip())
                dificultad = partes[1].strip()
                cadena = partes[2].strip()
                # Si la cadena tiene espacios, los eliminamos
                cadena = cadena.replace(' ', '')
                tablero = Tablero(id_sudoku, dificultad, cadena)
                tableros.append(tablero)
    return tableros


def cargar_jugadores(ruta):
    """Lee el archivo jugadores.lfp y devuelve una lista de objetos Jugador."""
    jugadores = []
    with open(ruta, 'r', encoding='utf-8') as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            partes = linea.split(',')
            if len(partes) >= 4:
                carnet = int(partes[0].strip())
                nombre = partes[1].strip()
                apellido = partes[2].strip()
                nivel = partes[3].strip()
                jugador = Jugador(carnet, nombre, apellido, nivel)
                jugadores.append(jugador)
    return jugadores


def cargar_intentos(ruta):
    """Lee el archivo intentos.lfp y devuelve una lista de objetos Intento."""
    intentos = []
    with open(ruta, 'r', encoding='utf-8') as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            partes = linea.split(',')
            if len(partes) >= 5:
                carnet = int(partes[0].strip())
                id_sudoku = int(partes[1].strip())
                solucion = partes[2].strip().replace(' ', '')
                tiempo = int(partes[3].strip())
                fecha = partes[4].strip()
                intento = Intento(carnet, id_sudoku, solucion, tiempo, fecha)
                intentos.append(intento)
    return intentos
