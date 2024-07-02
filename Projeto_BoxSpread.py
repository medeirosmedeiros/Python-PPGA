import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import MetaTrader5 as mt5


# Obter os dados das opções
subjacente = 'ITUB4'  
vencimento = '2024-09-20' 


# Função para obter os dados das opções e filtrar
def optionchaindate(subjacente, vencimento):
    url = f'https://opcoes.net.br/listaopcoes/completa?idAcao={subjacente}&listarVencimentos=false&cotacoes=true&vencimentos={vencimento}'
    r = requests.get(url).json()
    x = ([subjacente, vencimento, i[0].split('_')[0], i[2], i[3], i[5], i[8], i[9], i[10]] for i in r['data']['cotacoesOpcoes'])
    df = pd.DataFrame(x, columns=['subjacente', 'vencimento', 'ativo', 'tipo', 'modelo', 'strike', 'preco', 'negocios', 'volume'])
    df['negocios'] = pd.to_numeric(df['negocios'], errors='coerce')
    df = df[(df['modelo'] == 'E') & (df['negocios'] > 10)]
    return df

df = optionchaindate(subjacente, vencimento)

# Mostrar as primeiras linhas do dataframe filtrado
print(df.head())

# Função para calcular o lucro e prejuízo do Box Spread
def calculate_box_spread_profit(call_options, put_options, strike_prices, underlying_prices):
    call_premiums = call_options['preco'].astype(float).tolist()
    put_premiums = put_options['preco'].astype(float).tolist()
    
    # Lucro e Prejuízo para Bull Spread com Calls
    bull_profit = np.where(underlying_prices <= strike_prices[0], 0,
                           np.where(underlying_prices <= strike_prices[1], underlying_prices - strike_prices[0],
                                    strike_prices[1] - strike_prices[0]))
    bull_profit = bull_profit - call_premiums[0] + call_premiums[1]
    
    # Lucro e Prejuízo para Bear Spread com Puts
    bear_profit = np.where(underlying_prices <= strike_prices[0], strike_prices[1] - strike_prices[0],
                           np.where(underlying_prices <= strike_prices[1], strike_prices[1] - underlying_prices,
                                    0))
    bear_profit = bear_profit + put_premiums[0] - put_premiums[1]
    
    # Combinação do Bull Spread com o Bear Spread para criar o Box Spread
    box_profit = bull_profit + bear_profit
    return box_profit

# Preços para o eixo x (variação no preço do ativo subjacente)
underlying_prices = np.arange(0, 80, 0.5)

# Encontrar a combinação de strikes que maximiza o lucro do Box Spread
max_profit = -np.inf
best_strikes = None
best_call_options = None
best_put_options = None

for i in range(len(df)):
    for j in range(i+1, len(df)):
        if df.iloc[i]['tipo'] == 'CALL' and df.iloc[j]['tipo'] == 'CALL':
            for k in range(len(df)):
                for l in range(k+1, len(df)):
                    if df.iloc[k]['tipo'] == 'PUT' and df.iloc[l]['tipo'] == 'PUT':
                        strike_prices = [float(df.iloc[i]['strike']), float(df.iloc[j]['strike'])]
                        call_options = df.iloc[[i, j]]
                        put_options = df.iloc[[k, l]]
                        
                        # Verificar se os strikes são distintos e na ordem correta
                        if strike_prices[0] < strike_prices[1]:
                            box_profit = calculate_box_spread_profit(call_options, put_options, strike_prices, underlying_prices)
                            total_profit = np.sum(box_profit)
                            if total_profit > max_profit:
                                max_profit = total_profit
                                best_strikes = strike_prices
                                best_call_options = call_options
                                best_put_options = put_options

# Plotagem do gráfico de lucros e prejuízos para Bull Spread, Bear Spread e Box Spread
box_profit = calculate_box_spread_profit(best_call_options, best_put_options, best_strikes, underlying_prices)

plt.figure(figsize=(10, 6))
plt.plot(underlying_prices, box_profit, label='Box Spread', color='blue')
plt.xlabel('Preço do Ativo Subjacente')
plt.ylabel('Lucro/Prejuízo')
plt.title('Gráfico de Lucros e Prejuízos - Box Spread')
plt.axvline(32.62, color='black', linestyle='--', linewidth=0.7, label='Spot')  # Ajuste conforme necessário
plt.axvline(best_strikes[0], color='red', linestyle='--', linewidth=0.7, label='Strike 1')
plt.axvline(best_strikes[1], color='blue', linestyle='--', linewidth=0.7, label='Strike 2')
plt.legend()
plt.grid(True)
plt.savefig('box_spread_combined.png')
plt.show()

# Mostrar as melhores opções selecionadas
print(f"Melhores Strikes: {best_strikes}")
print("Melhores Call Options:")
print(best_call_options)
print("Melhores Put Options:")
print(best_put_options)

# Inicializar o MetaTrader 5
if not mt5.initialize():
    print("Falha ao inicializar o MetaTrader 5")
    mt5.shutdown()
    exit()

# Detalhes da sua conta XP (substitua pelos seus detalhes)
account_number = 52157665
password = "01w755R#"
server = "XPMT5-DEMO"

# Conectar à conta
if not mt5.login(account_number, password, server):
    print("Falha ao conectar à conta")
    mt5.shutdown()
    exit()

# Obter o book de ofertas
def get_order_book(symbol):
    if not mt5.market_book_add(symbol):
        print(f"Falha ao adicionar símbolo ao book de ofertas para {symbol}")
        return None
    return mt5.market_book_get(symbol)

# Função para enviar ordens de execução
def send_order(symbol, order_type, volume, price):
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "deviation": 20,
        "magic": 234000,
        "comment": "Box Spread Order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }

    result = mt5.order_send(request)
    return result

# Seus dados de opções selecionadas (exemplo)
best_call_options = ["CALL1", "CALL2"]
best_put_options = ["PUT1", "PUT2"]

# Definir volume e tipo de ordem
volume = 1.0
order_type_buy = mt5.ORDER_TYPE_BUY
order_type_sell = mt5.ORDER_TYPE_SELL

# Executar ordens com base no book de ofertas
def execute_box_spread():
    # Dicionário para armazenar os resultados das ordens
    order_results = {}

    for option in best_call_options:
        order_book = get_order_book(option)
        if order_book:
            best_ask = min(order['price'] for order in order_book if order['type'] == mt5.ORDER_BOOK_TYPE_SELL)
            result = send_order(option, order_type_buy, volume, best_ask)
            order_results[option] = result
            print(f"Ordem de compra enviada para {option}: {result}")

    for option in best_put_options:
        order_book = get_order_book(option)
        if order_book:
            best_bid = max(order['price'] for order in order_book if order['type'] == mt5.ORDER_BOOK_TYPE_BUY)
            result = send_order(option, order_type_sell, volume, best_bid)
            order_results[option] = result
            print(f"Ordem de venda enviada para {option}: {result}")

    return order_results

# Executar todas as ordens do Box Spread
order_results = execute_box_spread()

# Verificar os resultados das ordens
for option, result in order_results.items():
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Falha ao executar a ordem para {option}: {result.retcode}")
    else:
        print(f"Ordem executada com sucesso para {option}")

# Encerrar a conexão
mt5.shutdown()

