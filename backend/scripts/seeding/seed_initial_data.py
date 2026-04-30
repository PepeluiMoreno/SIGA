import asyncio
import json
from pathlib import Path
from sqlalchemy import select
from passlib.context import CryptContext

from app.core.database import get_session, engine, Base
from app.modulos.administracion.modelos import (
    Transaccion, Rol, Usuario, roles_transacciones
)
from app.modulos.personas.modelos import Persona

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class DataSeeder:
    """Carga datos iniciales del sistema desde archivos JSON"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "initial_data"
        self.transacciones_map = {}
        self.roles_map = {}
    
    async def seed_all(self, recreate_tables: bool = False):
        """Ejecutar todo el seeding"""
        
        print("🌱 Iniciando carga de datos iniciales...")
        
        if recreate_tables:
            print("⚠️  Recreando todas las tablas...")
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
            print("✅ Tablas recreadas")
        
        await self.seed_transacciones()
        await self.seed_roles()
        await self.seed_roles_transacciones()
        await self.seed_usuario_admin()
        
        print("✅ Carga de datos iniciales completada")
    
    async def seed_transacciones(self):
        """Cargar transacciones desde JSON"""
        
        print("\n📋 Cargando transacciones...")
        
        file_path = self.data_dir / "transacciones.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        async with get_session() as session:
            for trans_data in data['transacciones']:
                # Verificar si ya existe
                stmt = select(Transaccion).where(
                    Transaccion.codigo == trans_data['codigo']
                )
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()
                
                if existing:
                    print(f"  ⏭️  Transacción {trans_data['codigo']} ya existe")
                    self.transacciones_map[trans_data['codigo']] = existing
                    continue
                
                # Crear transacción
                transaccion = Transaccion(**trans_data)
                session.add(transaccion)
                await session.flush()
                
                self.transacciones_map[trans_data['codigo']] = transaccion
                print(f"  ✅ Creada transacción: {trans_data['codigo']} - {trans_data['nombre']}")
            
            await session.commit()
        
        print(f"✅ {len(self.transacciones_map)} transacciones cargadas")
    
    async def seed_roles(self):
        """Cargar roles desde JSON"""
        
        print("\n👥 Cargando roles...")
        
        file_path = self.data_dir / "roles.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        async with get_session() as session:
            for rol_data in data['roles']:
                # Verificar si ya existe
                stmt = select(Rol).where(Rol.codigo == rol_data['codigo'])
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()
                
                if existing:
                    print(f"  ⏭️  Rol {rol_data['codigo']} ya existe")
                    self.roles_map[rol_data['codigo']] = existing
                    continue
                
                # Crear rol
                rol = Rol(**rol_data)
                session.add(rol)
                await session.flush()
                
                self.roles_map[rol_data['codigo']] = rol
                print(f"  ✅ Creado rol: {rol_data['codigo']} - {rol_data['nombre']}")
            
            await session.commit()
        
        print(f"✅ {len(self.roles_map)} roles cargados")
    
    async def seed_roles_transacciones(self):
        """Asignar transacciones a roles desde JSON"""
        
        print("\n🔐 Asignando permisos a roles...")
        
        file_path = self.data_dir / "roles_transacciones.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        async with get_session() as session:
            for rol_codigo, transacciones_codigos in data['asignaciones'].items():
                rol = self.roles_map.get(rol_codigo)
                if not rol:
                    print(f"  ⚠️  Rol {rol_codigo} no encontrado, saltando...")
                    continue
                
                print(f"  📝 Asignando permisos a {rol_codigo}...")
                
                for trans_codigo in transacciones_codigos:
                    transaccion = self.transacciones_map.get(trans_codigo)
                    if not transaccion:
                        print(f"    ⚠️  Transacción {trans_codigo} no encontrada")
                        continue
                    
                    # Verificar si ya existe la asignación
                    stmt = select(roles_transacciones).where(
                        roles_transacciones.c.rol_id == rol.id,
                        roles_transacciones.c.transaccion_id == transaccion.id
                    )
                    result = await session.execute(stmt)
                    existing = result.first()
                    
                    if existing:
                        continue
                    
                    # Crear asignación
                    stmt = roles_transacciones.insert().values(
                        rol_id=rol.id,
                        transaccion_id=transaccion.id
                    )
                    await session.execute(stmt)
                
                await session.commit()
                print(f"  ✅ {len(transacciones_codigos)} permisos asignados a {rol_codigo}")
        
        print("✅ Permisos asignados correctamente")
    
    async def seed_usuario_admin(self):
        """Crear usuario administrador inicial"""
        
        print("\n👤 Creando usuario administrador...")
        
        file_path = self.data_dir / "usuario_admin.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        user_data = data['usuario']
        
        async with get_session() as session:
            # Verificar si ya existe
            stmt = select(Usuario).where(Usuario.username == user_data['username'])
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                print("  ⏭️  Usuario admin ya existe")
                return
            
            # Crear persona
            persona = Persona(
                tipo="PERSONA",
                nombre=user_data['nombre'],
                apellido1=user_data['apellido1'],
                apellido2=user_data.get('apellido2', ''),
                email=user_data['email']
            )
            session.add(persona)
            await session.flush()
            
            # Hash de contraseña
            password_hash = pwd_context.hash(user_data['password'])
            
            # Crear usuario
            usuario = Usuario(
                persona_id=persona.id,
                username=user_data['username'],
                email=user_data['email'],
                password_hash=password_hash,
                activo=user_data['activo'],
                email_verificado=user_data['email_verificado']
            )
            session.add(usuario)
            await session.flush()
            
            # Asignar roles
            for rol_codigo in user_data['roles']:
                rol = self.roles_map.get(rol_codigo)
                if rol:
                    usuario.roles.append(rol)
            
            await session.commit()
            
            print(f"  ✅ Usuario admin creado")
            print(f"     Username: {user_data['username']}")
            print(f"     Email: {user_data['email']}")
            print(f"     Password: {user_data['password']}")
            print(f"     ⚠️  CAMBIAR CONTRASEÑA INMEDIATAMENTE")


async def main():
    """Función principal de seeding"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Cargar datos iniciales del sistema')
    parser.add_argument(
        '--recreate',
        action='store_true',
        help='Recrear todas las tablas (⚠️ BORRA TODOS LOS DATOS)'
    )
    
    args = parser.parse_args()
    
    if args.recreate:
        confirm = input(
            "⚠️  ADVERTENCIA: Esto borrará TODOS los datos. "
            "¿Estás seguro? (escribe 'SI' para confirmar): "
        )
        if confirm != "SI":
            print("❌ Operación cancelada")
            return
    
    seeder = DataSeeder()
    await seeder.seed_all(recreate_tables=args.recreate)


if __name__ == "__main__":
    asyncio.run(main())