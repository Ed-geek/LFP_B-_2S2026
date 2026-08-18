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

# ------------------------------------------------------------
# PROCESAMIENTO Y MÉTRICAS
# ------------------------------------------------------------

def procesar_todos_intentos(tableros, intentos):
    """
    Valida todos los intentos y los asocia con sus tableros.
    Devuelve un diccionario con estadísticas.
    """
    # Crear un diccionario para acceder rápido a los tableros por id
    tableros_dict = {t.id: t for t in tableros}

    resultados = {
        'intentos_validados': [],
        'estadisticas_sudokus': {},
        'estadisticas_jugadores': {}
    }

    for intento in intentos:
        tablero = tableros_dict.get(intento.id_sudoku)
        if tablero is None:
            print(f"Advertencia: Intento con id_sudoku {intento.id_sudoku} no encontrado.")
            continue
        # Validar
        porcentaje = validar_intento(tablero, intento)
        # Guardar referencia al tablero y al jugador después
        intento.tablero = tablero
        resultados['intentos_validados'].append(intento)

    return resultados


def calcular_metricas(resultados):
    """
    A partir de los intentos validados, calcula:
    - Por cada sudoku: cantidad de intentos, tiempo promedio, tasa de éxito.
    - Por cada jugador: cantidad de tableros intentados, porcentaje de validez promedio,
      tiempo promedio, cantidad de resueltos perfectamente.
    - Top 10 mejores tiempos (entre resueltos correctamente).
    """
    intentos = resultados['intentos_validados']

    # ---- Estadísticas por Sudoku ----
    stats_sudoku = {}
    for intento in intentos:
        id_s = intento.id_sudoku
        if id_s not in stats_sudoku:
            stats_sudoku[id_s] = {
                'total_intentos': 0,
                'suma_tiempos': 0,
                'exitos': 0,  # resueltos correctamente
                'tiempos_exitos': []  # para top 10
            }
        stats_sudoku[id_s]['total_intentos'] += 1
        stats_sudoku[id_s]['suma_tiempos'] += intento.tiempo
        if intento.resuelto_correctamente:
            stats_sudoku[id_s]['exitos'] += 1
            stats_sudoku[id_s]['tiempos_exitos'].append((intento.carnet, intento.tiempo))

    # Calcular promedios y tasas
    for id_s, data in stats_sudoku.items():
        total = data['total_intentos']
        data['tiempo_promedio'] = data['suma_tiempos'] / total if total > 0 else 0
        data['tasa_exito'] = (data['exitos'] / total) * 100 if total > 0 else 0

    # ---- Estadísticas por Jugador ----
    stats_jugador = {}
    for intento in intentos:
        carnet = intento.carnet
        if carnet not in stats_jugador:
            stats_jugador[carnet] = {
                'total_intentos': 0,
                'suma_tiempos': 0,
                'suma_validez': 0.0,
                'exitos_perfectos': 0,
                'tableros_distintos': set()
            }
        stats_jugador[carnet]['total_intentos'] += 1
        stats_jugador[carnet]['suma_tiempos'] += intento.tiempo
        stats_jugador[carnet]['suma_validez'] += intento.porcentaje_validez
        stats_jugador[carnet]['tableros_distintos'].add(intento.id_sudoku)
        if intento.resuelto_correctamente:
            stats_jugador[carnet]['exitos_perfectos'] += 1

    # Calcular promedios
    for carnet, data in stats_jugador.items():
        total = data['total_intentos']
        data['validez_promedio'] = data['suma_validez'] / total if total > 0 else 0
        data['tiempo_promedio'] = data['suma_tiempos'] / total if total > 0 else 0
        data['cantidad_tableros'] = len(data['tableros_distintos'])

    # ---- Top 10 mejores tiempos (entre exitosos) ----
    top_tiempos = []
    for intento in intentos:
        if intento.resuelto_correctamente:
            top_tiempos.append((intento.carnet, intento.id_sudoku, intento.tiempo))
    # Ordenar por tiempo (menor a mayor)
    top_tiempos.sort(key=lambda x: x[2])
    top_10 = top_tiempos[:10]

    return stats_sudoku, stats_jugador, top_10


#  -----------------------------------------------------------
# GENERACIÓN DE REPORTES HTML
# ------------------------------------------------------------

def generar_reporte_sudoku(stats_sudoku, tableros):
    """Genera reporte1: Resumen por Sudoku."""
    html = """
    <html>
    <head><meta charset="UTF-8"><title>Resumen por Sudoku</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        table { border-collapse: collapse; width: 80%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
        th { background-color: #4CAF50; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
    </style>
    </head>
    <body>
    <h1>Resumen por Sudoku</h1>
    <table>
        <tr><th>ID</th><th>Dificultad</th><th>Intentos</th><th>Tiempo Promedio (seg)</th><th>Tasa Éxito (%)</th></tr>
    """
    # Ordenar por ID
    for id_s in sorted(stats_sudoku.keys()):
        data = stats_sudoku[id_s]
        # Buscar dificultad en tableros
        dificultad = "N/A"
        for t in tableros:
            if t.id == id_s:
                dificultad = t.dificultad
                break
        html += f"""
        <tr>
            <td>{id_s}</td>
            <td>{dificultad}</td>
            <td>{data['total_intentos']}</td>
            <td>{data['tiempo_promedio']:.2f}</td>
            <td>{data['tasa_exito']:.2f}</td>
        </tr>
        """
    html += """
    </table>
    </body>
    </html>
    """
    return html


def generar_reporte_jugador(stats_jugador, jugadores):
    """Genera reporte2: Rendimiento por Jugador."""
    html = """
    <html>
    <head><meta charset="UTF-8"><title>Rendimiento por Jugador</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        table { border-collapse: collapse; width: 90%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
        th { background-color: #008CBA; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
    </style>
    </head>
    <body>
    <h1>Rendimiento por Jugador</h1>
    <table>
        <tr><th>Carnet</th><th>Nombre</th><th>Nivel</th><th>Tableros Intentados</th>
            <th>Validez Promedio (%)</th><th>Tiempo Promedio (seg)</th><th>Resueltos Perfectos</th></tr>
    """
    # Crear diccionario de jugadores por carnet
    jugadores_dict = {j.carnet: j for j in jugadores}
    for carnet in sorted(stats_jugador.keys()):
        data = stats_jugador[carnet]
        jugador = jugadores_dict.get(carnet)
        nombre = jugador.nombre_completo() if jugador else "Desconocido"
        nivel = jugador.nivel if jugador else "N/A"
        html += f"""
        <tr>
            <td>{carnet}</td>
            <td>{nombre}</td>
            <td>{nivel}</td>
            <td>{data['cantidad_tableros']}</td>
            <td>{data['validez_promedio']:.2f}</td>
            <td>{data['tiempo_promedio']:.2f}</td>
            <td>{data['exitos_perfectos']}</td>
        </tr>
        """
    html += """
    </table>
    </body>
    </html>
    """
    return html


def generar_reporte_top10(top_10, jugadores, tableros):
    """Genera reporte3: Top 10 Mejores Tiempos."""
    html = """
    <html>
    <head><meta charset="UTF-8"><title>Top 10 Mejores Tiempos</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        table { border-collapse: collapse; width: 70%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
        th { background-color: #f44336; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
    </style>
    </head>
    <body>
    <h1>Top 10 Mejores Tiempos (Resueltos Correctamente)</h1>
    <table>
        <tr><th>Posición</th><th>Carnet</th><th>Nombre</th><th>ID Sudoku</th><th>Dificultad</th><th>Tiempo (seg)</th></tr>
    """
    # Preparar diccionarios
    jugadores_dict = {j.carnet: j for j in jugadores}
    tableros_dict = {t.id: t for t in tableros}

    pos = 1
    for carnet, id_s, tiempo in top_10:
        jugador = jugadores_dict.get(carnet)
        nombre = jugador.nombre_completo() if jugador else "Desconocido"
        tablero = tableros_dict.get(id_s)
        dificultad = tablero.dificultad if tablero else "N/A"
        html += f"""
        <tr>
            <td>{pos}</td>
            <td>{carnet}</td>
            <td>{nombre}</td>
            <td>{id_s}</td>
            <td>{dificultad}</td>
            <td>{tiempo}</td>
        </tr>
        """
        pos += 1

    html += """
    </table>
    </body>
    </html>
    """
    return html
