"""Script para exportar el schema GraphQL a formato SDL."""

import asyncio
from app.graphql.schema_simple import schema

async def export_schema():
    """Exporta el schema GraphQL a un archivo .graphql"""
    schema_str = str(schema)

    with open('schema.graphql', 'w', encoding='utf-8') as f:
        f.write(schema_str)

    print(f"Schema exportado a schema.graphql ({len(schema_str)} caracteres)")
    print(f"Total de tipos en el schema: {schema_str.count('type ')}")
    print(f"Total de queries: {schema_str.count('Query')}")

if __name__ == '__main__':
    asyncio.run(export_schema())
