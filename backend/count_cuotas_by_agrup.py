import asyncio
from app.scripts.importacion.mysql_helper import get_mysql_connection

async def check():
    # Missing codes that don't exist in agrupacionterritorial
    missing_codes = [
        '125000', '500000', '800000', '900000', '1000000',
        '1505000', '1511000', '1533000', '1600000', '1805000', '1814000',
        '1820000', '2005000', '2010000', '2012000', '2100000', '2200000',
        '2300000', '2400000', '2505000', '2515000', '2526000', '2539000',
        '2600000', '2700000', '2800000', '2900000', '3000000', '3100000',
        '3200000', '3300000', '3400000'
    ]

    print('Counting cuotas with invalid agrupacion references...\n')

    async with get_mysql_connection() as mysql_conn:
        async with mysql_conn.cursor() as cursor:
            total_invalid = 0

            for code in missing_codes:
                # Pad with leading zeros to match MySQL format (8 digits)
                mysql_code = code.zfill(8)

                await cursor.execute(
                    "SELECT COUNT(*) FROM CUOTAANIOmiembro WHERE CODAGRUPACION = %s",
                    (mysql_code,)
                )
                count = (await cursor.fetchone())[0]

                if count > 0:
                    print(f"  Code '{code}': {count} cuotas")
                    total_invalid += count

            print(f'\nTotal cuotas with invalid agrupacion references: {total_invalid}')

            # Also count the '0' code (Europa Laica Estatal)
            await cursor.execute(
                "SELECT COUNT(*) FROM CUOTAANIOmiembro WHERE CODAGRUPACION = '00000000'"
            )
            count_zero = (await cursor.fetchone())[0]
            print(f"Cuotas with code '0' (Europa Laica Estatal - exists but not imported): {count_zero}")

            print(f'\nTotal potentially recoverable cuotas: {total_invalid + count_zero}')

asyncio.run(check())
