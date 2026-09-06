# Pipeline da revisão cienciométrica — federalismo fiscal dos entes subnacionais
# Uso: make ajuda

PY      ?= python3
export PYTHONPATH := src
CORPUS  ?= dados/processado/corpus.csv
BRUTOS  ?= dados/processado/corpus-bruto.csv
ENTRADA ?= dados/bruto
SAIDA   ?= saidas
SEED    ?= 42

.PHONY: ajuda importar dedup triagem kappa indicadores redes prisma relatorio analise exemplo teste limpar

ajuda:
	@echo "Alvos disponíveis:"
	@echo "  make importar     lê $(ENTRADA) e monta o corpus"
	@echo "  make dedup        deduplica (guarda cópia bruta para o PRISMA)"
	@echo "  make triagem      gera a planilha cega de triagem"
	@echo "  make kappa        concordância entre revisores (TRIAGEM=arquivo.csv)"
	@echo "  make indicadores  produção, Lotka, Bradford, Price, impacto, colaboração"
	@echo "  make redes        co-citação, acoplamento, coautoria, co-palavras, mapa temático"
	@echo "  make prisma       contagens e diagrama do fluxo PRISMA"
	@echo "  make relatorio    monta saidas/relatorio.md"
	@echo "  make analise      importar -> dedup -> indicadores -> redes -> prisma -> relatorio"
	@echo "  make exemplo      roda tudo sobre a amostra SINTÉTICA (dados/exemplo)"
	@echo "  make teste        executa os testes"
	@echo "  make limpar       apaga saídas e dados processados"

importar:
	$(PY) -m cienciometria importar --entrada $(ENTRADA) --saida $(CORPUS)
	@cp $(CORPUS) $(BRUTOS)

dedup:
	$(PY) -m cienciometria dedup --corpus $(CORPUS)

triagem:
	$(PY) -m cienciometria triagem --corpus $(CORPUS) --saida modelos/triagem.csv

kappa:
	$(PY) -m cienciometria kappa --triagem $(or $(TRIAGEM),dados/processado/triagem-preenchida.csv)

indicadores:
	$(PY) -m cienciometria indicadores --corpus $(CORPUS) --saida $(SAIDA) --seed $(SEED)

redes:
	$(PY) -m cienciometria redes --corpus $(CORPUS) --saida $(SAIDA) --seed $(SEED)

prisma:
	$(PY) -m cienciometria prisma --corpus $(CORPUS) --brutos $(BRUTOS) --saida $(SAIDA)

relatorio:
	$(PY) -m cienciometria relatorio --saida $(SAIDA)

analise: importar dedup indicadores redes prisma relatorio
	@echo "Relatório em $(SAIDA)/relatorio.md"

exemplo:
	$(PY) testes/gerar_exemplo.py
	$(MAKE) analise ENTRADA=dados/exemplo CORPUS=dados/processado/corpus-exemplo.csv \
		BRUTOS=dados/processado/corpus-bruto-exemplo.csv SAIDA=saidas/exemplo
	@echo
	@echo "AVISO: saidas/exemplo vem de dados SINTÉTICOS. Não é resultado de pesquisa."

teste:
	$(PY) -m unittest discover -s testes -v

limpar:
	rm -rf saidas/* dados/processado/*
	@echo "saídas e dados processados removidos (dados/bruto e dados/exemplo preservados)"
