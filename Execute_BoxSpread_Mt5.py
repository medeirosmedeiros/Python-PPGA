import requests
import pandas as pd
import numpy as np
import MetaTrader5 as mt5

# Função para obter todos os dados de opções e vencimentos disponíveis para um subjacente
def get_all_options():
    url = 'https://opcoes.net.br/listaopcoes/listarAcoes'
    r = requests.get(url).json()
    assets = r['data']['acoes']
    options_data = []

    for asset in assets:
        asset_id = asset['idAcao']
        asset_name = asset['nomeAcao']
        url = f'https://opcoes.net.br/listaopcoes/completa?idAcao={asset_id}&listarVencimentos=true&cotacoes=true'
        r = requests.get(url).json()
        
        for expiration in r['data']['vencimentos']:
            expiration_date = expiration['dataVencimento']
            options = expiration['cotacoesOpcoes']

            for option in options:
                options_data.append({
                    'Ativo': asset_name,
                    'Vencimento': expiration_date,
                    'Código': option[0].split('_')[0],
                    'Tipo': option[2],
                    'Strike': float(option[3]),
                    'Preço': float(option[5])
                })
    
    df = pd.DataFrame(options_data)
    return df

# Função para conectar e obter cotações bid e ask do MetaTrader 5
def get_mt5_quotes(symbol):
    quotes = mt5.symbol_info_tick(symbol)
    if quotes is None:
        print(f"Falha ao obter cotações para {symbol} no MetaTrader 5")
        return None, None
    else:
        return quotes.bid, quotes.ask

# Função para calcular o lucro do Box Spread
def calculate_box_spread_profit(call_strike1, call_strike2, put_strike1, put_strike2, call_premiums, put_premiums, underlying_prices):
    bull_profit = np.where(underlying_prices <= call_strike1, 0,
                           np.where(underlying_prices <= call_strike2, underlying_prices - call_strike1,
                                    call_strike2 - call_strike1))
    bull_profit = bull_profit - call_premiums[0] + call_premiums[1]

    bear_profit = np.where(underlying_prices <= put_strike1, put_strike2 - put_strike1,
                           np.where(underlying_prices <= put_strike2, put_strike2 - underlying_prices,
                                    0))
    bear_profit = bear_profit + put_premiums[0] - put_premiums[1]

    box_profit = bull_profit + bear_profit
    return box_profit

# Função para executar ordens no MetaTrader 5
def execute_orders(symbol_buy, symbol_sell, volume_buy, volume_sell, price_buy, price_sell):
    # Implemente aqui a lógica para enviar as ordens de compra e venda no MT5
    print(f"Ordem de compra para {symbol_buy} enviada com preço {price_buy} e volume {volume_buy}")
    print(f"Ordem de venda para {symbol_sell} enviada com preço {price_sell} e volume {volume_sell}")

# Inicializar o MetaTrader 5
if not mt5.initialize():
    print("Falha ao inicializar o MetaTrader 5")
    mt5.shutdown()
else:
    # Obter todas as opções disponíveis
    options_df = get_all_options()
    
    # Filtrar opções para Box Spread (2 CALL e 2 PUT com strikes diferentes)
    for index, row_call1 in options_df[options_df['Tipo'] == 'CALL'].iterrows():
        for index2, row_call2 in options_df[options_df['Tipo'] == 'CALL'].iterrows():
            for index3, row_put1 in options_df[options_df['Tipo'] == 'PUT'].iterrows():
                for index4, row_put2 in options_df[options_df['Tipo'] == 'PUT'].iterrows():
                    if row_call1['Ativo'] == row_call2['Ativo'] and row_call1['Ativo'] == row_put1['Ativo'] and row_call1['Ativo'] == row_put2['Ativo']:
                        if row_call1['Vencimento'] == row_call2['Vencimento'] and row_call1['Vencimento'] == row_put1['Vencimento'] and row_call1['Vencimento'] == row_put2['Vencimento']:
                            if row_call1['Strike'] != row_call2['Strike'] and row_put1['Strike'] != row_put2['Strike']:
                                symbol_buy = row_call1['Código']
                                symbol_sell = row_put1['Código']
                                volume_buy = 1.0  # Quantidade para compra
                                volume_sell = 1.0  # Quantidade para venda
                                
                                # Obter cotações do MT5
                                bid_buy, ask_buy = get_mt5_quotes(symbol_buy)
                                bid_sell, ask_sell = get_mt5_quotes(symbol_sell)
                                
                                if bid_buy is not None and ask_buy is not None and bid_sell is not None and ask_sell is not None:
                                    # Preços para execução
                                    price_buy = ask_buy
                                    price_sell = bid_sell
                                    
                                    # Calcular lucro potencial do Box Spread
                                    underlying_prices = np.arange(0, 100, 1)  # Variação no preço do ativo subjacente
                                    call_premiums = [row_call1['Preço'], row_call2['Preço']]
                                    put_premiums = [row_put1['Preço'], row_put2['Preço']]
                                    
                                    box_profit = calculate_box_spread_profit(row_call1['Strike'], row_call2['Strike'], 
                                                                            row_put1['Strike'], row_put2['Strike'], 
                                                                            call_premiums, put_premiums, underlying_prices)
                                    
                                    total_profit = np.sum(box_profit)
                                    
                                    # Verificar se o lucro é positivo e solicitar confirmação para execução das ordens
                                    if total_profit > 0:
                                        print(f"Encontrada estrutura lucrativa de Box Spread para {row_call1['Ativo']} - Vencimento {row_call1['Vencimento']}:")
                                        print(f"CALL: {symbol_buy}, PUT: {symbol_sell}")
                                        print(f"Lucro estimado: {total_profit}")
                                        confirmacao = input("Deseja executar as ordens? (sim/não): ").lower()
                                        
                                        if confirmacao == 'sim':
                                            execute_orders(symbol_buy, symbol_sell, volume_buy, volume_sell, price_buy, price_sell)
                                        else:
                                            print("Ordens não executadas.")
                                else:
                                    print("Não foi possível obter cotações do MetaTrader 5 para as opções.")
    
    # Encerrar conexão com o MetaTrader 5
    mt5.shutdown()
