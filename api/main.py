from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import logging
import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# Importações locais (serão implementadas posteriormente)
from schemas import SentimentRequest, SentimentResponse, BatchRequest, BatchResponse
from models.model_handler import ModelHandler

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("sentiment-saas")

# Gerenciador de ciclo de vida
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Inicializando modelos de ML...")
    try:
        app.state.model_handler = ModelHandler()
        app.state.model_handler.load_models()
        logger.info("Modelos carregados com sucesso")
    except Exception as e:
        logger.error(f"Erro ao carregar modelos: {str(e)}")
    yield
    logger.info("Desligando serviço...")

# Definição da API
app = FastAPI(
    title="SentimentSaaS API",
    description="API de análise de sentimentos em redes sociais para pequenas empresas",
    version="0.1.0",
    lifespan=lifespan
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raiz com informações básicas da API"""
    return {
        "name": "SentimentSaaS API",
        "version": "0.1.0",
        "status": "online"
    }

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde para monitoramento"""
    return {"status": "online"}

@app.post("/analyze", response_model=SentimentResponse)
async def analyze_text(request: SentimentRequest):
    """Analisa o sentimento de um único texto"""
    try:
        model_handler = app.state.model_handler
        
        if request.model_type == "fast":
            sentiment, confidence = model_handler.analyze_baseline(request.text)
        else:
            sentiment, confidence = model_handler.analyze_transformer(request.text)
            
        return SentimentResponse(
            text=request.text,
            sentiment=sentiment,
            confidence=confidence,
            model_used=request.model_type
        )
    except Exception as e:
        logger.error(f"Erro na análise: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro no processamento")

@app.post("/analyze/batch", response_model=BatchResponse)
async def analyze_batch(request: BatchRequest):
    """Analisa o sentimento de múltiplos textos em batch"""
    try:
        model_handler = app.state.model_handler
        results = []
        
        for text in request.texts:
            if request.model_type == "fast":
                sentiment, confidence = model_handler.analyze_baseline(text)
            else:
                sentiment, confidence = model_handler.analyze_transformer(text)
                
            results.append(SentimentResponse(
                text=text,
                sentiment=sentiment,
                confidence=confidence,
                model_used=request.model_type
            ))
            
        return BatchResponse(results=results)
    except Exception as e:
        logger.error(f"Erro na análise em batch: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro no processamento em batch")

@app.post("/social/collect")
async def collect_social_data(platform: str, query: str, days_back: int = 7):
    """Coleta dados de redes sociais baseado em query"""
    # Implementação futura
    return {"status": "not_implemented", "message": "Este endpoint será implementado em breve"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)