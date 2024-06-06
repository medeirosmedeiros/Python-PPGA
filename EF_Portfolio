import pandas as pd
pd.set_option('display.float_format', lambda x: '%.2f' % x)
import numpy as np
import datetime
from datetime import timedelta
import yfinance as yf
yf.pdr_override()
from pypfopt import EfficientFrontier  # PyPortfolioOpt
from pypfopt import risk_models
from pypfopt import expected_returns
import matplotlib.pyplot as plt
from pypfopt import plotting

# Data
end = datetime.datetime(2024, 3, 6)
start = end - timedelta(days=252)

# Buscar dados das ações
assets = ["ABEV3.SA", "ALPA4.SA", "ARZZ3.SA", "ASAI3.SA", "AZUL4.SA", "B3SA3.SA", "BBAS3.SA", 
          "BBDC3.SA", "BBDC4.SA", "BBSE3.SA", "BEEF3.SA", "BPAC11.SA", "BRAP4.SA", "BRFS3.SA", "BRKM5.SA", 
          "CASH3.SA", "CCRO3.SA", "CIEL3.SA", "CMIG4.SA", "CMIN3.SA", "COGN3.SA", "CPFE3.SA", "CPLE6.SA", 
          "CRFB3.SA", "CSAN3.SA", "CSNA3.SA", "CVCB3.SA", "CYRE3.SA", "DXCO3.SA", "EGIE3.SA", "ELET3.SA", 
          "ELET6.SA", "EMBR3.SA", "ENEV3.SA", "ENGI11.SA", "EQTL3.SA", "EZTC3.SA", "FLRY3.SA", 
          "GGBR4.SA", "GOAU4.SA", "GOLL4.SA", "HAPV3.SA", "HYPE3.SA", "IGTI11.SA", "IRBR3.SA", "ITSA4.SA", 
          "ITUB4.SA", "JBSS3.SA", "KLBN11.SA", "LREN3.SA", "LWSA3.SA", "MGLU3.SA", "MRFG3.SA", "MRVE3.SA", 
          "MULT3.SA", "NTCO3.SA", "PCAR3.SA", "PETR3.SA", "PETR4.SA", "PETZ3.SA", "PRIO3.SA", "RADL3.SA", 
          "RAIL3.SA", "RAIZ4.SA", "RDOR3.SA", "RENT3.SA", "RRRP3.SA", "SANB11.SA", "SBSP3.SA", "SLCE3.SA", 
          "SMTO3.SA", "SOMA3.SA", "SUZB3.SA", "TAEE11.SA", "TIMS3.SA", "TOTS3.SA", "UGPA3.SA", "USIM5.SA", 
          "VALE3.SA", "VBBR3.SA", "VIVT3.SA", "WEGE3.SA", "YDUQ3.SA"]

df = yf.download(assets, start=start, end=end)["Adj Close"]

# Retornos diários
returns = df.pct_change()

# Retornos esperados e matriz de covariância dos retornos dos ativos
mu = expected_returns.mean_historical_return(df)
S = risk_models.sample_cov(df)

# Criar objeto Efficient Frontier (sem restrições de vendas à descoberto)
ef_unconstrained = EfficientFrontier(mu, S)

# Plotar a fronteira eficiente sem restrições
plotting.plot_efficient_frontier(ef_unconstrained, show_assets=True)
plt.title('Fronteira Eficiente sem Restrição de Vendas à Descoberto')
plt.xlabel('Volatilidade')
plt.ylabel('Retorno')
plt.show()

# Obter a carteira de mínima variância sem restrições
min_vol_weights_unconstrained = ef_unconstrained.min_volatility()
cleaned_weights_unconstrained = ef_unconstrained.clean_weights()
print("Carteira de Mínima Variância (Sem Restrição):")
print(cleaned_weights_unconstrained)

# Criar objeto Efficient Frontier (com restrições de vendas à descoberto)
ef_constrained = EfficientFrontier(mu, S)

# Adicionar restrição para evitar vendas à descoberto
ef_constrained.add_constraint(lambda x: x >= 0)

# Plotar a fronteira eficiente com restrições
plotting.plot_efficient_frontier(ef_constrained, show_assets=True)
plt.title('Fronteira Eficiente com Restrição de Vendas à Descoberto')
plt.xlabel('Volatilidade')
plt.ylabel('Retorno')
plt.show()

# Obter a carteira de mínima variância com restrições
min_vol_weights_constrained = ef_constrained.min_volatility()
cleaned_weights_constrained = ef_constrained.clean_weights()
print("Carteira de Mínima Variância (Com Restrição):")
print(cleaned_weights_constrained)

# Definir a taxa livre de risco (DI)
risk_free_rate = 0.1049

# Criar a fronteira eficiente sem restrições de vendas à descoberto
ef_no_constraints = EfficientFrontier(mu, S)
tangency_portfolio_no_constraints = ef_no_constraints.max_sharpe(risk_free_rate=risk_free_rate)
cleaned_weights_no_constraints_tangency = ef_no_constraints.clean_weights()
print("\nCarteira de Tangência sem restrições de vendas à descoberto:")
print(cleaned_weights_no_constraints_tangency)

# Plotar a fronteira eficiente sem restrições de vendas à descoberto
plotting.plot_efficient_frontier(ef_no_constraints, show_assets=True)
plt.title('Fronteira Eficiente sem Restrição de Vendas à Descoberto')
plt.xlabel('Volatilidade')
plt.ylabel('Retorno')
plt.show()

# Criar a fronteira eficiente com restrições de vendas à descoberto (pesos >= 0)
ef_with_constraints = EfficientFrontier(mu, S)
ef_with_constraints.add_constraint(lambda x: x >= 0)
tangency_portfolio_with_constraints = ef_with_constraints.max_sharpe(risk_free_rate=risk_free_rate)
cleaned_weights_with_constraints_tangency = ef_with_constraints.clean_weights()
print("\nCarteira de Tangência com restrições de vendas à descoberto:")
print(cleaned_weights_with_constraints_tangency)

# Plotar a fronteira eficiente com restrições de vendas à descoberto
plotting.plot_efficient_frontier(ef_with_constraints, show_assets=True)
plt.title('Fronteira Eficiente com Restrição de Vendas à Descoberto')
plt.xlabel('Volatilidade')
plt.ylabel('Retorno')
plt.show()

# Construir/plotar a fronteira eficiente com a existência do ativo livre de risco e sem restrições de vendas à descoberto
ef_risk_free_no_constraints = EfficientFrontier(mu, S, weight_bounds=(-1, 1))
ef_risk_free_no_constraints.max_sharpe(risk_free_rate=risk_free_rate)
plotting.plot_efficient_frontier(ef_risk_free_no_constraints, show_assets=True)
plt.title('Fronteira Eficiente com Ativo Livre de Risco e Sem Restrição de Vendas à Descoberto')
plt.xlabel('Volatilidade')
plt.ylabel('Retorno')
plt.show()

# Construir/plotar a fronteira eficiente com a existência do ativo livre de risco e com restrições de vendas à descoberto
ef_risk_free_with_constraints = EfficientFrontier(mu, S, weight_bounds=(0, 1))
ef_risk_free_with_constraints.max_sharpe(risk_free_rate=risk_free_rate)
plotting.plot_efficient_frontier(ef_risk_free_with_constraints, show_assets=True)
plt.title('Fronteira Eficiente com Ativo Livre de Risco e Com Restrição de Vendas à Descoberto')
plt.xlabel('Volatilidade')
plt.ylabel('Retorno')
plt.show()
