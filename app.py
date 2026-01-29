import MetaTrader5 as mt5
from src.utils.configs import settings 
import sys

print("🔄 Iniciando teste com Pydantic v2...")
print(f"📂 Caminho configurado: {settings.MT5_PATH}")
print(f"👤 Conta configurada: {settings.MT5_LOGIN}")

# Inicializa usando os dados validados pelo Pydantic
if not mt5.initialize(path=settings.MT5_PATH):
    print("❌ Falha na inicialização com caminho específico. Tentando padrão...")
    if not mt5.initialize():
        print("❌ Erro crítico no MT5:", mt5.last_error())
        sys.exit()

# Login explícito (opcional, mas bom para garantir que é a conta do .env)
# O Pydantic garante que settings.MT5_LOGIN é um número (int), então não precisamos converter
authorized = mt5.login(
    settings.MT5_LOGIN, 
    password=settings.MT5_PASSWORD, 
    server=settings.MT5_SERVER
)

if authorized:
    print(f"✅ Login autorizado na conta {settings.MT5_LOGIN}")
    account_info = mt5.account_info()
    print(f"💰 Saldo Atual: {account_info.balance}")
    
    # Teste do Símbolo
    symbol = settings.SYMBOL
    selected = mt5.symbol_select(symbol, True) # Garante que está visível no Market Watch
    if not selected:
        print(f"⚠️ Erro: Não foi possível selecionar o par {symbol}")
    else:
        tick = mt5.symbol_info_tick(symbol)
        print(f"📊 Cotação {symbol}: Compra {tick.ask} / Venda {tick.bid}")
else:
    print(f"❌ Falha no login: {mt5.last_error()}")

mt5.shutdown()