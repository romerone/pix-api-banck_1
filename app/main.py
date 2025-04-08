from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import time

# Variáveis globais
valor_do_pix = 0
valor_pix_maquina2 = 0
last_active = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia estado da API e evita timeout"""
    global last_active
    last_active = time.time()
    yield
    print("API encerrada")

app = FastAPI(lifespan=lifespan)

# CORS (ajuste para produção)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Endpoint para health checks do Railway"""
    global last_active
    last_active = time.time()
    return {"status": "online", "last_active": last_active}

@app.post("/rota-recebimento")
async def receber_pix(request: Request):
    global valor_do_pix, valor_pix_maquina2, last_active
    last_active = time.time()
    
    # Sua lógica existente aqui...
    # (Mantive o código original, só adicionei o last_active)

@app.get("/consulta-Maquina01")
async def consulta_maquina1():
    global valor_do_pix, last_active
    last_active = time.time()
    # Sua lógica existente...
    return {"retorno": format_pulses(valor_do_pix)}

def format_pulses(valor: float) -> str:
    """Formatação para 4 dígitos"""
    return f"{int(valor):04d}" if valor > 0 else "0000"git add railway.jsonuvicorn app.main:app