"""Utilidad para parsear archivos SQL dump de phpMyAdmin/MySQL."""

import re
from typing import Generator, Any
from pathlib import Path


class SQLDumpParser:
    """Parser para archivos SQL dump que extrae INSERT statements."""

    def __init__(self, dump_file_path: str):
        """
        Inicializa el parser con la ruta al archivo dump.

        Args:
            dump_file_path: Ruta al archivo .sql dump
        """
        self.dump_file_path = Path(dump_file_path)
        if not self.dump_file_path.exists():
            raise FileNotFoundError(f"Archivo dump no encontrado: {dump_file_path}")

    def extraer_inserts(self, tabla: str) -> Generator[tuple[Any, ...], None, None]:
        """
        Extrae todos los INSERT statements para una tabla específica.

        Args:
            tabla: Nombre de la tabla (case-insensitive)

        Yields:
            Tupla con los valores de cada INSERT

        Example:
            parser = SQLDumpParser('dump.sql')
            for valores in parser.extraer_inserts('MIEMBRO'):
                print(valores)  # (1, 'Juan', 'Perez', ...)
        """
        # Try multiple encodings
        for encoding in ['utf8', 'latin1', 'cp1252']:
            try:
                with open(self.dump_file_path, 'r', encoding=encoding) as f:
                    lines = f.readlines()
                break
            except UnicodeDecodeError:
                continue
        else:
            # Fallback with error handling
            with open(self.dump_file_path, 'r', encoding='utf8', errors='replace') as f:
                lines = f.readlines()

        # Buscar línea con INSERT INTO tabla
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Verificar si es un INSERT para esta tabla
            insert_pattern = re.compile(
                rf"INSERT\s+INTO\s+[`]?{re.escape(tabla)}[`]?",
                re.IGNORECASE
            )

            if insert_pattern.search(line):
                # Ahora leer las líneas siguientes hasta encontrar un ';'
                values_lines = []
                i += 1
                while i < len(lines):
                    current_line = lines[i]
                    values_lines.append(current_line)

                    if ';' in current_line:
                        break
                    i += 1

                # Combinar líneas y parsear
                values_str = ''.join(values_lines)

                # Parsear múltiples filas: (val1,val2,...),(val1,val2,...)
                for row in self._parse_values(values_str):
                    yield row

            i += 1

    def _parse_values(self, values_str: str) -> Generator[tuple[Any, ...], None, None]:
        """
        Parsea la sección VALUES de un INSERT.

        Args:
            values_str: String con los valores, ej: "(1,'Juan',NULL),(2,'Pedro',NULL)"

        Yields:
            Tupla de valores por cada fila
        """
        # Patrón para capturar cada tupla de valores
        # Maneja strings entre comillas, NULL, números, fechas, etc.
        row_pattern = re.compile(r'\(([^)]+(?:\([^)]*\)[^)]*)*)\)')

        for row_match in row_pattern.finditer(values_str):
            row_str = row_match.group(1)
            valores = self._parse_row(row_str)
            yield tuple(valores)

    def _parse_row(self, row_str: str) -> list[Any]:
        """
        Parsea una fila individual de valores.

        Args:
            row_str: String con valores separados por comas

        Returns:
            Lista de valores parseados (str, int, float, None)
        """
        valores = []
        current_value = ""
        in_string = False
        escape_next = False

        i = 0
        while i < len(row_str):
            char = row_str[i]

            if escape_next:
                current_value += char
                escape_next = False
                i += 1
                continue

            if char == '\\':
                escape_next = True
                i += 1
                continue

            if char == "'" and not in_string:
                in_string = True
                i += 1
                continue

            if char == "'" and in_string:
                in_string = False
                i += 1
                continue

            if char == ',' and not in_string:
                # Fin de valor
                valores.append(self._parse_value(current_value.strip()))
                current_value = ""
                i += 1
                continue

            current_value += char
            i += 1

        # Último valor
        if current_value.strip():
            valores.append(self._parse_value(current_value.strip()))

        return valores

    def _parse_value(self, value_str: str) -> Any:
        """
        Convierte un valor string a su tipo Python correspondiente.

        Args:
            value_str: Valor como string

        Returns:
            Valor convertido (None, int, float, str)
        """
        value_str = value_str.strip()

        # NULL
        if value_str.upper() == 'NULL':
            return None

        # Números
        if value_str.isdigit():
            return int(value_str)

        # Flotantes
        try:
            if '.' in value_str:
                return float(value_str)
        except ValueError:
            pass

        # Strings (ya sin comillas)
        return value_str

    def extraer_estructura_tabla(self, tabla: str) -> dict[str, Any]:
        """
        Extrae la estructura CREATE TABLE de una tabla.

        Args:
            tabla: Nombre de la tabla

        Returns:
            Dict con columnas y tipos
        """
        create_pattern = re.compile(
            rf"CREATE\s+TABLE\s+[`]?{re.escape(tabla)}[`]?\s*\((.+?)\)\s*ENGINE",
            re.IGNORECASE | re.DOTALL
        )

        with open(self.dump_file_path, 'r', encoding='utf8') as f:
            content = f.read()

        match = create_pattern.search(content)
        if not match:
            raise ValueError(f"No se encontró CREATE TABLE para: {tabla}")

        columnas_str = match.group(1)
        columnas = {}

        # Parsear columnas (simplificado)
        for line in columnas_str.split('\n'):
            line = line.strip()
            if line.startswith('`'):
                # Línea de columna
                parts = line.split()
                if len(parts) >= 2:
                    nombre = parts[0].strip('`,')
                    tipo = parts[1]
                    columnas[nombre] = tipo

        return columnas

    def listar_tablas(self) -> list[str]:
        """
        Lista todas las tablas encontradas en el dump.

        Returns:
            Lista de nombres de tablas
        """
        table_pattern = re.compile(
            r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`]?(\w+)[`]?",
            re.IGNORECASE
        )

        tablas = []
        with open(self.dump_file_path, 'r', encoding='utf8') as f:
            for line in f:
                match = table_pattern.search(line)
                if match:
                    tablas.append(match.group(1))

        return tablas


# Ejemplo de uso:
if __name__ == "__main__":
    import asyncio

    async def ejemplo():
        dump_path = r"C:\Users\Jose\dev\AIEL\data\europalaica_com_2026_01_01 apertura de año.sql"
        parser = SQLDumpParser(dump_path)

        print("Tablas en el dump:")
        for tabla in parser.listar_tablas():
            print(f"  - {tabla}")

        print("\nPrimeros 5 registros de AGRUPACIONTERRITORIAL:")
        for i, valores in enumerate(parser.extraer_inserts('AGRUPACIONTERRITORIAL')):
            if i >= 5:
                break
            print(f"  {valores}")

    asyncio.run(ejemplo())
