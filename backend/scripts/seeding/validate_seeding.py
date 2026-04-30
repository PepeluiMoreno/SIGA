import asyncio
from sqlalchemy import select, func

from app.core.database import get_session
from app.modulos.administracion.modelos import Transaccion, Rol, Usuario, roles_transacciones


async def validate():
    """Validar que el seeding se haya ejecutado correctamente"""
    
    print("🔍 Validando datos iniciales...\n")
    
    async with get_session() as session:
        # Contar transacciones
        stmt = select(func.count()).select_from(Transaccion)
        result = await session.execute(stmt)
        count_trans = result.scalar()
        print(f"✅ Transacciones: {count_trans}")
        
        # Contar roles
        stmt = select(func.count()).select_from(Rol)
        result = await session.execute(stmt)
        count_roles = result.scalar()
        print(f"✅ Roles: {count_roles}")
        
        # Contar usuarios
        stmt = select(func.count()).select_from(Usuario)
        result = await session.execute(stmt)
        count_users = result.scalar()
        print(f"✅ Usuarios: {count_users}")
        
        # Contar asignaciones
        stmt = select(func.count()).select_from(roles_transacciones)
        result = await session.execute(stmt)
        count_asignaciones = result.scalar()
        print(f"✅ Asignaciones rol-transacción: {count_asignaciones}")
        
        # Verificar rol SUPERADMIN
        stmt = select(Rol).where(Rol.codigo == 'SUPERADMIN')
        result = await session.execute(stmt)
        superadmin = result.scalar_one_or_none()
        
        if superadmin:
            print(f"\n✅ Rol SUPERADMIN encontrado")
            print(f"   Transacciones asignadas: {len(superadmin.transacciones)}")
        else:
            print("\n❌ Rol SUPERADMIN NO encontrado")
        
        # Verificar usuario admin
        stmt = select(Usuario).where(Usuario.username == 'admin')
        result = await session.execute(stmt)
        admin_user = result.scalar_one_or_none()
        
        if admin_user:
            print(f"\n✅ Usuario admin encontrado")
            print(f"   Email: {admin_user.email}")
            print(f"   Roles: {[r.nombre for r in admin_user.roles]}")
        else:
            print("\n❌ Usuario admin NO encontrado")
    
    print("\n✅ Validación completada")


if __name__ == "__main__":
    asyncio.run(validate())