#!/usr/bin/env python3
"""
Script para inicializar dados básicos do sistema WOSA.
"""
import asyncio
from app.database import SessionLocal
from app.infrastructure.database.wosa_models import (
    ApplicationComponent, InterfaceType, Interface
)


async def init_basic_data():
    """Inicializar dados básicos do sistema."""
    db = SessionLocal()
    
    try:
        print("Inicializando dados básicos do sistema WOSA...")
        
        # Criar Application Components básicos
        app_components = [
            {"name": "VladSystem", "description": "Sistema principal Vlad"},
            {"name": "Kafka", "description": "Sistema de mensageria Kafka"},
            {"name": "Database", "description": "Sistema de banco de dados"},
            {"name": "API Gateway", "description": "Gateway de API"},
        ]
        
        for comp_data in app_components:
            existing = db.query(ApplicationComponent).filter(
                ApplicationComponent.name == comp_data["name"]
            ).first()
            
            if not existing:
                component = ApplicationComponent(**comp_data)
                db.add(component)
                print(f"Criado Application Component: {comp_data['name']}")
        
        # Criar Interface Types básicos
        interface_types = [
            {"name": "REST API", "description": "Interface REST API"},
            {"name": "Kafka Topic", "description": "Tópico Kafka"},
            {"name": "Database Connection", "description": "Conexão com banco de dados"},
            {"name": "Message Queue", "description": "Fila de mensagens"},
        ]
        
        for type_data in interface_types:
            existing = db.query(InterfaceType).filter(
                InterfaceType.name == type_data["name"]
            ).first()
            
            if not existing:
                interface_type = InterfaceType(**type_data)
                db.add(interface_type)
                print(f"Criado Interface Type: {type_data['name']}")
        
        # Commit das alterações
        db.commit()
        print("Dados básicos inicializados com sucesso!")
        
    except Exception as e:
        print(f"Erro ao inicializar dados básicos: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(init_basic_data())
