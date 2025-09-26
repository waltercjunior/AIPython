#!/usr/bin/env python3
"""
Script de teste para demonstrar o funcionamento do sistema WOSA Reports.
"""
import asyncio
import json
import base64
from app.database import SessionLocal
from app.core.services.wosa_service import WOSAFileService, WOSATopicService
from app.schemas.wosa_schemas import WOSAReportData


async def test_wosa_system():
    """Testar o sistema WOSA com dados de exemplo."""
    
    db = SessionLocal()
    
    try:
        print("🧪 Testando sistema WOSA Reports...")
        
        # Carregar dados de exemplo
        with open('sample_wosa_data.json', 'r') as f:
            sample_data = json.load(f)
        
        print(f"📄 Dados carregados: {len(sample_data['topics'])} tópicos")
        
        # Validar estrutura JSON
        wosa_data = WOSAReportData.parse_obj(sample_data)
        print("✅ Estrutura JSON válida")
        
        # Simular upload de arquivo
        file_service = WOSAFileService(db)
        
        # Converter dados para base64 (simulando upload)
        json_content = json.dumps(sample_data)
        content_b64 = base64.b64encode(json_content.encode('utf-8')).decode('utf-8')
        
        from app.schemas.wosa_schemas import FileUploadRequest
        upload_request = FileUploadRequest(
            filename="sample_wosa_report.json",
            user_id="test_user",
            content=content_b64
        )
        
        # Upload do arquivo
        file_record = await file_service.upload_file(upload_request)
        print(f"📁 Arquivo criado: ID {file_record.id}, Nome: {file_record.name}")
        
        # Processar tópicos
        topic_service = WOSATopicService(db)
        result = await topic_service.process_topics(file_record.id, wosa_data.topics)
        
        print(f"📊 Processamento concluído:")
        print(f"   - Tópicos processados: {result.topics_processed}")
        print(f"   - Tópicos criados: {result.topics_created}")
        print(f"   - Tópicos atualizados: {result.topics_updated}")
        
        if result.errors:
            print(f"❌ Erros encontrados:")
            for error in result.errors:
                print(f"   - {error}")
        
        # Atualizar status do arquivo
        file_record.status = "completed"
        file_record.processing_date = file_record.upload_date
        db.commit()
        
        print("✅ Teste concluído com sucesso!")
        
        # Mostrar estatísticas dos tópicos
        from app.infrastructure.database.wosa_models import Topic
        topics = db.query(Topic).filter(Topic.file_id == file_record.id).all()
        
        print(f"\n📈 Estatísticas dos tópicos:")
        for topic in topics:
            print(f"   - {topic.name}")
            print(f"     Ambiente: {topic.environment}")
            print(f"     Produtores: {len(topic.producers)}")
            print(f"     Consumidores: {len(topic.consumers)}")
            print(f"     Mensagens (30d): {topic.messages_last_30d}")
            print(f"     Última mensagem: {topic.last_message_date}")
            print()
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_wosa_system())
