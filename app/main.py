from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

# Variáveis globais PERSISTENTES
valor_do_pix = 0
valor_pix_maquina2 = 0

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Garante que as variáveis sejam mantidas entre requisições"""
    global valor_do_pix, valor_pix_maquina2
    valor_do_pix = 0  # Inicializa ao iniciar o servidor
    valor_pix_maquina2 = 0
    yield
    # Limpa ao encerrar (opcional)

load_dotenv()

app = FastAPI(lifespan=lifespan)  # Habilita o gerenciamento de estado

# CORS (ajuste os origens em produção!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/rota-recebimento")
async def receber_pix(request: Request):
    global valor_do_pix, valor_pix_maquina2
    
    try:
        body = await request.json()
        print(f"Dados recebidos:", body)  # Log completo

        # Aceita ambos os formatos
        if "pix" in body:  # Formato do Banco EFI
            pix_data = body["pix"][0]
            valor = float(pix_data["valor"])
            txid = pix_data["txid"]
        else:  # Formato simplificado para testes
            valor = float(body["valor"])
            txid = body["txid"]

        print(f"Valor processado: {valor}, TXID: {txid}")  # Novo log

        if txid == "70dcb59b94eac9ccbm01":
            valor_do_pix = valor
            print(f"Crédito atualizado (Máquina 1): R$ {valor}")
        elif txid == "flaksdfjaskldfj":
            valor_pix_maquina2 = valor

        return {"status": "ok"}

    except Exception as e:
        print("Erro:", str(e))
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/consulta-Maquina01")
def consulta_maquina1():
    global valor_do_pix
    pulsos = format_pulses(valor_do_pix)
    valor_do_pix = 0  # Zera após consulta
    return {"retorno": pulsos}

@app.get("/consulta-rafael-mac02-lojaFulanoDeTal")
def consulta_maquina2():
    global valor_pix_maquina2
    pulsos = format_pulses(valor_pix_maquina2)
    valor_pix_maquina2 = 0
    return {"retorno": pulsos}

def format_pulses(valor: float, ticket: float = 1.0) -> str:
    """Formata o valor para 4 dígitos (ex: 5 → '0005')"""
    if valor > 0 and valor >= ticket:
        creditos = int(valor // ticket)
        return f"{creditos:04d}"
    return "0000"