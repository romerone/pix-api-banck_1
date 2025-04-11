from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import logging

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variáveis globais PERSISTENTES
valor_do_pix = 0
valor_pix_maquina2 = 0

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Garante que as variáveis sejam mantidas entre requisições"""
    global valor_do_pix, valor_pix_maquina2
    valor_do_pix = 0  # Inicializa ao iniciar o servidor
    valor_pix_maquina2 = 0
    logger.info("API PIX iniciada - Variáveis resetadas")
    yield
    logger.info("Encerrando API PIX")

load_dotenv()

app = FastAPI(lifespan=lifespan, title="API de Webhook PIX", version="1.0.1")

# CORS (ajuste os origens em produção!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrinja em produção!
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    """Endpoint de status da API"""
    return {
        "message": "API PIX Online", 
        "endpoints": {
            "receber_pix": ["POST /rota-recebimento", "POST /rota-recebimento/pix"],
            "consulta": ["GET /consulta-Maquina01", "GET /consulta-Maquina02"]
        },
        "docs": "/docs"
    }

@app.post("/rota-recebimento")
@app.post("/rota-recebimento/pix")
async def receber_pix(request: Request):
    """Endpoint para receber notificações PIX do Banco EFI"""
    global valor_do_pix, valor_pix_maquina2
    
    try:
        # Verificação de IP (importante para segurança)
        client_ip = request.headers.get('x-forwarded-for', request.client.host)
        allowed_ip = os.getenv("ALLOWED_IP", "34.193.116.226")  # IP do Banco EFI como padrão
        
        if client_ip != allowed_ip:
            logger.warning(f"Tentativa de acesso de IP não autorizado: {client_ip}")
            raise HTTPException(status_code=403, detail="IP não autorizado")

        # Log da rota acessada
        logger.info(f"Requisição recebida na rota: {request.url.path}")

        body = await request.json()
        logger.info(f"Dados recebidos: {body}")

        if "pix" in body:
            valor = float(body["pix"][0]["valor"])
            txid = body["pix"][0]["txid"]

            if txid == "65a8cdcb59b54eac9m01":  # ID para Máquina 1
                valor_do_pix = valor
                logger.info(f"Crédito atualizado (Máquina 1): R$ {valor}")
            elif txid == "flaksdfjaskldfj":  # ID para Máquina 2
                valor_pix_maquina2 = valor
                logger.info(f"Crédito atualizado (Máquina 2): R$ {valor}")
            else:
                logger.warning(f"TxID não reconhecido: {txid}")

        return {"status": "ok", "message": "PIX processado com sucesso"}

    except Exception as e:
        logger.error(f"Erro ao processar PIX: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Erro no processamento: {str(e)}")

@app.get("/consulta-Maquina01")
def consulta_maquina1():
    """Endpoint para consulta do Arduino (Máquina 1)"""
    global valor_do_pix
    pulsos = format_pulses(valor_do_pix)
    valor_do_pix = 0  # Zera após consulta
    logger.info(f"Consulta Máquina 1 - Retornando: {pulsos}")
    return {"retorno": pulsos}

@app.get("/consulta-Maquina02")
def consulta_maquina2():
    """Endpoint para consulta do Arduino (Máquina 2)"""
    global valor_pix_maquina2
    pulsos = format_pulses(valor_pix_maquina2)
    valor_pix_maquina2 = 0
    logger.info(f"Consulta Máquina 2 - Retornando: {pulsos}")
    return {"retorno": pulsos}

def format_pulses(valor: float, ticket: float = 1.0) -> str:
    """Formata o valor para 4 dígitos (ex: 5 → '0005')"""
    if valor > 0 and valor >= ticket:
        creditos = int(valor // ticket)
        return f"{creditos:04d}"
    return "0000"