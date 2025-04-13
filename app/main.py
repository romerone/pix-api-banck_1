from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime
import pytz
import os

# Carrega variáveis de ambiente
load_dotenv()

# Supabase config
SUPABASE_URL = "https://mgvzikxtfmaoaozgtzyh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1ndnppa3h0Zm1hb2Fvemd0enloIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ0MTMxMTAsImV4cCI6MjA1OTk4OTExMH0.Tadv7KO68vy0SKgr8OyaP9KRjTB9G1yRmLDc5nIjlg8"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Variáveis globais persistentes
valor_do_pix = 0
valor_pix_maquina2 = 0

@asynccontextmanager
async def lifespan(app: FastAPI):
    global valor_do_pix, valor_pix_maquina2
    valor_do_pix = 0
    valor_pix_maquina2 = 0
    yield

app = FastAPI(lifespan=lifespan)

# Libera CORS (ajuste para domínios específicos em produção)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "API PIX Online",
        "endpoints": {
            "receber_pix": "POST /rota-recebimento/pix",
            "consulta": "GET /consulta-Maquina01"
        },
        "docs": "/docs"
    }

@app.post("/rota-recebimento/pix")
async def receber_pix(request: Request):
    global valor_do_pix, valor_pix_maquina2

    try:
        body = await request.json()
        print("Recebido:", body)

        if "pix" in body:
            pix_data = body["pix"][0]
            valor = float(pix_data["valor"])
            txid = pix_data["txid"]

            # Acessa o nome do pagador
            remetente = pix_data.get("gnExtras", {}).get("pagador", {}).get("nome", "Desconhecido")

            # Determina a máquina
            if txid == "65a8cdcb59b54eac9m01":
                valor_do_pix = valor
                maquina = "maquina01"
                print(f"Crédito atualizado (Máquina 1): R$ {valor}")
            elif txid == "flaksdfjaskldfj":
                valor_pix_maquina2 = valor
                maquina = "maquina02"
                print(f"Crédito atualizado (Máquina 2): R$ {valor}")
            else:
                maquina = "desconhecida"

            # Data/hora local (Brasília)
            horario_local = datetime.now(pytz.timezone("America/Sao_Paulo")).isoformat()

            # Insere no Supabase
            supabase.table("transacoes_pix").insert({
                "valor": valor,
                "remetente": remetente,
                "txid": txid,
                "maquina": maquina,
                "data": horario_local
            }).execute()

        return {"status": "ok"}

    except Exception as e:
        print("Erro:", str(e))
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/consulta-Maquina01")
def consulta_maquina1():
    global valor_do_pix
    pulsos = format_pulses(valor_do_pix)
    valor_do_pix = 0
    return {"retorno": pulsos}

@app.get("/consulta-Maquina02")
def consulta_maquina2():
    global valor_pix_maquina2
    pulsos = format_pulses(valor_pix_maquina2)
    valor_pix_maquina2 = 0
    return {"retorno": pulsos}

def format_pulses(valor: float, ticket: float = 1.0) -> str:
    """Formata o valor em múltiplos de R$1, com 4 dígitos (ex: '0005')"""
    if valor > 0 and valor >= ticket:
        creditos = int(valor // ticket)
        return f"{creditos:04d}"
    return "0000"
